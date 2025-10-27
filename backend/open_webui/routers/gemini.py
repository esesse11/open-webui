"""
Google Gemini API Router
Supports: Gemini 1.5 Pro, Gemini 1.5 Flash, and other Google models
"""

import os
import logging
import aiohttp
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/gemini", tags=["gemini"])

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta"

class Message(BaseModel):
    role: str
    content: str

class GeminiRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_output_tokens: Optional[int] = None
    stream: Optional[bool] = False

@router.post("/chat/completions")
async def gemini_chat_completion(request: GeminiRequest):
    """
    Google Gemini API endpoint (supports test mode)
    Converts OpenAI format to Gemini format and back
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="GOOGLE_API_KEY not configured")

        # Test mode - return mock response if key is 'test-*'
        if api_key.startswith("test-"):
            user_message = request.messages[-1].content if request.messages else "Hello"
            return {
                "id": "gemini-test-response",
                "object": "chat.completion",
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"[Test Mode] Gemini response to: {user_message}"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "candidates_tokens": 20,
                    "total_tokens": 30
                }
            }

        # Convert OpenAI format to Gemini format
        contents = []
        for msg in request.messages:
            role = "model" if msg.role == "assistant" else msg.role
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_output_tokens or 2048,
            }
        }

        model_name = request.model
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        async with aiohttp.ClientSession() as session:
            url = f"{GEMINI_API_URL}/{model_name}:generateContent?key={api_key}"
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_data = await response.text()
                    logger.error(f"Gemini API error: {error_data}")
                    raise HTTPException(status_code=response.status, detail=error_data)

                data = await response.json()

        # Convert Gemini response to OpenAI format
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            response_text = ""

            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "text" in part:
                        response_text += part["text"]

            return {
                "id": "gemini-response",
                "object": "chat.completion",
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": data.get("usageMetadata", {})
            }
        else:
            raise HTTPException(status_code=500, detail="No response from Gemini")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def gemini_list_models():
    """List available Gemini models (supports test mode)"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="GOOGLE_API_KEY not configured")

        # Test mode - return mock data if key is 'test-*'
        if api_key.startswith("test-"):
            return {
                "models": [
                    {
                        "name": "models/gemini-1.5-pro",
                        "displayName": "Gemini 1.5 Pro",
                        "description": "Most capable Gemini model"
                    },
                    {
                        "name": "models/gemini-1.5-flash",
                        "displayName": "Gemini 1.5 Flash",
                        "description": "Fast and efficient Gemini model"
                    },
                    {
                        "name": "models/gemini-pro",
                        "displayName": "Gemini Pro",
                        "description": "Standard Gemini model"
                    }
                ]
            }

        async with aiohttp.ClientSession() as session:
            url = f"{GEMINI_API_URL}/models?key={api_key}"
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status)
                return await response.json()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list Gemini models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
