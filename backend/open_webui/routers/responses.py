"""
OpenAI Deep Research API Router
Handles o3-deep-research and other advanced reasoning models
These models return structured responses with reasoning steps
"""

import asyncio
import json
import logging
from typing import Optional
from datetime import datetime

import aiohttp
from fastapi import Depends, HTTPException, Request, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from open_webui.models.models import Models
from open_webui.env import (
    AIOHTTP_CLIENT_SESSION_SSL,
    AIOHTTP_CLIENT_TIMEOUT,
    ENABLE_FORWARD_USER_INFO_HEADERS,
    BYPASS_MODEL_ACCESS_CONTROL,
)
from open_webui.models.users import UserModel
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS
from open_webui.utils.auth import get_verified_user
from open_webui.utils.access_control import has_access
from urllib.parse import quote

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("OPENAI", "INFO"))

router = APIRouter()


# ==========================================
# Utility Functions
# ==========================================


def is_responses_model(model: str) -> bool:
    """
    Check if the model uses responses API (o3-deep-research, o3-pro, etc.)
    These models require special handling:
    - Must use /v1/responses endpoint
    - Not supported in /v1/chat/completions
    - Require 'input' and 'tools' parameters
    """
    if not model:
        return False
    model_lower = model.lower()

    # Models that require /v1/responses endpoint
    responses_models = [
        "o3-deep-research",
        "o4-deep-research",
        "o3-pro",  # New: o3-pro family
        "o4-mini-deep-research",
    ]

    return (
        "deep-research" in model_lower
        or "o3-pro" in model_lower
        or "o4-mini-deep-research" in model_lower
        or model_lower in responses_models
    )


async def get_headers_for_responses(
    request: Request,
    url: str,
    key: Optional[str] = None,
    metadata: Optional[dict] = None,
    user: Optional[UserModel] = None,
) -> dict:
    """
    Generate headers for responses API request
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}" if key else "",
    }

    if ENABLE_FORWARD_USER_INFO_HEADERS and user:
        headers.update(
            {
                "X-OpenWebUI-User-Name": quote(user.name, safe=" "),
                "X-OpenWebUI-User-Id": user.id,
                "X-OpenWebUI-User-Email": user.email,
                "X-OpenWebUI-User-Role": user.role,
            }
        )

    if metadata and metadata.get("chat_id"):
        headers["X-OpenWebUI-Chat-Id"] = metadata.get("chat_id")

    return headers


def convert_chat_completions_to_responses(payload: dict) -> dict:
    """
    Convert chat/completions payload format to responses API payload format

    Responses API format expects:
    - input: The user's query (string)
    - tools: List of tools to use (e.g., [{"type": "web_search_preview"}])
    - max_completion_tokens: Maximum tokens (optional)
    - temperature, top_p, etc.: Standard parameters

    Chat/completions format has:
    - messages: Array of message objects
    """
    # Extract user message as input
    messages = payload.get("messages", [])
    input_text = ""

    # Get the last user message as the input
    for msg in reversed(messages):
        if msg.get("role") == "user":
            input_text = msg.get("content", "")
            break

    responses_payload = {
        "model": payload.get("model"),
        "input": input_text,
        # Default tool for deep research
        "tools": [{"type": "web_search_preview"}],
    }

    # Map optional parameters
    optional_fields = {
        "temperature": "temperature",
        "top_p": "top_p",
        "presence_penalty": "presence_penalty",
        "frequency_penalty": "frequency_penalty",
        "seed": "seed",
        "max_completion_tokens": "max_completion_tokens",
    }

    for chat_field, responses_field in optional_fields.items():
        if chat_field in payload:
            responses_payload[responses_field] = payload[chat_field]

    # Handle metadata if present
    if "metadata" in payload:
        responses_payload["metadata"] = payload["metadata"]

    log.debug(f"Converted to responses format: input={input_text[:100]}...")
    return responses_payload


def convert_responses_to_chat_completions(response_data: dict) -> dict:
    """
    Convert Responses API response format to chat/completions format
    for compatibility with OpenWebUI

    Responses API returns format like:
    {
        "id": "resp_...",
        "object": "response",
        "status": "completed",
        "result": {
            "output": "The research output text..."
        },
        "usage": {...}
    }

    We need to convert it to:
    {
        "choices": [{"message": {"content": "..."}}],
        "usage": {...}
    }
    """
    if not response_data:
        return {
            "error": {
                "message": "Empty response from OpenAI",
                "type": "invalid_response_error",
            }
        }

    # Handle error responses
    if "error" in response_data:
        return response_data

    # If already in chat.completion format, return as-is
    if response_data.get("object") == "chat.completion" and "choices" in response_data:
        return response_data

    # Convert from responses format to chat.completion format
    output_text = ""

    # Extract output from responses API format
    if "result" in response_data and "output" in response_data["result"]:
        output_text = response_data["result"]["output"]
    elif "output" in response_data:
        output_text = response_data["output"]
    elif "content" in response_data:
        output_text = response_data["content"]

    # Build chat.completion format response
    completion_response = {
        "id": response_data.get("id", ""),
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": response_data.get("model", ""),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": response_data.get("usage", {}),
    }

    log.debug(
        f"Converted responses API response: output length={len(output_text)}"
    )
    return completion_response


# ==========================================
# API Endpoints
# ==========================================


@router.post("/v1/responses")
async def create_response(
    request: Request,
    form_data: dict,
    user=Depends(get_verified_user),
    bypass_filter: Optional[bool] = False,
):
    """
    Create a response using OpenAI's responses API (for o3-deep-research)
    This endpoint handles models that require the /v1/responses endpoint
    instead of /v1/chat/completions
    """

    if BYPASS_MODEL_ACCESS_CONTROL:
        bypass_filter = True

    payload = {**form_data}
    metadata = payload.pop("metadata", None)

    model_id = form_data.get("model")

    # Validate model is a responses model
    if not is_responses_model(model_id):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_id}' does not support responses API endpoint",
        )

    # Check if model exists in OpenWebUI
    model_info = Models.get_model_by_id(model_id)

    if model_info:
        if model_info.base_model_id:
            payload["model"] = model_info.base_model_id
            model_id = model_info.base_model_id

        # Check if user has access
        if not bypass_filter and user.role == "user":
            if not (
                user.id == model_info.user_id
                or has_access(
                    user.id, type="read", access_control=model_info.access_control
                )
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Model not found",
                )
    elif not bypass_filter:
        if user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Model not found",
            )

    # Get OpenAI API configuration
    # For responses API, we use the same OPENAI_API_CONFIGS
    url = None
    key = None

    # Try to get config from request app state (same as openai.py)
    try:
        if hasattr(request.app.state, "config"):
            config = request.app.state.config
            if hasattr(config, "OPENAI_API_BASE_URLS") and config.OPENAI_API_BASE_URLS:
                url = config.OPENAI_API_BASE_URLS[0]
                key = config.OPENAI_API_KEYS[0] if config.OPENAI_API_KEYS else None
    except (AttributeError, IndexError) as e:
        log.warning(f"Failed to get OpenAI config from request: {e}")

    if not url or not key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API configuration not found. Please configure OpenAI API keys in settings.",
        )

    # Convert from chat/completions format to responses format
    try:
        if "messages" in payload and isinstance(payload["messages"], list):
            responses_payload = convert_chat_completions_to_responses(payload)
        else:
            log.warning(
                f"Payload doesn't have 'messages' key or it's not a list. Keys: {list(payload.keys())}"
            )
            responses_payload = payload
    except Exception as e:
        log.error(f"Error converting payload to responses format: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process request: {str(e)}",
        )

    # Remove unsupported parameters for responses API
    # (responses API uses 'input' not 'messages', so no message role conversion needed)
    # NOTE: 'tools' is REQUIRED and already added by convert_chat_completions_to_responses()
    unsupported_params = [
        "max_tokens",
        "top_k",
        "logit_bias",
        "response_format",
        "tool_choice",  # Removed 'tools' - it's required for deep research!
        "logprobs",
        "top_logprobs",
        "messages",  # Remove chat completions specific field
        "stream",  # Remove streaming parameter
    ]

    for param in unsupported_params:
        responses_payload.pop(param, None)

    # Prepare the request
    # Deep Research models MUST use /v1/responses endpoint (NOT /v1/chat/completions)
    # Remove trailing slash and /v1 if it already exists to avoid duplication

    base_url = url.rstrip('/')
    if base_url.endswith('/v1'):
        # URL already has /v1, just add /responses
        response_url = f"{base_url}/responses"
    else:
        # URL doesn't have /v1, add both
        response_url = f"{base_url}/v1/responses"

    log.info(
        f"Using Responses API endpoint: {response_url} for model {responses_payload.get('model')}"
    )
    log.debug(
        f"URL construction: original_url={url} -> base_url={base_url} -> response_url={response_url}"
    )

    headers = await get_headers_for_responses(request, url, key, metadata, user)
    payload_json = json.dumps(responses_payload)

    session = None
    try:
        session = aiohttp.ClientSession(
            trust_env=True, timeout=aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT)
        )

        log.info(
            f"Sending request to {response_url} for model {responses_payload.get('model')}"
        )
        log.debug(f"Request headers: {headers}")
        log.debug(f"Request payload keys: {list(responses_payload.keys())}")
        log.debug(f"Tools in payload: {responses_payload.get('tools')}")
        log.debug(f"Full payload: {payload_json[:500]}...")  # Log first 500 chars

        r = await session.request(
            method="POST",
            url=response_url,
            data=payload_json,
            headers=headers,
            ssl=AIOHTTP_CLIENT_SESSION_SSL,
        )

        response_text = await r.text()

        if r.status != 200:
            log.error(
                f"OpenAI API error: status={r.status}, url={response_url}, response={response_text[:500]}"
            )
            try:
                error_data = json.loads(response_text)
                return JSONResponse(
                    status_code=r.status,
                    content=error_data,
                )
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=r.status,
                    content={
                        "error": {
                            "message": response_text,
                            "type": "api_error",
                        }
                    },
                )

        # Parse the response
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            log.error(f"Failed to parse response: {response_text}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "Invalid response from OpenAI API",
                        "type": "invalid_response_error",
                    }
                },
            )

        # Convert responses format to chat/completions format for compatibility
        chat_completion_response = convert_responses_to_chat_completions(response_data)

        return JSONResponse(
            status_code=200,
            content=chat_completion_response,
        )

    except asyncio.TimeoutError:
        log.error("Request timeout to OpenAI API")
        return JSONResponse(
            status_code=504,
            content={
                "error": {
                    "message": "Request timeout",
                    "type": "timeout_error",
                }
            },
        )
    except aiohttp.ClientError as e:
        log.error(f"Client error: {e}")
        return JSONResponse(
            status_code=502,
            content={
                "error": {
                    "message": str(e),
                    "type": "client_error",
                }
            },
        )
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "Internal server error",
                    "type": "internal_error",
                }
            },
        )
    finally:
        if session:
            await session.close()


@router.get("/v1/responses/models")
async def get_responses_models(
    request: Request,
    user=Depends(get_verified_user),
):
    """
    Get list of available responses models
    """
    responses_models = [
        {
            "id": "o3-deep-research",
            "object": "model",
            "owned_by": "openai",
            "description": "Deep research model using responses API",
            "supports_responses_api": True,
        },
        {
            "id": "o4-deep-research",
            "object": "model",
            "owned_by": "openai",
            "description": "Advanced deep research model using responses API (future)",
            "supports_responses_api": True,
        },
    ]

    return JSONResponse(
        status_code=200,
        content={
            "object": "list",
            "data": responses_models,
        },
    )
