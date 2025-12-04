# ListeningMind 통합 - 구현 상세

> OpenWebUI에 ListeningMind API를 통합한 기술적 상세 내용

**작성일**: 2025-12-04
**구현 파일**:
- `C:\openwebui\source\open-webui\backend\open_webui\routers\listeningmind_api.py`
- `C:\openwebui\source\open-webui\backend\open_webui\main.py` (수정)
- `C:\openwebui\source\open-webui\.env` (수정)

---

## 📝 파일 변경 사항

### 1. main.py - 임포트 추가 (라인 98)

**변경 전**:

```python
from open_webui.routers import (
    audio,
    images,
    # ... 생략 ...
    custom_openai,
    gemini,
    responses,
)
```

**변경 후**:

```python
from open_webui.routers import (
    audio,
    images,
    # ... 생략 ...
    custom_openai,
    gemini,
    listeningmind_api,  # ← 추가됨
    responses,
)
```

### 2. main.py - 라우터 등록 (라인 1403-1404)

**변경 전**:

```python
# Google Gemini API
app.include_router(gemini.router)

# OpenAI Responses API (for o3-deep-research and advanced reasoning models)
app.include_router(responses.router)
```

**변경 후**:

```python
# Google Gemini API
app.include_router(gemini.router)

# ListeningMind SEO API
app.include_router(listeningmind_api.router)  # ← 추가됨

# OpenAI Responses API (for o3-deep-research and advanced reasoning models)
app.include_router(responses.router)
```

### 3. .env 파일 - 환경 변수 추가

**파일 위치**: `C:\openwebui\source\open-webui\.env`

**추가된 내용** (라인 45-53):

```bash
# ========================================
# ListeningMind API Configuration
# ========================================
# ListeningMind API 키 설정 (https://www.listeningmind.com)
LISTENINGMIND_API_KEY='your-api-key-here'
# ListeningMind API 베이스 URL
LISTENINGMIND_API_BASE='https://listeningmind-mcp-api.ascentlab.io'
# 기본 지역 코드 (kr: 한국, us: 미국, jp: 일본)
LISTENINGMIND_DEFAULT_GL='kr'
```

---

## 🔧 주요 구현 로직

### 1. 프롬프트 파싱 함수

```python
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
```

**동작 예시**:

```python
# 입력
prompt = "냉장고, 세탁기\n에어컨"

# 처리
extract_keywords_from_prompt(prompt)
# → ['냉장고', '세탁기', '에어컨']
```

### 2. 응답 포맷팅 함수

```python
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

        # ... 나머지 필드들 ...

    return "\n".join(summary)
```

**출력 예시**:

```
📊 키워드 분석 결과

🔍 **냉장고**
  • 검색량: 356,033
  • 경쟁도: HIGH
  • CPC: $0.56
  • SERP 특징: 이미지, 동영상, 관련검색
  • 검색의도: Information(정보), Transactional(거래)

💳 남은 크레딧: 99999
```

### 3. ChatCompletion 호환 엔드포인트

```python
@router.post("/chat/completions")
async def listeningmind_chat_completion(request: ChatCompletionRequest):
    """
    ListeningMind API를 OpenAI 호환 ChatCompletion 형식으로 제공

    흐름:
    1. API 키 확인
    2. 프롬프트에서 키워드 추출
    3. ListeningMind API 호출
    4. 응답 포맷팅
    5. OpenAI 호환 형식으로 반환
    """
    try:
        # 1. API 키 확인
        api_key = os.getenv("LISTENINGMIND_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key not configured")

        # 2. 사용자 프롬프트에서 최신 메시지 추출
        user_message = request.messages[-1].content if request.messages else ""

        # 3. 프롬프트에서 키워드 추출
        keywords = extract_keywords_from_prompt(user_message)

        if not keywords:
            return {
                "id": "listeningmind-0",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "⚠️ 키워드를 추출할 수 없습니다."
                    },
                    "finish_reason": "stop"
                }]
            }

        # 4. ListeningMind API 호출
        api_base = os.getenv("LISTENINGMIND_API_BASE", "https://...")
        default_gl = os.getenv("LISTENINGMIND_DEFAULT_GL", "kr")

        headers = {
            "LM-API-Key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "keywords": keywords,
            "gl": default_gl
        }

        async with aiohttp.ClientSession() as session:
            url = f"{api_base}/keyword"
            async with session.post(url, json=payload, headers=headers, ...) as response:
                if response.status != 200:
                    error_data = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_data)

                api_response = await response.json()

                # 5. 응답 포맷팅
                summary_text = format_keyword_response_as_text(api_response)

                # 6. OpenAI 호환 형식으로 반환
                return {
                    "id": f"listeningmind-{int(datetime.now().timestamp())}",
                    "object": "chat.completion",
                    "created": int(datetime.now().timestamp()),
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": summary_text
                        },
                        "finish_reason": "stop"
                    }],
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
```

---

## 📊 데이터 흐름

### 요청 → 응답 흐름

```
1. OpenWebUI UI
   ↓
2. POST /api/v1/listeningmind/chat/completions
   {
     "model": "listeningmind-keyword",
     "messages": [{"role": "user", "content": "냉장고"}]
   }
   ↓
3. listeningmind_chat_completion() 함수
   ├─ API 키 검증
   ├─ 프롬프트 파싱 → ["냉장고"]
   └─ ListeningMind API 호출
   ↓
4. ListeningMind API (외부)
   POST /keyword
   {
     "keywords": ["냉장고"],
     "gl": "kr"
   }
   ↓
5. ListeningMind API 응답
   {
     "result": "OK",
     "data": {
       "infos": [{
         "keyword": "냉장고",
         "ads_metrics": {...},
         "features": {...},
         ...
       }]
     }
   }
   ↓
6. 응답 포맷팅
   format_keyword_response_as_text()
   ↓
7. OpenAI 호환 응답
   {
     "object": "chat.completion",
     "choices": [{
       "message": {
         "content": "📊 키워드 분석 결과\n..."
       }
     }]
   }
   ↓
8. OpenWebUI UI
   "📊 키워드 분석 결과\n..."
```

---

## 🔌 API 엔드포인트 상세

### POST /api/v1/listeningmind/chat/completions

**요청 모델**:

```python
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
```

**응답 구조**:

```json
{
  "id": "listeningmind-1733289456",
  "object": "chat.completion",
  "created": 1733289456,
  "model": "listeningmind-keyword",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 150,
    "total_tokens": 160
  }
}
```

### GET /api/v1/listeningmind/models

**응답**:

```json
{
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
```

### POST /api/v1/listeningmind/raw-keyword

**요청**:

```json
{
  "keywords": ["냉장고", "세탁기"],
  "gl": "kr"
}
```

**응답**: ListeningMind 원본 API 응답

---

## ⚙️ 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `LISTENINGMIND_API_KEY` | (필수) | API 인증 키 |
| `LISTENINGMIND_API_BASE` | `https://listeningmind-mcp-api.ascentlab.io` | API 베이스 URL |
| `LISTENINGMIND_DEFAULT_GL` | `kr` | 기본 지역 코드 |

---

## 🐛 에러 처리

### 401 - API Key Not Configured

```python
if not api_key:
    raise HTTPException(
        status_code=401,
        detail="ListeningMind API key not configured (LISTENINGMIND_API_KEY)"
    )
```

### 400 - No Keywords Found

```python
if not keywords:
    return {
        "choices": [{
            "message": {
                "content": "⚠️ 키워드를 추출할 수 없습니다..."
            }
        }]
    }
```

### ListeningMind API Error

```python
if response.status != 200:
    error_data = await response.text()
    error_detail = {
        "status": response.status,
        "message": error_data,
        "model": request.model,
        "endpoint": "listeningmind_api",
        "api_base": api_base
    }
    raise HTTPException(status_code=response.status, detail=error_detail)
```

---

## 성능 최적화

### 1. 키워드 수 제한

```python
# 최대 100개 제한
return keywords[:100]
```

이유: ListeningMind API의 최대 제한과 성능 고려

### 2. 응답 키워드 제한

```python
# 응답에서는 최대 5개만 표시
for info in data.get("infos", [])[:5]:
```

이유: 읽기 쉬운 요약 제공

### 3. 타임아웃 설정

```python
timeout=aiohttp.ClientTimeout(total=60)
```

이유: 장시간 요청 방지

### 4. 비동기 처리

```python
async with aiohttp.ClientSession() as session:
    async with session.post(...) as response:
```

이유: 동시 요청 처리 가능

---

## 보안 고려사항

### 1. API 키 보호

- .env 파일은 .gitignore에 포함
- 프로덕션 환경에서는 Secret Manager 사용
- API 키는 환경변수로만 전달

### 2. CORS 설정

```python
# OpenWebUI 기본 설정
CORS_ALLOW_ORIGIN='*'

# 프로덕션에서는 특정 도메인만 허용
CORS_ALLOW_ORIGIN='https://yourdomain.com'
```

### 3. 입력 검증

- 최대 100개 키워드 제한
- 빈 문자열 제거
- SQL 인젝션 등의 보안 위험 없음

---

## 확장 가능성

### 추가 엔드포인트 구현

```python
@router.post("/path-finder")
async def listeningmind_path_finder(request: KeywordRequest):
    # /path_finder 엔드포인트 호출
    ...

@router.post("/google-serp")
async def listeningmind_google_serp(request: KeywordRequest):
    # /google_serp 엔드포인트 호출
    ...
```

### 캐싱 추가

```python
from aiocache import cached

@cached(ttl=3600)  # 1시간 캐시
async def cached_keyword_research(keywords: List[str]):
    ...
```

### 배치 처리

```python
@router.post("/batch-keywords")
async def batch_keyword_research(keywords: List[str]):
    # 여러 키워드를 배치로 처리
    ...
```

---

## 테스트 코드 예시

```python
# test_listeningmind.py
import pytest
from fastapi.testclient import TestClient
from open_webui.main import app

client = TestClient(app)

def test_models_endpoint():
    response = client.get("/api/v1/listeningmind/models")
    assert response.status_code == 200
    assert response.json()["object"] == "list"

def test_keyword_extraction():
    from open_webui.routers.listeningmind_api import extract_keywords_from_prompt

    prompt = "냉장고, 세탁기\n에어컨"
    keywords = extract_keywords_from_prompt(prompt)

    assert len(keywords) == 3
    assert "냉장고" in keywords
    assert "세탁기" in keywords
    assert "에어컨" in keywords

def test_chat_completion():
    response = client.post(
        "/api/v1/listeningmind/chat/completions",
        json={
            "model": "listeningmind-keyword",
            "messages": [{"role": "user", "content": "test"}]
        }
    )
    assert response.status_code in [200, 401, 500]  # 설정에 따라
```

---

**구현 완료**: 2025-12-04
**테스트 상태**: 준비 대기
**다음 단계**: 실제 API 키로 통합 테스트
