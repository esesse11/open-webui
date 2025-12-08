# Google/Gemini 이미지 생성 오류 해결

**작성일**: 2025-12-06
**오류**: "An error occurred while generating an image"
**사용 모델**: models/gemini-2.5-flash

---

## 🔍 문제 원인

### 잘못 사용한 모델
```
❌ gemini-2.5-flash → 텍스트 생성 모델 (이미지 생성 불가)
```

### 올바른 모델
```
✅ imagen-3.0-generate-002 → 이미지 생성 전용 모델
```

---

## 📊 모델 구분

### Google의 AI 모델 종류

| 모델 시리즈 | 용도 | 예시 |
|------------|------|------|
| **Gemini** | 텍스트 생성, 대화, 코딩 | gemini-2.5-flash, gemini-1.5-pro |
| **Imagen** | 이미지 생성 | imagen-3.0-generate-002, imagen-2.0 |
| **Gemini Vision** | 이미지 이해 | gemini-2.5-flash-image-preview |

### 현재 문제
- **Gemini (텍스트 모델)** ≠ **Imagen (이미지 생성 모델)**
- `gemini-2.5-flash`로 이미지 생성 시도 → 실패

---

## 🔧 올바른 OpenWebUI 설정

### Admin Panel → Settings → Images

#### Image Generation (이미지 생성)

**Image Generation Engine**:
```
gemini
```

**Image Generation Model**:
```
imagen-3.0-generate-002
```
⚠️ **중요**: `gemini-2.5-flash` 입력하면 안 됨!

**Gemini API Base URL**:
```
https://us-central1-aiplatform.googleapis.com/v1
```
또는
```
https://generativelanguage.googleapis.com/v1beta
```

**Gemini API Key**:
```
실제 Google Cloud API 키
```

**Endpoint Method**:
```
predict (기본값, 추천)
```
또는
```
generateContent
```

---

## 🔑 Google Cloud API 설정

### 1. API 활성화

**Google Cloud Console**:
```
APIs & Services → Enable APIs & Services
→ "Vertex AI API" 검색 후 활성화
→ "Generative Language API" 활성화 (선택사항)
```

### 2. API 키 생성

```
APIs & Services → Credentials
→ Create Credentials → API Key
→ 키 복사
```

### 3. API 키 제한 (보안)

**권장 설정**:
- Application restrictions: HTTP referrers (websites)
- API restrictions: Vertex AI API, Generative Language API

---

## 📋 OpenWebUI images.py 분석

### 지원되는 Gemini 이미지 모델

**코드** (images.py 라인 384-387):
```python
elif request.app.state.config.IMAGE_GENERATION_ENGINE == "gemini":
    return [
        {"id": "imagen-3.0-generate-002", "name": "imagen-3.0 generate-002"},
    ]
```

**결론**: 현재 OpenWebUI는 **imagen-3.0-generate-002만** 지원

---

## 🧪 API 엔드포인트

### 방법 1: predict (기본값)

**엔드포인트**:
```
POST {API_BASE_URL}/models/imagen-3.0-generate-002:predict
```

**요청 형식**:
```json
{
  "instances": {
    "prompt": "귀여운 고양이"
  },
  "parameters": {
    "sampleCount": 1,
    "outputOptions": {
      "mimeType": "image/png"
    }
  }
}
```

**헤더**:
```
Content-Type: application/json
x-goog-api-key: YOUR_API_KEY
```

---

### 방법 2: generateContent

**엔드포인트**:
```
POST {API_BASE_URL}/models/imagen-3.0-generate-002:generateContent
```

**요청 형식**:
```json
{
  "contents": [{
    "parts": [{
      "text": "귀여운 고양이"
    }]
  }]
}
```

---

## ⚠️ 자주하는 실수

### 1. 잘못된 모델 이름
```
❌ gemini-2.5-flash (텍스트 모델)
❌ gemini-1.5-pro (텍스트 모델)
❌ gemini-pro-vision (이미지 이해, 생성 X)
✅ imagen-3.0-generate-002 (이미지 생성)
```

### 2. 잘못된 API Base URL
```
❌ https://generativelanguage.googleapis.com/v1beta/openai
   (OpenAI 호환 엔드포인트, Imagen 미지원)

✅ https://us-central1-aiplatform.googleapis.com/v1
   (Vertex AI, Imagen 지원)
```

### 3. API 키 권한 문제
```
오류: "Permission denied" 또는 "API not enabled"
해결: Google Cloud Console에서 Vertex AI API 활성화
```

---

## 🚀 단계별 해결 방법

### 1단계: OpenWebUI 설정 수정

**Admin Panel → Settings → Images**:

```yaml
Image Generation:
  Engine: gemini
  Model: imagen-3.0-generate-002  # ⬅️ 여기 수정!

Gemini API:
  Base URL: https://us-central1-aiplatform.googleapis.com/v1
  API Key: [실제 Google API 키]
  Endpoint Method: predict
```

### 2단계: 설정 저장

**Save** 버튼 클릭

### 3단계: 테스트

1. 채팅창으로 이동
2. 이미지 생성 버튼 클릭 (🎨)
3. 프롬프트: "귀여운 고양이, 만화 스타일"
4. 생성 시작

---

## 📊 예상 결과

### 성공 시
```
✅ imagen-3.0-generate-002가 이미지 생성
✅ 고품질 이미지 출력
✅ 빠른 생성 속도
```

### 실패 시
```
❌ 오류: "API key not valid"
→ Google Cloud Console에서 API 키 확인

❌ 오류: "API not enabled"
→ Vertex AI API 활성화

❌ 오류: "Permission denied"
→ API 키 권한 확인
```

---

## 🔍 서버 로그 확인

### OpenWebUI 서버 터미널에서

성공 시:
```
INFO: POST /models/imagen-3.0-generate-002:predict
INFO: Image generated successfully
```

실패 시:
```
ERROR: Failed to generate image: [오류 메시지]
```

---

## 💡 추가 정보

### Imagen vs Gemini Vision

**혼동하기 쉬운 점**:

| 기능 | Imagen | Gemini Vision |
|------|--------|---------------|
| 용도 | 이미지 **생성** | 이미지 **이해** |
| 입력 | 텍스트 프롬프트 | 이미지 + 텍스트 |
| 출력 | 이미지 | 텍스트 설명 |
| 모델 | imagen-3.0-generate-002 | gemini-*-vision |
| 엔드포인트 | :predict 또는 :generateContent | :generateContent |

### 사용 예시

**Imagen (이미지 생성)**:
```
사용자: "고양이 그림 그려줘"
→ Imagen → 🖼️ 고양이 이미지
```

**Gemini Vision (이미지 이해)**:
```
사용자: [고양이 사진 업로드] "이게 뭐야?"
→ Gemini Vision → "이것은 귀여운 고양이입니다"
```

---

## 📖 참고 자료

### Google Cloud 문서
- **Imagen API**: https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview
- **Vertex AI**: https://cloud.google.com/vertex-ai/docs
- **API 키 관리**: https://cloud.google.com/docs/authentication/api-keys

### OpenWebUI
- **Images 설정**: images.py 라인 600-660
- **지원 모델**: images.py 라인 384-387

---

## 🎯 핵심 요약

### 문제
```
❌ models/gemini-2.5-flash를 이미지 생성에 사용
→ 오류: "An error occurred while generating an image"
```

### 원인
```
gemini-2.5-flash = 텍스트 모델 (이미지 생성 불가)
```

### 해결
```
✅ Admin Panel → Images
✅ Model: imagen-3.0-generate-002
✅ API Base URL: https://us-central1-aiplatform.googleapis.com/v1
✅ API Key: Google Cloud API 키
```

---

## ✅ 체크리스트

설정 전 확인:
- [ ] Google Cloud Console에서 Vertex AI API 활성화
- [ ] API 키 생성 및 복사
- [ ] OpenWebUI Admin Panel 접근 권한 확인

설정:
- [ ] Image Generation Engine = `gemini`
- [ ] Image Generation Model = `imagen-3.0-generate-002`
- [ ] Gemini API Base URL 입력
- [ ] Gemini API Key 입력
- [ ] Endpoint Method = `predict`
- [ ] 설정 저장

테스트:
- [ ] 이미지 생성 버튼 클릭
- [ ] 프롬프트 입력
- [ ] 이미지 생성 성공 확인

---

**작성자**: Claude Code
**최종 수정**: 2025-12-06
**상태**: 해결 방법 제시 완료 ✅
