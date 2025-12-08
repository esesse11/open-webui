# gpt-image-1 모델 분석 결과

**작성일**: 2025-12-06
**조사**: OpenWebUI 버전 비교 및 gpt-image-1 지원 현황

---

## 🔍 조사 결과

### gpt-image-1이란?

**OpenAI의 새로운 이미지 생성 모델** (2025년 3월 출시)
- **용도**: 이미지 생성 (DALL-E 후속 모델)
- **특징**: ChatGPT에서 7일 동안 7억 개 이상의 이미지 생성
- **API**: `/v1/images/generations` 엔드포인트 사용

---

## 📊 OpenWebUI 지원 현황

### 현재 develop-api 브랜치 상태

**이미 지원됨!** ✅

#### 관련 커밋
```bash
9cc00afc6 - fix: support gpt-image-1 with correct parameter (2025-05-06)
7489bc612 - fix: image model list
95610080f - allowing auto on gpt-image-1
9b2c3dec3 - Merge pull request #15220 from prilosac/allow_auto_gpt_image_1
```

#### 구현 위치
**파일**: `backend/open_webui/routers/images.py`

**주요 코드** (라인 199):
```python
if (
    form_data.IMAGE_SIZE == "auto"
    and form_data.IMAGE_GENERATION_MODEL != "gpt-image-1"
):
    raise HTTPException(
        status_code=400,
        detail=ERROR_MESSAGES.INCORRECT_FORMAT(
            "  (auto is only allowed with gpt-image-1)."
        ),
    )
```

**수정 내용** (라인 501):
```python
# gpt-image-1은 response_format을 지원하지 않음
**(
    {}
    if "gpt-image-1" in request.app.state.config.IMAGE_GENERATION_MODEL
    else {"response_format": "b64_json"}
),
```

---

## ⚠️ 오류 메시지 분석

### 받은 오류
```
This model is only supported in v1/responses and not in v1/chat/completions.
```

### 문제 원인

**잘못된 사용 방식**:
사용자가 gpt-image-1을 **채팅 모델**로 사용하려고 시도

```
❌ 잘못된 방법:
OpenWebUI 채팅창 → 모델 선택: gpt-image-1 → 메시지 입력
→ OpenAI API: POST /v1/chat/completions (gpt-image-1)
→ 오류: "only supported in v1/responses"
```

**올바른 사용 방식**:
gpt-image-1은 **이미지 생성 전용** 모델

```
✅ 올바른 방법:
OpenWebUI → Admin Panel → Settings → Images
→ Image Generation Engine: openai
→ Image Generation Model: gpt-image-1
→ 이미지 생성 기능 사용
```

---

## 🤔 오류 메시지의 의미

### "v1/responses" 언급 이유

OpenAI가 오류 메시지를 잘못 표현한 것일 수 있습니다:

1. **실제 의도**:
   ```
   "This model is only supported in v1/images/generations and not in v1/chat/completions."
   ```

2. **잘못된 메시지**:
   ```
   "This model is only supported in v1/responses and not in v1/chat/completions."
   ```

3. **가능성**:
   - OpenAI API 내부에서 "responses"를 일반적인 응답 엔드포인트로 지칭
   - 또는 gpt-image-1이 실제로 특별한 엔드포인트를 사용

---

## 🔧 해결 방법

### 방법 1: 이미지 생성 기능으로 사용 ⭐ 추천

#### 설정 위치
```
OpenWebUI → Admin Panel → Settings → Images
```

#### 설정 값
```
Image Generation Engine: openai
Image Generation Model: gpt-image-1
Image Size: auto (gpt-image-1만 지원)
```

#### 사용 방법
1. 채팅창에서 이미지 생성 버튼 클릭
2. 또는 `/generate <프롬프트>` 명령 사용
3. gpt-image-1이 이미지 생성

---

### 방법 2: 채팅 모델 목록에서 제외

gpt-image-1을 채팅 모델로 사용하지 않도록 설정:

#### Admin Panel에서
- Connections에서 gpt-image-1을 채팅 모델 목록에서 제거
- 또는 이미지 생성 전용으로만 설정

---

## 📋 다른 서버에서의 성공 사례

### 사용자 보고
> "다른 서버에서 업로드한 거는 OpenWebUI 업데이트만으로 해당 모델 정상 사용 가능"

### 분석

#### 가능성 1: 이미지 생성으로 사용
- 다른 서버에서 gpt-image-1을 **이미지 생성 모델**로 올바르게 설정
- 채팅 모델이 아닌 이미지 생성 기능으로 사용
- 따라서 정상 작동

#### 가능성 2: 최신 버전 사용
- 다른 서버가 더 최신 OpenWebUI 버전 사용
- gpt-image-1 처리 로직이 개선됨
- 자동으로 올바른 엔드포인트 사용

#### 가능성 3: 커스텀 설정
- Function 또는 Pipe 플러그인 사용
- OpenWebUI Community에서 제공하는 gpt-image-1 Function 사용:
  - https://openwebui.com/f/shayoo/gpt_image_1
  - https://openwebui.com/f/spammenot/gpt_image_1

---

## 🧪 현재 develop-api 브랜치 상태

### 확인된 내용

#### 1. gpt-image-1 지원 코드 존재
```bash
$ cd C:\openwebui\source\open-webui
$ git log --oneline --all --grep="gpt-image" -5

9b2c3dec3 Merge pull request #15220 from prilosac/allow_auto_gpt_image_1
95610080f allowing auto on gpt-image-1
7489bc612 fix: image model list
7b5247810 Merge pull request #13542 from tuzkiyoung/main
9cc00afc6 fix: support gpt-image-1 with correct parameter
```

#### 2. 커밋이 현재 브랜치에 포함됨
```bash
$ git branch --contains 9cc00afc6
* develop-api
  main
```

#### 3. images.py에 gpt-image-1 처리 로직 존재
- 라인 199: IMAGE_SIZE = "auto" 검증
- 라인 501: response_format 파라미터 제외

### 결론
**업데이트 불필요!** 현재 브랜치에 이미 gpt-image-1 지원 코드가 포함되어 있음

---

## 🚀 권장 조치

### 1단계: 사용 방식 확인

**질문**:
- gpt-image-1을 어떻게 사용하려고 했나요?
  - [ ] 채팅 모델로 선택해서 대화
  - [ ] 이미지 생성 기능 사용
  - [ ] 이미지 업로드 후 이해/분석 요청

### 2단계: 올바른 설정

#### A. 이미지 생성 용도
```
Admin Panel → Settings → Images
→ Image Generation Engine: openai
→ Image Generation Model: gpt-image-1
```

#### B. 이미지 이해 용도 (Vision)
```
채팅 모델: gpt-4-vision-preview 또는 gpt-4-turbo 사용
(gpt-image-1은 이미지 이해 불가, 생성만 가능)
```

### 3단계: 테스트

#### 이미지 생성 테스트
1. 채팅창에서 이미지 생성 버튼 클릭
2. 프롬프트 입력: "귀여운 고양이"
3. 생성 확인

---

## 📖 참고 자료

### OpenAI 공식
- **Image Generation API**: https://openai.com/index/image-generation-api/
- **Blog**: OpenAI Integrates GPT-Image-1 into its Image API (ActuIA)

### OpenWebUI Community
- **Discussion #13294**: feat: Support gpt-image-1 from OpenAI new Image gen model
  - https://github.com/open-webui/open-webui/discussions/13294
- **Issue #13180**: feat: Support gpt-image-1 from OpenAI new Image gen model
  - https://github.com/open-webui/open-webui/issues/13180
- **Function (shayoo)**: https://openwebui.com/f/shayoo/gpt_image_1
- **Function (spammenot)**: https://openwebui.com/f/spammenot/gpt_image_1

### 통계
- 7억 개 이상의 이미지가 ChatGPT에서 1주일 만에 생성됨 (2025년 3월)
- Responses API 지원 예정 (곧 출시)

---

## 💡 핵심 요약

### 문제
❌ gpt-image-1을 **채팅 모델**로 사용하려고 시도
→ 오류: "only supported in v1/responses"

### 해결
✅ gpt-image-1은 **이미지 생성 전용** 모델
→ Admin Panel → Images 설정에서 사용

### 혼동
- **이미지 생성**: gpt-image-1 (새 이미지 만들기)
- **이미지 이해**: gpt-4-vision, gemini-*-vision (이미지 설명)

---

**작성자**: Claude Code
**최종 수정**: 2025-12-06
**상태**: 분석 완료 ✅

---

## 🎯 다음 단계

올바른 사용 방법으로 다시 시도해보시겠습니까?

**옵션 A**: 이미지 생성 설정
- Admin Panel → Images 설정
- gpt-image-1 설정
- 이미지 생성 테스트

**옵션 B**: 이미지 이해 기능
- Gemini vision 모델 사용
- 또는 gpt-4-vision 사용

**옵션 C**: 추가 조사
- OpenWebUI Function 설치
- 커뮤니티 솔루션 시도
