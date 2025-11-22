# API 수정 테스트 가이드

**작성**: 2025-11-22
**대상**: Gemini API & Custom OpenAI API 구조 수정 결과 테스트

---

## 실행된 수정사항

### Gemini API (`gemini.py`)

#### 추가된 요청 필드
```python
class GeminiRequest(BaseModel):
    model: str                              # 필수
    messages: List[Message]                 # 필수
    temperature: Optional[float] = 0.7      # 기본값: 0.7
    max_output_tokens: Optional[int] = None # 선택
    stream: Optional[bool] = False          # 선택

    # 새로 추가됨!
    top_p: Optional[float] = None           # nucleus sampling
    top_k: Optional[int] = None             # top-k sampling
    system_prompt: Optional[str] = None     # 시스템 프롬프트
```

#### 변경된 Payload 생성 로직
```python
# 1. generationConfig에 topP, topK 동적 추가
generation_config = {
    "temperature": request.temperature,
    "maxOutputTokens": request.max_output_tokens or 2048,
}
if request.top_p is not None:
    generation_config["topP"] = request.top_p
if request.top_k is not None:
    generation_config["topK"] = request.top_k

# 2. systemInstruction 지원
if request.system_prompt:
    payload["systemInstruction"] = {
        "parts": [{"text": request.system_prompt}]
    }
```

#### 개선된 에러 처리
```python
# 상세한 에러 정보 반환
error_detail = {
    "status": response.status,
    "message": error_data,
    "model": request.model,
    "endpoint": "gemini"
}
```

---

### Custom OpenAI API (`custom_openai.py`)

#### 추가된 요청 필드
```python
class ChatCompletionRequest(BaseModel):
    model: str                              # 필수
    messages: List[Message]                 # 필수
    temperature: Optional[float] = 0.7      # 기본값: 0.7
    max_tokens: Optional[int] = None        # 선택
    stream: Optional[bool] = False          # 선택

    # 새로 추가됨!
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
```

#### 개선된 Payload 생성 (선택적 필드만 포함)
```python
# None인 필드는 제외하고 전송
payload = {
    "model": request.model,
    "messages": [...]
}

# 선택적 필드는 값이 있을 때만 추가
if request.temperature is not None:
    payload["temperature"] = request.temperature
if request.top_p is not None:
    payload["top_p"] = request.top_p
# ... 기타 필드들
```

---

## 테스트 예시

### 1. Gemini API - 시스템 프롬프트 사용

**테스트 1-1: 기본 요청 (기존)**
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [
      {"role": "user", "content": "안녕하세요"}
    ]
  }'
```

**응답:**
```json
{
  "id": "gemini-response",
  "object": "chat.completion",
  "model": "gemini-3-pro",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "[Test Mode] Gemini response to: 안녕하세요"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "candidates_tokens": 20,
    "total_tokens": 30
  }
}
```

---

**테스트 1-2: 시스템 프롬프트 추가 (NEW!)**
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [
      {"role": "user", "content": "2+2는?"}
    ],
    "system_prompt": "You are a helpful math tutor. Always explain your answers step by step.",
    "temperature": 0.2,
    "max_output_tokens": 512
  }'
```

**설명:**
- `system_prompt`: Gemini API의 `systemInstruction` 필드로 변환됨
- `temperature`: 더 낮은 값(0.2)으로 더 일관된 답변
- 모델이 시스템 프롬프트를 고려하여 더 구조화된 답변 제공

---

**테스트 1-3: top_p와 top_k 활용 (NEW!)**
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-1.5-pro",
    "messages": [
      {"role": "user", "content": "창의적인 이야기를 지어줘"}
    ],
    "temperature": 0.8,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024
  }'
```

**설명:**
- `top_p`: 0.9 = 누적 확률 90% 범위의 토큰 중 선택 (더 다양함)
- `top_k`: 40 = 확률 상위 40개 토큰 중 선택
- 함께 사용하면 창의성과 일관성 사이 균형

---

### 2. Custom OpenAI API - 확장된 파라미터

**테스트 2-1: 기본 요청 (기존)**
```bash
curl -X POST http://localhost:8001/api/v1/custom/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

---

**테스트 2-2: OpenAI 완전 호환 파라미터 (NEW!)**
```bash
curl -X POST http://localhost:8001/api/v1/custom/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "프로그래밍 팁 3개를 제시해줘"}
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.95,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.2,
    "stop": ["\\n\\n", "---"]
  }'
```

**설명:**
- `top_p`: 0.95 = nucleus sampling으로 다양성 조절
- `frequency_penalty`: 0.5 = 반복되는 단어 감소
- `presence_penalty`: 0.2 = 새로운 토픽 장려
- `stop`: 특정 시퀀스에서 생성 중단

---

**테스트 2-3: None 필드 제외 테스트 (NEW!)**

이제 None인 필드는 API에 전송되지 않습니다:
```bash
curl -X POST http://localhost:8001/api/v1/custom/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hi"}
    ],
    "temperature": 0.7
  }'
```

**생성되는 Payload:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [{"role": "user", "content": "Hi"}],
  "temperature": 0.7
}
```

max_tokens, top_p 등 None인 필드는 제외됨 (API 호환성 향상)

---

## 에러 처리 개선 테스트

### 3-1: Gemini API - 상세한 에러 응답 (NEW!)

**요청 (잘못된 API 키):**
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [{"role": "user", "content": "Hi"}],
    "top_p": "invalid"
  }'
```

**응답 (401 에러):**
```json
{
  "detail": "GOOGLE_API_KEY not configured"
}
```

---

### 3-2: Custom OpenAI API - 상세한 에러 응답 (NEW!)

**요청 (API 연결 실패):**
```bash
curl -X POST http://localhost:8001/api/v1/custom/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hi"}]
  }'
```

**응답 (401 에러):**
```json
{
  "detail": {
    "status": 401,
    "message": "Unauthorized",
    "model": "gpt-4",
    "endpoint": "custom",
    "api_base": "https://api.openai.com/v1"
  }
}
```

---

## Python 클라이언트로 테스트

### 예제 1: Gemini API 테스트
```python
import requests

url = "http://localhost:8001/api/v1/gemini/chat/completions"

# 시스템 프롬프트 포함 요청
payload = {
    "model": "gemini-3-pro",
    "messages": [
        {"role": "user", "content": "파이썬 리스트 컴프리헨션 설명해줘"}
    ],
    "system_prompt": "You are a Python programming expert. Explain concepts clearly with code examples.",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_output_tokens": 1024
}

response = requests.post(url, json=payload)
print(response.json())
```

### 예제 2: Custom OpenAI API 테스트
```python
import requests

url = "http://localhost:8001/api/v1/custom/chat/completions"

# 확장된 파라미터 사용
payload = {
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "최신 AI 기술 트렌드"}
    ],
    "temperature": 0.7,
    "max_tokens": 800,
    "top_p": 0.95,
    "frequency_penalty": 0.3,
    "presence_penalty": 0.1
}

response = requests.post(url, json=payload)
result = response.json()
print(result["choices"][0]["message"]["content"])
```

---

## 파라미터 설명서

### Gemini API 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| model | str | - | 모델명 (필수) |
| messages | List | - | 메시지 배열 (필수) |
| temperature | float | 0.7 | 응답의 무작위성 (0.0~2.0) |
| max_output_tokens | int | 2048 | 최대 생성 토큰 수 |
| top_p | float | None | Nucleus sampling 확률 (0.0~1.0) |
| top_k | int | None | Top-K sampling 토큰 개수 |
| system_prompt | str | None | 시스템 프롬프트/지시사항 |
| stream | bool | False | 스트리밍 응답 |

### Custom OpenAI API 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| model | str | - | 모델명 (필수) |
| messages | List | - | 메시지 배열 (필수) |
| temperature | float | 0.7 | 응답의 무작위성 (0.0~2.0) |
| max_tokens | int | None | 최대 생성 토큰 수 |
| top_p | float | None | Nucleus sampling (0.0~1.0) |
| top_k | int | None | Top-K sampling |
| frequency_penalty | float | None | 빈도 페널티 (-2.0~2.0) |
| presence_penalty | float | None | 존재 페널티 (-2.0~2.0) |
| stop | List[str] | None | 중지 시퀀스 |
| stream | bool | False | 스트리밍 응답 |

---

## 다음 구현 가능한 기능들

### Gemini API
- [ ] Streaming 응답 지원
- [ ] Safety Settings 추가
- [ ] Tools/Function calling 지원
- [ ] Response Format (JSON mode)

### Custom OpenAI API
- [ ] Streaming 응답 구현
- [ ] Tools/Function calling 지원
- [ ] Response Format 지원
- [ ] Vision API 지원

---

**마지막 업데이트**: 2025-11-22
