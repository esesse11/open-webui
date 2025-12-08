# gpt-image-1 모델 오류 해결 가이드

**작성일**: 2025-12-06
**오류**: "This model is only supported in v1/responses and not in v1/chat/completions."

---

## 🔍 문제 분석

### 오류 메시지
```
This model is only supported in v1/responses and not in v1/chat/completions.
```

### 원인
1. **"gpt-image-1" 모델**이 OpenAI의 **Responses API**를 사용하는 특별한 모델임
2. OpenWebUI가 기본적으로 `/v1/chat/completions` 엔드포인트로 요청
3. 하지만 이 모델은 `/v1/responses` 엔드포인트만 지원
4. **responses.py의 `is_responses_model()` 함수**에 "gpt-image-1"이 등록되지 않음

---

## 📊 Responses API란?

### 일반 Chat Completions API
```
POST /v1/chat/completions
- 일반적인 GPT 모델 (gpt-4, gpt-3.5-turbo 등)
- 대화형 응답
```

### Responses API (고급 추론 모델용)
```
POST /v1/responses
- 특별한 추론 모델 전용
- 현재 지원 모델:
  * o3-deep-research
  * o4-deep-research
  * o3-pro
  * o4-mini-deep-research
  * gpt-image-1 ⬅️ 새로 발견!
```

---

## 🔧 해결 방법

### 방법 1: responses.py 수정 ⭐ 추천

**파일**: `C:\openwebui\source\open-webui\backend\open_webui\routers\responses.py`

**수정 위치**: 라인 43-68의 `is_responses_model()` 함수

#### Before (현재 코드)
```python
def is_responses_model(model: str) -> bool:
    """
    Check if the model uses responses API (o3-deep-research, o3-pro, etc.)
    """
    if not model:
        return False
    model_lower = model.lower()

    # Models that require /v1/responses endpoint
    responses_models = [
        "o3-deep-research",
        "o4-deep-research",
        "o3-pro",
        "o4-mini-deep-research",
    ]

    return (
        "deep-research" in model_lower
        or "o3-pro" in model_lower
        or "o4-mini-deep-research" in model_lower
        or model_lower in responses_models
    )
```

#### After (수정 버전)
```python
def is_responses_model(model: str) -> bool:
    """
    Check if the model uses responses API (o3-deep-research, o3-pro, etc.)
    """
    if not model:
        return False
    model_lower = model.lower()

    # Models that require /v1/responses endpoint
    responses_models = [
        "o3-deep-research",
        "o4-deep-research",
        "o3-pro",
        "o4-mini-deep-research",
        "gpt-image-1",          # 추가: 이미지 추론 모델
    ]

    return (
        "deep-research" in model_lower
        or "o3-pro" in model_lower
        or "o4-mini-deep-research" in model_lower
        or "gpt-image" in model_lower          # 추가: gpt-image 패턴
        or model_lower in responses_models
    )
```

**변경 사항**:
1. `responses_models` 리스트에 `"gpt-image-1"` 추가
2. 조건문에 `or "gpt-image" in model_lower` 추가
   - 미래의 gpt-image-2, gpt-image-3 등도 자동 지원

---

### 방법 2: 모델 이름 변경

**Admin Panel에서**:
- "gpt-image-1" 대신 지원되는 다른 이미지 모델 사용
- 예: `gpt-4-vision-preview`, `gpt-4-turbo-vision` 등

---

## 🚀 구현 단계

### 1단계: 백업
```bash
cp C:\openwebui\source\open-webui\backend\open_webui\routers\responses.py C:\work\project\BACKUP\openwebui\responses.py.backup
```

### 2단계: responses.py 수정
위의 "After" 코드로 `is_responses_model()` 함수 수정

### 3단계: 서버 재시작
```bash
# 서버가 --reload 모드라면 자동 재시작
# 아니면 수동으로 재시작
```

### 4단계: 테스트
1. OpenWebUI에서 "gpt-image-1" 모델 선택
2. 이미지 + 텍스트 프롬프트 입력
3. 정상 작동 확인

---

## ⚙️ 동작 방식

### 수정 전
```
사용자 → OpenWebUI → /v1/chat/completions (gpt-image-1)
                    ↓
                  ❌ 오류: "only supported in v1/responses"
```

### 수정 후
```
사용자 → OpenWebUI → is_responses_model("gpt-image-1")
                    ↓
                  ✅ True
                    ↓
                  /v1/responses (gpt-image-1)
                    ↓
                  ✅ 성공
```

---

## 🔍 is_responses_model() 함수의 역할

### 체크 로직
```python
# 1. 모델 이름이 리스트에 있는가?
model_lower in responses_models

# 2. 또는 특정 패턴이 포함되어 있는가?
"deep-research" in model_lower
"o3-pro" in model_lower
"gpt-image" in model_lower  # 새로 추가
```

### 자동 라우팅
```python
# openai.py 또는 다른 라우터에서:
if is_responses_model(model_name):
    # /v1/responses 엔드포인트 사용
    use_responses_api()
else:
    # /v1/chat/completions 엔드포인트 사용
    use_chat_completions_api()
```

---

## 🧪 테스트 스크립트

### Python 테스트
```python
# responses.py의 함수 직접 테스트

def is_responses_model(model: str) -> bool:
    if not model:
        return False
    model_lower = model.lower()

    responses_models = [
        "o3-deep-research",
        "o4-deep-research",
        "o3-pro",
        "o4-mini-deep-research",
        "gpt-image-1",  # 추가
    ]

    return (
        "deep-research" in model_lower
        or "o3-pro" in model_lower
        or "o4-mini-deep-research" in model_lower
        or "gpt-image" in model_lower  # 추가
        or model_lower in responses_models
    )

# 테스트
test_models = [
    "gpt-image-1",           # True ✅
    "gpt-image-2",           # True ✅
    "GPT-IMAGE-1",           # True ✅
    "o3-deep-research",      # True ✅
    "gpt-4-vision-preview",  # False (일반 chat/completions)
    "gpt-4",                 # False
]

for model in test_models:
    result = is_responses_model(model)
    print(f"{model}: {result}")
```

**예상 출력**:
```
gpt-image-1: True ✅
gpt-image-2: True ✅
GPT-IMAGE-1: True ✅
o3-deep-research: True ✅
gpt-4-vision-preview: False
gpt-4: False
```

---

## 📋 추가 참고 사항

### Responses API 특징
1. **입력 형식**:
   ```json
   {
     "model": "gpt-image-1",
     "input": "사용자 질문",
     "tools": [{"type": "web_search_preview"}]
   }
   ```

2. **출력 형식**:
   ```json
   {
     "id": "resp_...",
     "object": "response",
     "status": "completed",
     "result": {
       "output": "응답 텍스트"
     }
   }
   ```

3. **자동 변환**:
   - OpenWebUI가 chat/completions 형식 → responses 형식 자동 변환
   - `convert_chat_completions_to_responses()` 함수 사용
   - 응답도 자동으로 chat/completions 형식으로 변환

---

## ⚠️ 주의사항

### 1. 이미지 지원 확인
"gpt-image-1"이 실제로 이미지를 지원하는지 확인 필요:
- Responses API는 기본적으로 텍스트 입력만 지원
- 이미지 입력은 별도 처리 필요할 수 있음

### 2. API 키 확인
- gpt-image-1이 실제 OpenAI 모델인지 확인
- API 키가 해당 모델에 접근 권한이 있는지 확인

### 3. 비용
- Responses API 모델은 일반적으로 비용이 높음
- 사용 전 가격 확인 권장

---

## 🔗 관련 파일

- **responses.py**: `C:\openwebui\source\open-webui\backend\open_webui\routers\responses.py`
- **백업**: `C:\work\project\BACKUP\openwebui\responses.py.backup` (생성 예정)
- **main.py**: 라우터 등록 (라인 1402-1403)

---

## 📞 다음 단계

수정을 진행하시겠습니까?

**옵션 A**: 직접 수정 시작
- responses.py 백업 후 수정
- 서버 재시작
- 테스트

**옵션 B**: 더 알아보기
- gpt-image-1이 정확히 무엇인지 조사
- OpenAI 문서 확인
- 다른 모델 시도

---

**작성자**: Claude Code
**최종 수정**: 2025-12-06
**상태**: 해결 방법 제시 완료
