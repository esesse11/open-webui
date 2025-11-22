"""
Custom OpenAI Compatible API Router
Supports: Groq, LMStudio, NanoBanana2, and other OpenAI-compatible services
"""

import os
import logging
import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/custom", tags=["custom"])

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None

@router.post("/chat/completions")
async def custom_chat_completion(request: ChatCompletionRequest):
    """
    OpenAI Compatible API endpoint (No authentication required)
    Supports Groq, LMStudio, and other compatible services
    """
    try:
        if not request.model:
            raise HTTPException(status_code=400, detail="Model is required")

        api_base = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise HTTPException(status_code=401, detail="API key not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Build payload with base parameters
        payload = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        }

        # Add optional parameters only if provided (not None)
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.stream is not None:
            payload["stream"] = request.stream
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.top_k is not None:
            payload["top_k"] = request.top_k
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            payload["stop"] = request.stop

        async with aiohttp.ClientSession() as session:
            url = f"{api_base}/chat/completions"
            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_data = await response.text()
                    error_detail = {
                        "status": response.status,
                        "message": error_data,
                        "model": request.model,
                        "endpoint": "custom",
                        "api_base": api_base
                    }
                    logger.error(f"Custom API error [{response.status}]: {error_data}")
                    raise HTTPException(status_code=response.status, detail=error_detail)

                return await response.json()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def custom_list_models():
    """List available models (supports test mode)"""
    try:
        api_base = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise HTTPException(status_code=401, detail="API key not configured")

        # Test mode - return mock data if key is 'test-*'
        if api_key.startswith("sk-test"):
            return {
                "object": "list",
                "data": [
                    {"id": "gpt-4", "object": "model", "owned_by": "openai"},
                    {"id": "gpt-3.5-turbo", "object": "model", "owned_by": "openai"},
                    {"id": "text-davinci-003", "object": "model", "owned_by": "openai"},
                    {"id": "nano-banana-2", "object": "model", "owned_by": "google", "description": "NanoBanana 2 - High-quality image generation with Gemini 3 Pro backend"}
                ]
            }

        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{api_base}/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status)
                return await response.json()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
