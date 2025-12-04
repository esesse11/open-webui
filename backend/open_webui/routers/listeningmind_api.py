"""
ListeningMind SEO API Router
Integrates ListeningMind API as a custom model for OpenWebUI
Supports keyword research, path finder, Google SERP, and Google Ads
"""

import os
import logging
import aiohttp
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/listeningmind", tags=["listeningmind"])


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class KeywordRequest(BaseModel):
    keywords: List[str]
    gl: str = "kr"


def extract_keywords_from_prompt(prompt: str) -> List[str]:
    """
    자동 파싱: 프롬프트에서 키워드 추출
    - 쉼표, 공백, 슬래시로 분리된 단어들을 키워드로 추출
    - 각 라인을 개별 키워드로 처리
    """
    keywords = []

    # 쉼표로 분리
    comma_split = [k.strip() for k in prompt.split(',')]
    keywords.extend([k for k in comma_split if k])

    # 개행으로 분리된 항목들
    lines = prompt.split('\n')
    for line in lines:
        line = line.strip()
        if line and line not in keywords:
            keywords.append(line)

    # 최대 100개 제한
    return keywords[:100]


def format_keyword_response_as_text(response_data: Dict[str, Any]) -> str:
    """
    API 응답을 읽기 좋은 요약 텍스트로 변환
    """
    if response_data.get("result") != "OK":
        return f"❌ 요청 실패: {response_data.get('reason', 'Unknown error')}"

    data = response_data.get("data")
    if not data or not data.get("infos"):
        return "⚠️ 검색 결과가 없습니다."

    summary = []
    summary.append("📊 키워드 분석 결과\n")

    for info in data.get("infos", [])[:5]:  # 최대 5개 키워드
        keyword = info.get("keyword", "Unknown")
        summary.append(f"\n🔍 **{keyword}**")

        # Ads 메트릭
        ads = info.get("ads_metrics", {})
        if ads:
            summary.append(f"  • 검색량: {ads.get('volume_avg', 'N/A'):,}")
            summary.append(f"  • 경쟁도: {ads.get('competition', 'N/A')}")
            summary.append(f"  • CPC: ${ads.get('cpc', 'N/A')}")

        # Features
        features = info.get("features", {})
        if features:
            feature_list = []
            if features.get("f_images"): feature_list.append("이미지")
            if features.get("f_video_results"): feature_list.append("동영상")
            if features.get("f_people_also_search_for"): feature_list.append("관련검색")
            if feature_list:
                summary.append(f"  • SERP 특징: {', '.join(feature_list)}")

        # Intent
        intents = info.get("intents", {})
        if intents:
            intent_list = []
            if intents.get("i"): intent_list.append("Information(정보)")
            if intents.get("n"): intent_list.append("Navigation(탐색)")
            if intents.get("c"): intent_list.append("Commercial(상업)")
            if intents.get("t"): intent_list.append("Transactional(거래)")
            if intent_list:
                summary.append(f"  • 검색의도: {', '.join(intent_list)}")

    # 크레딧 정보
    remain = response_data.get("remain_credits")
    if remain is not None:
        summary.append(f"\n💳 남은 크레딧: {remain:,}")

    return "\n".join(summary)


@router.post("/chat/completions")
async def listeningmind_chat_completion(request: ChatCompletionRequest):
    """
    ListeningMind API를 OpenAI 호환 ChatCompletion 형식으로 제공
    """
    try:
        # API 설정 확인
        api_key = os.getenv("LISTENINGMIND_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="ListeningMind API key not configured (LISTENINGMIND_API_KEY)"
            )

        # 기본 지역 설정
        default_gl = os.getenv("LISTENINGMIND_DEFAULT_GL", "kr")

        # 사용자 프롬프트에서 최신 메시지 추출
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        user_message = request.messages[-1].content if request.messages else ""

        # 프롬프트에서 키워드 자동 추출
        keywords = extract_keywords_from_prompt(user_message)

        if not keywords:
            return {
                "id": "listeningmind-0",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "⚠️ 키워드를 추출할 수 없습니다. 프롬프트에 분석할 키워드를 입력해주세요."
                        },
                        "finish_reason": "stop"
                    }
                ]
            }

        # ListeningMind API 호출
        api_base = os.getenv("LISTENINGMIND_API_BASE", "https://listeningmind-mcp-api.ascentlab.io")

        headers = {
            "LM-API-Key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "keywords": keywords,
            "gl": default_gl
        }

        logger.info(f"Calling ListeningMind API with keywords: {keywords}")

        async with aiohttp.ClientSession() as session:
            url = f"{api_base}/keyword"
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
                        "endpoint": "listeningmind_api",
                        "api_base": api_base
                    }
                    logger.error(f"ListeningMind API error [{response.status}]: {error_data}")
                    raise HTTPException(status_code=response.status, detail=error_detail)

                api_response = await response.json()

                # 응답을 요약 텍스트로 변환
                summary_text = format_keyword_response_as_text(api_response)

                # OpenAI 호환 형식으로 응답
                return {
                    "id": f"listeningmind-{int(datetime.now().timestamp())}",
                    "object": "chat.completion",
                    "created": int(datetime.now().timestamp()),
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": summary_text
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(user_message.split()),
                        "completion_tokens": len(summary_text.split()),
                        "total_tokens": len(user_message.split()) + len(summary_text.split())
                    }
                }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ListeningMind API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def listeningmind_list_models():
    """
    ListeningMind 모델 목록 반환
    """
    try:
        api_key = os.getenv("LISTENINGMIND_API_KEY")

        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="ListeningMind API key not configured"
            )

        # ListeningMind는 하나의 "모델"로 제공
        return {
            "object": "list",
            "data": [
                {
                    "id": "listeningmind-keyword",
                    "object": "model",
                    "owned_by": "listeningmind",
                    "description": "ListeningMind Keyword Research API - SEO 분석",
                    "permissions": []
                }
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/raw-keyword")
async def listeningmind_raw_keyword(request: KeywordRequest):
    """
    ListeningMind Keyword API를 직접 호출
    (고급 사용자용)
    """
    try:
        api_key = os.getenv("LISTENINGMIND_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key not configured")

        api_base = os.getenv("LISTENINGMIND_API_BASE", "https://listeningmind-mcp-api.ascentlab.io")

        headers = {
            "LM-API-Key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "keywords": request.keywords,
            "gl": request.gl
        }

        async with aiohttp.ClientSession() as session:
            url = f"{api_base}/keyword"
            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_data = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_data)

                return await response.json()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
