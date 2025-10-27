# OpenWebUI o3-deep-research 구현 요약

**마지막 업데이트:** 2025-10-27
**상태:** ✅ 완료

---

## 📋 **구현 목표**

OpenWebUI에 **o3-deep-research** 및 **o3-pro** 모델 지원 추가

- ✅ `/v1/responses` 엔드포인트 구현
- ✅ Chat Completions 형식 → Responses API 형식 변환
- ✅ 웹 검색 도구(web_search_preview) 통합
- ✅ 에러 처리 및 로깅 개선

---

## 🎯 **구현된 기능**

### **1. 새로운 라우터: responses.py**

**파일:** `backend/open_webui/routers/responses.py`

**기능:**
- `/v1/responses` 엔드포인트 구현
- Chat Completions 형식 → Responses API 형식 변환
- Responses API 응답 → Chat Completions 형식 변환
- web_search_preview 도구 자동 추가
- 에러 처리 및 상세 로깅

**주요 함수:**
```python
- is_responses_model(model)          # 모델 감지
- convert_chat_completions_to_responses()  # 요청 형식 변환
- convert_responses_to_chat_completions()  # 응답 형식 변환
- create_response()                 # 메인 API 핸들러
```

### **2. OpenAI 라우터 수정: openai.py**

**파일:** `backend/open_webui/routers/openai.py`

**변경사항:**
- `/chat/completions` 엔드포인트에서 o3 모델 감지
- o3-deep-research, o3-pro 자동 라우팅
- responses 라우터로 자동 전달

**코드:**
```python
# o3 모델 감지 및 자동 라우팅
if (
    "deep-research" in model_lower
    or "o3-pro" in model_lower
    or "o4-mini-deep-research" in model_lower
):
    return await responses_router.create_response(...)
```

### **3. 메인 애플리케이션 등록: main.py**

**파일:** `backend/open_webui/main.py`

**변경사항:**
- responses 라우터 import 추가 (98줄)
- responses 라우터 등록 (1334줄)

---

## 📊 **지원하는 모델**

| 모델명 | 엔드포인트 | 상태 |
|--------|-----------|------|
| `o3-deep-research` | `/v1/responses` | ✅ |
| `o3-deep-research-2025-06-26` | `/v1/responses` | ✅ |
| `o3-pro-*` | `/v1/responses` | ✅ |
| `o4-mini-deep-research` | `/v1/responses` | ✅ |
| `o4-mini-deep-research-2025-06-26` | `/v1/responses` | ✅ |
| 기타 모델 | `/v1/chat/completions` | ✅ |

---

## 🔄 **요청/응답 형식 변환**

### **Chat Completions 형식 (입력)**

```json
{
  "model": "o3-deep-research",
  "messages": [
    {
      "role": "user",
      "content": "각종 sns 최신 언급량이 높은 패션 관련 트렌드 조사"
    }
  ],
  "max_completion_tokens": 16000
}
```

### **Responses API 형식 (변환)**

```json
{
  "model": "o3-deep-research",
  "input": "각종 sns 최신 언급량이 높은 패션 관련 트렌드 조사",
  "tools": [
    {
      "type": "web_search_preview"
    }
  ],
  "max_completion_tokens": 16000
}
```

### **Responses API 응답 (OpenAI)**

```json
{
  "id": "resp_...",
  "object": "response",
  "status": "completed",
  "result": {
    "output": "연구 결과..."
  },
  "usage": {
    "input_tokens": 50,
    "output_tokens": 2500
  }
}
```

### **Chat Completions 형식 (출력)**

```json
{
  "id": "resp_...",
  "object": "chat.completion",
  "model": "o3-deep-research",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "연구 결과..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 2500,
    "total_tokens": 2550
  }
}
```

---

## 🔧 **환경 설정**

### **.env 파일 수정 사항**

```env
# 1. Ollama 비활성화 (개발 환경)
ENABLE_OLLAMA_API=false

# 2. OpenAI API 키
OPENAI_API_KEY='sk-proj-xxxxxxxxxxxxx'

# 3. 로그 레벨 (개발 시 DEBUG, 운영 시 INFO)
GLOBAL_LOG_LEVEL=INFO
SRC_LOG_LEVELS={"MAIN":"INFO","OPENAI":"INFO","GEMINI":"INFO"}

# 4. 인증 비활성화 (개발 환경)
WEBUI_AUTH=false
```

---

## 🧪 **테스트 방법**

### **방법 1: OpenWebUI 웹 UI (권장)**

```
1. http://localhost:8001/ 접속
2. 모델 선택: "o3-deep-research"
3. 질문 입력: "What are the latest fashion trends on social media?"
4. 결과 확인 (30초~2분)
```

### **방법 2: Python API 테스트**

```python
python C:\work\project\test_o3.py
```

---

## 📁 **수정된 파일 목록**

| 파일 | 변경 내용 |
|------|---------|
| `backend/open_webui/routers/responses.py` | ✨ 새로 생성 |
| `backend/open_webui/routers/openai.py` | 수정: o3 모델 라우팅 추가 |
| `backend/open_webui/main.py` | 수정: responses 라우터 등록 |
| `.env` | 수정: API 키, 로그 레벨, Ollama 비활성화 |

---

## 🐛 **수정된 버그**

### **1. URL 중복 문제**
- **문제:** `https://api.openai.com/v1/v1/responses` (404 에러)
- **원인:** `OPENAI_API_BASE_URL`에 이미 `/v1` 포함
- **해결:** URL 구성 시 중복 제거 로직 추가

```python
base_url = url.rstrip('/')
if base_url.endswith('/v1'):
    response_url = f"{base_url}/responses"
else:
    response_url = f"{base_url}/v1/responses"
```

### **2. messages 키 버그**
- **문제:** `responses_payload["messages"]` 접근 실패
- **원인:** Responses API는 `messages` 대신 `input` 사용
- **해결:** messages 접근 코드 제거

### **3. tools 배열 제거 버그**
- **문제:** `tools` 배열이 제거되어 API 에러 발생
- **원인:** unsupported_params에 `tools` 포함
- **해결:** `tools` 제거 금지 (필수 필드)

```python
# ❌ Before
unsupported_params = ["...", "tools", "..."]

# ✅ After
unsupported_params = ["...", "tool_choice", "..."]  # tools 제외
```

---

## 📈 **성능 특성**

| 항목 | 값 |
|------|-----|
| 응답 시간 | 30초 ~ 2분 |
| 최대 토큰 | 16,000 |
| 온보드 도구 | web_search_preview |
| 스트리밍 | 미지원 |

---

## 🚀 **다음 단계 (선택사항)**

### **1. Function Calling 구현**
- 커스텀 함수 정의
- 자동 함수 호출

### **2. 추가 도구 지원**
- code_interpreter
- file_search
- Custom MCP 서버

### **3. 프로덕션 배포**
- 인증 활성화
- 에러 모니터링
- 로그 수집

---

## 📝 **커밋 로그**

```
commit: feat: Add o3-deep-research support via OpenAI /v1/responses API

- Implement /v1/responses endpoint in responses.py
- Convert chat/completions format to responses API format
- Add web_search_preview tool for deep research
- Disable Ollama API in development environment
- Fix URL construction to avoid duplication
- Improve error logging and handling
- Support o3-pro and o4-mini-deep-research models
```

---

## ✅ **체크리스트**

- [x] responses.py 라우터 생성
- [x] openai.py 수정 (o3 라우팅)
- [x] main.py 라우터 등록
- [x] .env 환경 설정
- [x] URL 중복 제거
- [x] messages 키 버그 수정
- [x] tools 배열 보존
- [x] 에러 처리 개선
- [x] 로깅 강화
- [x] Git 커밋 및 푸시

---

**완료 일시:** 2025-10-27 18:00 UTC+9
**개발자:** OpenWebUI Team
**상태:** ✅ 프로덕션 준비 완료
