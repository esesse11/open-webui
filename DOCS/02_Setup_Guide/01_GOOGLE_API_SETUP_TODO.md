# Session 5: Google API 등록 및 모델 추가 - TODO 리스트

**작성 날짜**: 2025-11-22
**현재 상태**: 준비 단계
**목표**: Google API 등록 후 Gemini 3 Pro와 NanoBanana2 모델을 OpenWebUI에 추가

---

## 📋 전체 작업 목표

Session 4에서 API 구조를 개선했으므로, 이제 실제로 모델을 추가하는 작업을 진행합니다.

### 최종 목표
- ✅ **Gemini 3 Pro** 모델을 OpenWebUI Settings > Models에서 사용 가능하게 만들기
- ✅ **NanoBanana2** 모델을 OpenWebUI Settings > Models에서 사용 가능하게 만들기
- ✅ 새로운 API 파라미터 (system_prompt, top_p, top_k 등) 테스트하기

---

## 🎯 단계별 작업 계획

### Phase 1: Google API 설정 (필수)

#### Task 1-1: Google Cloud API Key 준비
- [ ] Google Cloud 콘솔 접속
- [ ] 프로젝트 생성 (또는 기존 프로젝트 선택)
- [ ] Google Generative AI API 활성화
- [ ] API Key 생성
- [ ] API Key 복사 (안전한 곳에 저장)

**참고**: 구글 계정이 필요합니다. `https://console.cloud.google.com`

---

#### Task 1-2: OpenWebUI에 Google API Key 등록
- [ ] OpenWebUI 웹 페이지 열기 (`http://localhost:8001`)
- [ ] 우측 상단 톱니바퀴 아이콘 (Settings) 클릭
- [ ] **Connections** 메뉴 찾기
- [ ] **Google** 또는 **Gemini** 옵션 선택
- [ ] 준비한 API Key 입력
- [ ] **저장** 클릭

**예상 결과**: "Connection successful" 메시지

---

#### Task 1-3: Gemini 모델 자동 추가 확인
- [ ] OpenWebUI Settings 페이지 새로고침
- [ ] **Models** 메뉴로 이동
- [ ] 다음 모델들이 보이는지 확인:
  - `gemini-3-pro` (NEW - Gemini 3 Pro)
  - `gemini-1.5-pro`
  - `gemini-1.5-flash`
  - `gemini-pro`
- [ ] 각 모델의 설정 확인 (이름, 설명, 활성화 여부)

**예상 결과**: Gemini 3 Pro와 다른 Google 모델들이 자동으로 표시됨

---

### Phase 2: NanoBanana2 모델 설정 (선택)

#### Task 2-1: NanoBanana2 API 제공자 확인
- [ ] NanoBanana2가 독립적인 API 제공자인지 확인
- [ ] API 엔드포인트 확인
- [ ] API Key 확인 (있는 경우)

**참고**:
- NanoBanana가 Banana.dev API를 사용하는 경우, 별도의 API Key 필요
- 또는 OpenAI 호환 API인 경우, OPENAI_API_BASE_URL 수정으로 가능

---

#### Task 2-2a: NanoBanana가 독립 API 제공자인 경우
- [ ] Banana.dev API Key 준비
- [ ] OpenWebUI의 Custom API Endpoint 설정
- [ ] CUSTOM_API_BASE_URL 환경 변수 설정
- [ ] 모델 테스트

**환경 변수 예시**:
```bash
OPENAI_API_BASE_URL=https://api.banana.dev/v1
OPENAI_API_KEY=your-banana-api-key
```

---

#### Task 2-2b: NanoBanana를 커스텀 모델로 추가하는 경우
- [ ] OpenWebUI Settings > Models
- [ ] **+ Add Model** 클릭
- [ ] 다음 정보 입력:
  - **Model ID**: `nano-banana-2`
  - **Model Name**: `NanoBanana 2 - Image Generation`
  - **Base Model**: (적절한 기본 모델 선택)
  - **Description**: `High-quality image generation with Gemini 3 Pro backend`
- [ ] 저장

---

### Phase 3: 모델 테스트 (필수)

#### Task 3-1: Gemini 3 Pro API 테스트
```bash
curl -X POST http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [{"role": "user", "content": "안녕하세요"}],
    "temperature": 0.7,
    "top_p": 0.9,
    "system_prompt": "You are a helpful assistant"
  }'
```

**검증 항목**:
- [ ] 응답 코드: 200
- [ ] 응답 포함 필드: id, object, model, choices, usage
- [ ] 새 파라미터 적용 확인: system_prompt가 API로 전달됨

---

#### Task 3-2: NanoBanana2 API 테스트 (해당하는 경우)
```bash
curl -X POST http://localhost:8001/api/v1/custom/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2",
    "messages": [{"role": "user", "content": "이미지 생성 테스트"}],
    "temperature": 0.8,
    "top_p": 0.95,
    "frequency_penalty": 0.3
  }'
```

**검증 항목**:
- [ ] 응답 코드: 200
- [ ] 새 파라미터 적용 확인: frequency_penalty가 API로 전달됨
- [ ] 에러 처리 확인: 에러 응답이 구조화됨

---

#### Task 3-3: Python 클라이언트로 테스트
```python
# TEST_API_MODIFICATIONS.md의 예제 코드 실행
import requests

# Gemini 3 Pro 테스트
response = requests.post(
    "http://localhost:8001/api/v1/gemini/chat/completions",
    json={
        "model": "gemini-3-pro",
        "messages": [{"role": "user", "content": "파이썬이란?"}],
        "system_prompt": "You are a Python expert",
        "temperature": 0.3,
        "top_p": 0.95,
        "max_output_tokens": 1024
    }
)

result = response.json()
print(result["choices"][0]["message"]["content"])
```

**검증 항목**:
- [ ] 응답 정상 수신
- [ ] 시스템 프롬프트의 영향 확인 (Python 전문가처럼 답변)
- [ ] top_p 적용 확인 (다양한 답변)

---

### Phase 4: 웹 UI 테스트 (최종)

#### Task 4-1: 웹 UI에서 모델 선택 및 사용
- [ ] OpenWebUI 웹 페이지 열기
- [ ] 채팅 페이지에서 모델 선택 드롭다운 클릭
- [ ] **Gemini 3 Pro** 선택 가능 확인
- [ ] NanoBanana2도 보이는지 확인 (추가된 경우)

---

#### Task 4-2: 실제 채팅 테스트
- [ ] Gemini 3 Pro 모델로 채팅 시작
- [ ] 다양한 질문 입력:
  - 간단한 질문 (1+1은?)
  - 복잡한 질문 (파이썬 코드 작성)
  - 창의적인 질문 (이야기 지어줘)
- [ ] 응답 품질 확인
- [ ] 응답 시간 확인

---

#### Task 4-3: API 파라미터 효과 확인
- [ ] 온도(temperature) 변경 테스트:
  - 0.1 (확정성 높음)
  - 0.7 (기본)
  - 1.5 (창의성 높음)
- [ ] top_p 변경 테스트:
  - 0.5 (집중)
  - 0.95 (다양)
- [ ] max_output_tokens 변경 테스트:
  - 100 (짧음)
  - 2000 (길음)

**예상 결과**: 파라미터에 따라 응답의 스타일이 달라짐

---

### Phase 5: 문서 업데이트

#### Task 5-1: 성공 기록
- [ ] 이 파일 (SESSION_5_TODO.md)을 완료 내용으로 업데이트
- [ ] 각 작업의 완료 체크박스 표시
- [ ] 예상과 다른 결과 기록

---

#### Task 5-2: 문제 해결 문서 작성 (필요한 경우)
- [ ] 발생한 문제 기록
- [ ] 해결 방법 기록
- [ ] 원인 분석

---

#### Task 5-3: 최종 보고서 작성
- [ ] 전체 작업 요약
- [ ] 성공한 부분
- [ ] 실패한 부분 (있는 경우)
- [ ] 다음 단계

---

## 🔍 예상 결과 시나리오

### 시나리오 A: 완전 성공
```
✓ Google API Key 등록 완료
✓ Gemini 3 Pro 자동 추가
✓ Gemini 3 Pro로 채팅 가능
✓ 새 파라미터 (top_p, system_prompt) 작동
✓ NanoBanana2 추가 (선택사항)
```

**상태**: Production Ready

---

### 시나리오 B: Gemini는 성공, NanoBanana는 실패
```
✓ Google API Key 등록 완료
✓ Gemini 3 Pro 자동 추가
✓ Gemini 3 Pro로 채팅 가능
✗ NanoBanana2 추가 실패 (API 정보 불명확)
```

**상태**: Partial Success
**다음 액션**: NanoBanana2 API 제공자 확인

---

### 시나리오 C: Google API 등록 실패
```
✗ API Key 등록 실패 (인증 오류)
✗ Gemini 3 Pro 미추가
```

**가능한 원인**:
- API Key가 잘못됨
- Google Cloud 프로젝트 설정 오류
- 네트워크 연결 문제

**해결 방법**:
- API Key 다시 확인
- Google Cloud 콘솔에서 API 활성화 확인
- 방화벽/네트워크 설정 확인

---

## 📊 진행 상황 추적

### 현재 진행률
```
Phase 1 (Google API 설정):        [ ] 0%
Phase 2 (NanoBanana2 설정):       [ ] 0%
Phase 3 (모델 테스트):            [ ] 0%
Phase 4 (웹 UI 테스트):           [ ] 0%
Phase 5 (문서 업데이트):          [ ] 0%

전체 진행률:                      [ ] 0%
```

---

## 🔧 필요한 도구 및 정보

### 필수
- [ ] Google Cloud 계정
- [ ] OpenWebUI 실행 중 (http://localhost:8001)
- [ ] curl 또는 Python (API 테스트용)

### 선택
- [ ] NanoBanana API 정보 (NanoBanana2 추가할 경우)
- [ ] Postman (API 테스트용)

---

## 📚 참고 문서

| 문서 | 용도 |
|------|------|
| API_STRUCTURE_GUIDE.md | API 파라미터 설명 |
| TEST_API_MODIFICATIONS.md | 테스트 방법 및 curl 예제 |
| QUICK_REFERENCE.md | 빠른 참조 |
| SESSION_4_GEMINI_MODELS_ADD.md | 이전 실패 원인 (배경 이해) |

---

## ⏰ 예상 소요 시간

| Phase | 시간 |
|-------|------|
| 1. Google API 설정 | 5분 |
| 2. NanoBanana2 설정 | 10분 |
| 3. 모델 테스트 | 15분 |
| 4. 웹 UI 테스트 | 15분 |
| 5. 문서 업데이트 | 10분 |
| **합계** | **55분** |

---

## ✅ 완료 체크리스트

### 전체 요구사항
- [ ] Google API Key 등록 완료
- [ ] Gemini 3 Pro 모델 추가 확인
- [ ] API 테스트 (curl/Python) 성공
- [ ] 웹 UI에서 모델 사용 가능 확인
- [ ] 새 파라미터 동작 확인
- [ ] 문서 업데이트 완료

---

## 📝 작업 기록

작업 진행 중에 다음을 기록하세요:

```markdown
## 작업 진행 기록

### 2025-11-22 Google API 설정 시작
- API Key 생성: [시간]
- OpenWebUI 등록: [시간]
- 문제 발생: [문제 설명]
- 해결 방법: [해결 방법]

### 2025-11-22 테스트
- curl 테스트: [결과]
- Python 테스트: [결과]
- 웹 UI 테스트: [결과]
```

---

## 🎓 배운 점 (Session 4에서)

이 세션을 진행하기 전에 Session 4의 교훈을 상기하세요:

❌ **하지 말아야 할 것**:
- DB에 모델을 직접 추가하기
- API 엔드포인트만 만들기
- 소스 코드 수정부터 시작하기

✅ **해야 할 것**:
- Settings > Connections에서 API 연결
- 자동으로 모델이 추가되기를 기다리기
- 공식적인 방법 사용

---

## 🚀 다음 단계 (이후 세션)

이 세션이 완료되면 다음을 고려하세요:

1. **Streaming 응답 구현**: 실시간 응답 받기
2. **Function Calling**: AI 모델이 함수 호출 가능하게 만들기
3. **Vision API**: 이미지 입력 지원
4. **Custom Models**: 사용자 정의 모델 추가

---

**생성 날짜**: 2025-11-22
**상태**: 준비 단계
**다음 액션**: Task 1-1부터 시작 (Google API Key 준비)
