# Gemini 이미지 인식 문제 분석

**작성일**: 2025-12-06
**상태**: 조사 중

---

## 🔍 문제 현상

### 현재 동작
- ✅ **텍스트 프롬프트**: 정상 작동 (Gemini가 텍스트 응답)
- ❌ **이미지 + 텍스트 프롬프트**:
  - 텍스트로만 응답
  - 이미지를 인식하지 못함
  - 이미지를 생성하지 못함 (Gemini는 이미지 생성 모델이 아님)

### 테스트한 모델
- `models/gemini-2.5-flash-image-preview`

---

## 🧩 원인 분석

### 가능한 원인

#### 1. **OpenAI 호환 엔드포인트의 이미지 지원 문제**
현재 사용 중인 엔드포인트:
```
https://generativelanguage.googleapis.com/v1beta/openai
```

**문제점**:
- 이 엔드포인트가 OpenAI 호환 형식이지만, 이미지 입력을 완전히 지원하지 않을 수 있음
- OpenAI의 Vision API 형식과 Google의 Gemini 이미지 형식이 다를 수 있음

#### 2. **OpenWebUI의 이미지 전송 방식**
OpenWebUI가 이미지를 전송하는 방식:
- **Base64 인코딩**: 이미지를 base64로 인코딩해서 JSON에 포함
- **URL 형식**: 이미지 URL을 전송
- **Multipart 형식**: 파일 업로드

Gemini API가 기대하는 형식과 맞지 않을 수 있음

#### 3. **Gemini API 버전 문제**
Google Gemini API의 이미지 지원:
- **v1beta**: 베타 버전, 기능 제한 가능
- **네이티브 엔드포인트**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- **OpenAI 호환 엔드포인트**: 일부 기능 누락 가능

#### 4. **모델 선택 문제**
- 이미지를 지원하는 모델인지 확인 필요
- 모델 이름에 "image"가 포함되어 있지만 실제 지원 여부 확인 필요

---

## 🔬 진단 방법

### 1. Google Gemini API 직접 테스트

#### 네이티브 API 엔드포인트 테스트
```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "What is in this image?"},
        {
          "inline_data": {
            "mime_type": "image/jpeg",
            "data": "BASE64_ENCODED_IMAGE"
          }
        }
      ]
    }]
  }'
```

#### OpenAI 호환 엔드포인트 테스트
```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash-image-preview",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What is in this image?"},
        {
          "type": "image_url",
          "image_url": {"url": "data:image/jpeg;base64,BASE64_ENCODED_IMAGE"}
        }
      ]
    }]
  }'
```

### 2. OpenWebUI 디버깅

#### 브라우저 개발자 도구 확인
1. F12 → Network 탭
2. 이미지 포함 프롬프트 전송
3. Request Payload 확인:
   - 이미지가 포함되어 있는가?
   - 어떤 형식으로 전송되는가?

#### OpenWebUI 로그 확인
```bash
# 서버 터미널에서 로그 확인
# 이미지 관련 에러나 경고 메시지 찾기
```

---

## 💡 해결 방법

### 방법 1: 네이티브 Gemini API 엔드포인트 사용 (추천)

**장점**:
- ✅ 완전한 Gemini API 기능 사용 가능
- ✅ 이미지 지원 확실

**단점**:
- ⚠️ OpenWebUI 커스텀 라우터 구현 필요
- ⚠️ OpenAI 호환 형식 → Gemini 형식 변환 필요

**구현 방법**:
1. 새로운 `gemini_native.py` 라우터 생성
2. 이미지 포함 요청을 Gemini 네이티브 형식으로 변환
3. `/api/v1/gemini-native/chat/completions` 엔드포인트 제공

### 방법 2: OpenWebUI 이미지 설정 확인

**확인 사항**:
1. Admin Panel → Settings → Images
2. 이미지 업로드 설정
3. 이미지 프로세싱 설정

### 방법 3: 다른 Gemini 모델 테스트

**테스트할 모델**:
- `gemini-1.5-pro-vision` (있다면)
- `gemini-pro-vision`
- 다른 이미지 지원 모델

### 방법 4: Google AI Studio에서 확인

**검증 방법**:
1. https://aistudio.google.com/ 접속
2. 같은 이미지로 테스트
3. API 키와 모델이 정상 작동하는지 확인
4. Request 형식 비교

---

## 📋 다음 단계

### 1단계: API 직접 테스트
- [ ] 네이티브 Gemini API로 이미지 테스트
- [ ] OpenAI 호환 엔드포인트로 이미지 테스트
- [ ] 어느 엔드포인트가 작동하는지 확인

### 2단계: OpenWebUI 디버깅
- [ ] 브라우저 Network 탭에서 Request 확인
- [ ] 이미지가 올바르게 전송되는지 확인

### 3단계: 해결 방법 선택
- [ ] 네이티브 API 라우터 구현
- [ ] 또는 OpenWebUI 설정 조정
- [ ] 또는 다른 모델 시도

---

## 🔗 참고 자료

### Google Gemini API 문서
- **공식 문서**: https://ai.google.dev/gemini-api/docs
- **Vision 가이드**: https://ai.google.dev/gemini-api/docs/vision
- **API 레퍼런스**: https://ai.google.dev/api

### OpenWebUI 이슈
- OpenWebUI GitHub: https://github.com/open-webui/open-webui
- Image support 관련 이슈 검색

---

## 💻 테스트 스크립트

### Python 테스트 스크립트
```python
import requests
import base64

# 1. 네이티브 API 테스트
def test_native_gemini(api_key, image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [{
            "parts": [
                {"text": "What's in this image?"},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                }
            ]
        }]
    }

    response = requests.post(
        f"{url}?key={api_key}",
        headers=headers,
        json=payload
    )

    print("Native API Response:")
    print(response.json())

# 2. OpenAI 호환 API 테스트
def test_openai_compatible(api_key, image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gemini-2.5-flash-image-preview",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("OpenAI Compatible API Response:")
    print(response.json())

# 사용 예시
if __name__ == "__main__":
    API_KEY = "your-api-key-here"
    IMAGE_PATH = "test_image.jpg"

    print("Testing Native API...")
    test_native_gemini(API_KEY, IMAGE_PATH)

    print("\nTesting OpenAI Compatible API...")
    test_openai_compatible(API_KEY, IMAGE_PATH)
```

---

**작성자**: Claude Code
**최종 수정**: 2025-12-06
**상태**: 조사 중 - 추가 테스트 필요
