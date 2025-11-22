# 🔧 API 입출력 구조 수정 가이드

**작성**: 2025-11-22
**대상**: Gemini API & Custom OpenAI API 라우터

---

## 📊 현재 구조 분석

### 1️⃣ Gemini API (`gemini.py`)

#### 요청 구조 (INPUT)
```python
# Pydantic 모델 정의
class GeminiRequest(BaseModel):
    model: str                              # 모델명 (필수)
    messages: List[Message]                 # 메시지 배열 (필수)
    temperature: Optional[float] = 0.7      # 온도 설정 (선택, 기본값: 0.7)
    max_output_tokens: Optional[int] = None # 최대 토큰 (선택)
    stream: Optional[bool] = False          # 스트리밍 (선택)

class Message(BaseModel):
    role: str      # "user", "assistant" 등
    content: str   # 메시지 내용
```

**요청 예시**:
```json
POST /api/v1/gemini/chat/completions
{
  "model": "gemini-3-pro",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_output_tokens": 1024,
  "stream": false
}
```

#### 응답 구조 (OUTPUT)
```json
{
  "id": "gemini-response",
  "object": "chat.completion",
  "model": "gemini-3-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "응답 내용"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

#### 내부 변환 로직
```python
OpenAI 형식 → Gemini 형식
messages: [
  {"role": "user", "content": "..."}
]
       ↓ (라인 65-70)
contents: [
  {"role": "user", "parts": [{"text": "..."}]}
]

API 요청 페이로드 (라인 72-78):
{
  "contents": [...],           # 변환된 메시지
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 2048
  }
}
```

---

### 2️⃣ Custom OpenAI API (`custom_openai.py`)

#### 요청 구조 (INPUT)
```python
class ChatCompletionRequest(BaseModel):
    model: str                      # 모델명 (필수)
    messages: List[Message]         # 메시지 배열 (필수)
    temperature: Optional[float] = 0.7  # 온도 (선택)
    max_tokens: Optional[int] = None    # 최대 토큰 (선택)
    stream: Optional[bool] = False      # 스트리밍 (선택)

class Message(BaseModel):
    role: str      # "user", "assistant" 등
    content: str   # 메시지 내용
```

**요청 예시**:
```json
POST /api/v1/custom/chat/completions
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.8,
  "max_tokens": 2048
}
```

#### 응답 구조 (OUTPUT)
```
OpenAI API와 동일한 형식으로 그대로 반환
(라인 68: return await response.json())
```

---

## 🔨 수정 가능한 부분들

### Gemini API 수정 가능 항목

#### 1️⃣ 요청 필드 추가/수정 (라인 23-28)
```python
# 현재
class GeminiRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_output_tokens: Optional[int] = None
    stream: Optional[bool] = False

# 수정 가능
class GeminiRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_output_tokens: Optional[int] = None
    stream: Optional[bool] = False

    # 추가 필드 예시
    top_p: Optional[float] = None                    # nucleus sampling
    top_k: Optional[int] = None                      # top-k sampling
    presence_penalty: Optional[float] = None         # 반복 줄이기
    frequency_penalty: Optional[float] = None        # 빈도 페널티
    system_prompt: Optional[str] = None              # 시스템 프롬프트
    response_format: Optional[str] = None            # 응답 형식 (json, text)
```

#### 2️⃣ Gemini API로 보내는 Payload 수정 (라인 72-78)
```python
# 현재
payload = {
    "contents": contents,
    "generationConfig": {
        "temperature": request.temperature,
        "maxOutputTokens": request.max_output_tokens or 2048,
    }
}

# 수정 가능
payload = {
    "contents": contents,
    "generationConfig": {
        "temperature": request.temperature,
        "maxOutputTokens": request.max_output_tokens or 2048,
        "topP": request.top_p,                    # 추가 파라미터
        "topK": request.top_k,
        "candidateCount": 1,
    },
    "safetySettings": [                           # 안전성 필터
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        }
    ],
    "systemInstruction": {                        # 시스템 프롬프트
        "parts": [{"text": request.system_prompt}]
    } if request.system_prompt else None
}
```

#### 3️⃣ 응답 형식 수정 (라인 108-121)
```python
# 현재
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

# 수정 가능 - 더 많은 정보 포함
return {
    "id": data.get("name", "gemini-response"),    # Google API의 ID 사용
    "object": "chat.completion",
    "created": int(time.time()),                  # 생성 시간 추가
    "model": request.model,
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": response_text
        },
        "finish_reason": finish_reason,           # "stop", "length" 등
        "logprobs": None,                         # 로그 확률 (필요시)
    }],
    "usage": {
        "prompt_tokens": data.get("usageMetadata", {}).get("promptTokenCount", 0),
        "completion_tokens": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
        "total_tokens": data.get("usageMetadata", {}).get("totalTokenCount", 0),
    }
}
```

#### 4️⃣ 타임아웃 수정 (라인 89)
```python
# 현재
timeout=aiohttp.ClientTimeout(total=60)

# 수정 가능
timeout=aiohttp.ClientTimeout(
    total=120,           # 전체 타임아웃 (초)
    connect=10,          # 연결 타임아웃
    sock_connect=10,     # 소켓 연결
    sock_read=60         # 읽기 타임아웃
)
```

#### 5️⃣ 에러 처리 개선 (라인 91-95)
```python
# 현재
if response.status != 200:
    error_data = await response.text()
    logger.error(f"Gemini API error: {error_data}")
    raise HTTPException(status_code=response.status, detail=error_data)

# 수정 가능
if response.status != 200:
    error_data = await response.text()
    logger.error(f"Gemini API error [{response.status}]: {error_data}")

    # 상세한 에러 메시지
    error_detail = {
        "status": response.status,
        "message": error_data,
        "timestamp": datetime.now().isoformat(),
        "endpoint": request.model
    }

    raise HTTPException(
        status_code=response.status,
        detail=error_detail
    )
```

---

### Custom OpenAI API 수정 가능 항목

#### 1️⃣ 요청 필드 추가 (라인 20-25)
```python
# 현재
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

# 수정 가능 - OpenAI와 동일하게
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]

    # 기존
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

    # 추가 파라미터
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1                          # 몇 개 응답?
    stop: Optional[List[str]] = None              # 중지 시퀀스
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[dict] = None
    user: Optional[str] = None                    # 사용자 ID
    response_format: Optional[str] = None         # "json_object" 등
    tools: Optional[List[dict]] = None            # Function calling
    tool_choice: Optional[str] = None
```

#### 2️⃣ Payload 구성 수정 (라인 48-54)
```python
# 현재
payload = {
    "model": request.model,
    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
    "temperature": request.temperature,
    "max_tokens": request.max_tokens,
    "stream": request.stream
}

# 수정 가능 - None 값 제외
payload = {
    "model": request.model,
    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
}

# 선택적 파라미터 추가
if request.temperature is not None:
    payload["temperature"] = request.temperature
if request.max_tokens is not None:
    payload["max_tokens"] = request.max_tokens
if request.stream is not None:
    payload["stream"] = request.stream
if request.top_p is not None:
    payload["top_p"] = request.top_p
if request.stop:
    payload["stop"] = request.stop
if request.tools:
    payload["tools"] = request.tools
```

#### 3️⃣ API Base URL 환경 변수 사용 (라인 37)
```python
# 현재
api_base = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")

# 수정 가능 - 여러 API 지원
API_PROVIDERS = {
    "openai": os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1"),
    "groq": os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1"),
    "anthropic": os.getenv("ANTHROPIC_API_BASE_URL"),
    "custom": os.getenv("CUSTOM_API_BASE_URL"),
}

# 요청에서 provider 선택
@router.post("/chat/completions")
async def custom_chat_completion(
    request: ChatCompletionRequest,
    provider: Optional[str] = Query("openai")  # 쿼리 파라미터
):
    api_base = API_PROVIDERS.get(provider)
```

#### 4️⃣ 스트리밍 응답 구현 (라인 56-68)
```python
# 현재 - 스트리밍 미지원
async with session.post(...) as response:
    return await response.json()

# 스트리밍 지원 추가
if request.stream:
    async def stream_generator():
        async with session.post(...) as response:
            async for line in response.content:
                if line:
                    yield line + b"\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
else:
    async with session.post(...) as response:
        return await response.json()
```

---

## 📋 수정 체크리스트

### Gemini API 수정 시
- [ ] 요청 파라미터 추가 (top_p, top_k, system_prompt 등)
- [ ] Payload generationConfig 확장
- [ ] Safety settings 추가
- [ ] 응답 필드 추가 (created, logprobs 등)
- [ ] 타임아웃 설정 커스터마이징
- [ ] 에러 처리 상세화
- [ ] 로깅 개선
- [ ] Streaming 지원 추가

### Custom OpenAI API 수정 시
- [ ] OpenAI 스펙에 맞는 모든 필드 추가
- [ ] Provider별 API 엔드포인트 관리
- [ ] None 값 처리 (불필요한 필드 제외)
- [ ] Streaming 응답 구현
- [ ] Function calling 지원
- [ ] 에러 응답 포맷 통일
- [ ] Request validation 강화

---

## 🔄 수정 예시

### 예시 1: Gemini에 시스템 프롬프트 추가

**Step 1**: `GeminiRequest` 모델 수정
```python
class GeminiRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_output_tokens: Optional[int] = None
    stream: Optional[bool] = False
    system_prompt: Optional[str] = None  # 추가
```

**Step 2**: Payload에 반영
```python
payload = {
    "contents": contents,
    "generationConfig": {...},
    "systemInstruction": {
        "parts": [{"text": request.system_prompt}]
    } if request.system_prompt else None
}

# None 값 제거
payload = {k: v for k, v in payload.items() if v is not None}
```

**Step 3**: 테스트
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [{"role": "user", "content": "Hi"}],
    "system_prompt": "You are a helpful assistant."
  }'
```

---

## 🎯 다음 구현 순서

1. **필수**: OpenAI 호환 필드 추가
2. **권장**: Streaming 지원
3. **선택**: Function calling 지원
4. **선택**: Safety settings 커스터마이징

---

**파일 위치**:
- `C:\openwebui\source\open-webui\backend\open_webui\routers\gemini.py`
- `C:\openwebui\source\open-webui\backend\open_webui\routers\custom_openai.py`

---

**작성**: 2025-11-22
