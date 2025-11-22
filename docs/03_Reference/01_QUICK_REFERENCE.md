# API 수정 - 빠른 참조 가이드

**최종 업데이트**: 2025-11-22

---

## 한눈에 보기

### Gemini API 새로운 파라미터

```json
{
  "model": "gemini-3-pro",
  "messages": [...],

  "temperature": 0.7,              // 기존
  "max_output_tokens": 2048,       // 기존
  "stream": false,                 // 기존

  "top_p": 0.9,                    // NEW: Nucleus sampling
  "top_k": 40,                     // NEW: Top-K sampling
  "system_prompt": "You are..."    // NEW: 시스템 프롬프트
}
```

### Custom OpenAI API 새로운 파라미터

```json
{
  "model": "gpt-4",
  "messages": [...],

  "temperature": 0.7,              // 기존
  "max_tokens": 2048,              // 기존
  "stream": false,                 // 기존

  "top_p": 0.95,                   // NEW
  "top_k": 40,                     // NEW
  "frequency_penalty": 0.5,        // NEW
  "presence_penalty": 0.2,         // NEW
  "stop": ["\\n\\n"]               // NEW: 중지 시퀀스
}
```

---

## 코드 변경 포인트

### Gemini API 변경사항

#### 변경 1: 요청 모델 (라인 23-31)
```diff
class GeminiRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_output_tokens: Optional[int] = None
    stream: Optional[bool] = False
+   top_p: Optional[float] = None
+   top_k: Optional[int] = None
+   system_prompt: Optional[str] = None
```

#### 변경 2: Payload 생성 (라인 75-96)
```diff
+ generation_config = {
+     "temperature": request.temperature,
+     "maxOutputTokens": request.max_output_tokens or 2048,
+ }
+ if request.top_p is not None:
+     generation_config["topP"] = request.top_p
+ if request.top_k is not None:
+     generation_config["topK"] = request.top_k

  payload = {
      "contents": contents,
-     "generationConfig": {
-         "temperature": request.temperature,
-         "maxOutputTokens": request.max_output_tokens or 2048,
-     }
+     "generationConfig": generation_config,
  }

+ if request.system_prompt:
+     payload["systemInstruction"] = {
+         "parts": [{"text": request.system_prompt}]
+     }
```

#### 변경 3: 에러 처리 (라인 109-118)
```diff
  if response.status != 200:
      error_data = await response.text()
+     error_detail = {
+         "status": response.status,
+         "message": error_data,
+         "model": request.model,
+         "endpoint": "gemini"
+     }
-     logger.error(f"Gemini API error: {error_data}")
+     logger.error(f"Gemini API error [{response.status}]: {error_data}")
-     raise HTTPException(status_code=response.status, detail=error_data)
+     raise HTTPException(status_code=response.status, detail=error_detail)
```

---

### Custom OpenAI API 변경사항

#### 변경 1: 요청 모델 (라인 20-30)
```diff
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
+   top_p: Optional[float] = None
+   top_k: Optional[int] = None
+   frequency_penalty: Optional[float] = None
+   presence_penalty: Optional[float] = None
+   stop: Optional[List[str]] = None
```

#### 변경 2: Payload 생성 (라인 53-75)
```diff
- payload = {
-     "model": request.model,
-     "messages": [{"role": m.role, "content": m.content} for m in request.messages],
-     "temperature": request.temperature,
-     "max_tokens": request.max_tokens,
-     "stream": request.stream
- }

+ payload = {
+     "model": request.model,
+     "messages": [{"role": m.role, "content": m.content} for m in request.messages],
+ }

+ if request.temperature is not None:
+     payload["temperature"] = request.temperature
+ if request.max_tokens is not None:
+     payload["max_tokens"] = request.max_tokens
+ if request.stream is not None:
+     payload["stream"] = request.stream
+ if request.top_p is not None:
+     payload["top_p"] = request.top_p
+ if request.top_k is not None:
+     payload["top_k"] = request.top_k
+ if request.frequency_penalty is not None:
+     payload["frequency_penalty"] = request.frequency_penalty
+ if request.presence_penalty is not None:
+     payload["presence_penalty"] = request.presence_penalty
+ if request.stop is not None:
+     payload["stop"] = request.stop
```

#### 변경 3: 에러 처리 (라인 85-95)
```diff
  if response.status != 200:
      error_data = await response.text()
+     error_detail = {
+         "status": response.status,
+         "message": error_data,
+         "model": request.model,
+         "endpoint": "custom",
+         "api_base": api_base
+     }
+     logger.error(f"Custom API error [{response.status}]: {error_data}")
-     raise HTTPException(status_code=response.status, detail=error_data)
+     raise HTTPException(status_code=response.status, detail=error_detail)
```

---

## 실제 사용 예제

### curl로 테스트 (Gemini)

**기본 요청:**
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [{"role": "user", "content": "Hi"}],
    "temperature": 0.7
  }'
```

**시스템 프롬프트 포함:**
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [{"role": "user", "content": "2+2는?"}],
    "system_prompt": "You are a math expert. Explain step by step.",
    "top_p": 0.9,
    "top_k": 40,
    "temperature": 0.2,
    "max_output_tokens": 512
  }'
```

### Python으로 테스트

**Gemini API:**
```python
import requests

response = requests.post(
    "http://localhost:8001/api/v1/gemini/chat/completions",
    json={
        "model": "gemini-3-pro",
        "messages": [
            {"role": "user", "content": "파이썬 클래스 설명"}
        ],
        "system_prompt": "You are a Python expert.",
        "temperature": 0.3,
        "top_p": 0.95,
        "max_output_tokens": 1024
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

**Custom OpenAI API:**
```python
import requests

response = requests.post(
    "http://localhost:8001/api/v1/custom/chat/completions",
    json={
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "AI의 미래"}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.1,
        "max_tokens": 800
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

---

## 파라미터 설명 (간단 버전)

| 파라미터 | 범위 | 효과 | 예시 |
|---------|------|------|------|
| temperature | 0.0~2.0 | 낮음=확정, 높음=창의 | 0.2(수학), 0.8(창의) |
| top_p | 0.0~1.0 | Nucleus sampling | 0.95(다양), 0.5(집중) |
| top_k | 1~40+ | Top-K sampling | 40(표준), 5(집중) |
| frequency_penalty | -2.0~2.0 | 반복 억제 | 0.5(반복 줄임) |
| presence_penalty | -2.0~2.0 | 새 토픽 | 0.1(장려) |
| max_tokens | 1~모델_최대 | 답변 길이 제한 | 512(짧음), 2048(길음) |
| system_prompt | 문자열 | 역할 정의 | "You are..." |
| stop | 문자열 배열 | 생성 중단 | ["\\n\\n", "---"] |

---

## 에러 처리 개선 사항

### 이전 (단순)
```json
{
  "detail": "Unauthorized"
}
```

### 이후 (구조화됨)
```json
{
  "detail": {
    "status": 401,
    "message": "Unauthorized",
    "model": "gemini-3-pro",
    "endpoint": "gemini"
  }
}
```

---

## 호환성

| 기능 | Gemini | Custom OpenAI |
|------|--------|---------------|
| 온도 조절 | ✓ | ✓ |
| Top-P 샘플링 | ✓ | ✓ |
| Top-K 샘플링 | ✓ | ✓ |
| 시스템 프롬프트 | ✓ | ✓* |
| Frequency 페널티 | ✗ | ✓ |
| Presence 페널티 | ✗ | ✓ |
| 중지 시퀀스 | ✗ | ✓ |

*Custom OpenAI: system role message로 구현

---

## 커밋 시 확인사항

- [ ] 문법 검증: `python -m py_compile gemini.py custom_openai.py`
- [ ] 테스트: curl/Python으로 새 파라미터 확인
- [ ] 로그: 에러 로그에 상세 정보 출력 확인
- [ ] 에러: 구조화된 에러 응답 확인

---

## 다음 단계

### 우선순위 1
```python
# Streaming 응답 구현
if request.stream:
    async def stream_generator():
        async for line in response.content:
            yield line
    return StreamingResponse(stream_generator())
```

### 우선순위 2
```python
# Function calling 지원
if request.tools:
    payload["tools"] = request.tools
    # ... 응답 처리 로직
```

### 우선순위 3
```python
# Vision API 지원 (이미지 입력)
if request.image_url:
    # Gemini: parts에 imageData 추가
    # OpenAI: messages에 image content 추가
```

---

## 문서 참고

- **상세 가이드**: API_STRUCTURE_GUIDE.md
- **테스트 예제**: TEST_API_MODIFICATIONS.md
- **변경 요약**: API_MODIFICATIONS_SUMMARY.md
- **이전 교훈**: SESSION_4_GEMINI_MODELS_ADD.md

---

**상태**: 완료 ✓
**테스트**: 필요 (curl/Python 스크립트)
**배포**: 준비 완료
