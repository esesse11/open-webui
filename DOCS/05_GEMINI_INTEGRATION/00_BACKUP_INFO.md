# Gemini 라우터 백업 정보

**작성일**: 2025-12-06
**작업**: Gemini 라우터 제거 및 백업

---

## 📋 작업 내역

### 제거 이유
- OpenWebUI 관리자 페이지에서 Google Gemini API를 직접 연결
- 커스텀 gemini.py 라우터가 더 이상 필요하지 않음
- Google API의 OpenAI 호환 엔드포인트 사용: `https://generativelanguage.googleapis.com/v1beta/openai`

### 백업 파일 위치
```
C:\work\project\BACKUP\openwebui\gemini.py.backup
```

**파일 크기**: 8,193 bytes
**백업 일시**: 2025-12-06

---

## 🗑️ 제거된 파일

### 1. gemini.py 라우터
**원본 위치**: `C:\openwebui\source\open-webui\backend\open_webui\routers\gemini.py`

**기능**:
- Google Gemini API 통합
- ChatCompletion 호환 엔드포인트 (`/api/v1/gemini/chat/completions`)
- 모델 목록 엔드포인트 (`/api/v1/gemini/models`)
- 테스트 모드 지원

**제공했던 모델** (테스트 모드):
1. `models/gemini-3-pro` - Gemini 3 Pro
2. `models/gemini-3-pro-image-preview` - Gemini 3 Pro Image (Preview)
3. `models/gemini-2.5-flash-image` - Gemini 2.5 Flash Image
4. `models/gemini-2.5-flash-image-preview` - Gemini 2.5 Flash Image (Preview)
5. `models/gemini-1.5-pro` - Gemini 1.5 Pro
6. `models/gemini-1.5-flash` - Gemini 1.5 Flash
7. `models/gemini-pro` - Gemini Pro

### 2. main.py 수정 내역

**제거된 import** (라인 97):
```python
# Before
    custom_openai,
    gemini,              # 제거됨
    listeningmind_api,

# After
    custom_openai,
    listeningmind_api,
```

**제거된 라우터 등록** (라인 1400-1401):
```python
# Before
app.include_router(custom_openai.router)

# Google Gemini API
app.include_router(gemini.router)    # 제거됨

# ListeningMind SEO API
app.include_router(listeningmind_api.router)

# After
app.include_router(custom_openai.router)

# ListeningMind SEO API
app.include_router(listeningmind_api.router)
```

---

## 🔄 현재 Gemini API 연결 방식

### OpenWebUI 관리자 페이지 설정
- **위치**: Admin Panel → Settings → Connections
- **API Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai`
- **API Key**: Google Cloud Console에서 발급받은 실제 키
- **모델**: Google에서 제공하는 모든 Gemini 모델 자동 로드

### 장점
✅ Google의 최신 모델 자동 업데이트
✅ 실제 AI 응답 (테스트 모드 아님)
✅ 멀티모달 지원 (텍스트 + 이미지)
✅ 별도 커스텀 라우터 유지보수 불필요

---

## 🔧 복구 방법 (필요시)

만약 커스텀 gemini.py 라우터가 다시 필요한 경우:

### 1. 파일 복구
```bash
cp C:\work\project\BACKUP\openwebui\gemini.py.backup C:\openwebui\source\open-webui\backend\open_webui\routers\gemini.py
```

### 2. main.py 수정
**import 추가** (라인 97):
```python
    custom_openai,
    gemini,              # 추가
    listeningmind_api,
```

**라우터 등록 추가** (라인 1400):
```python
app.include_router(custom_openai.router)

# Google Gemini API
app.include_router(gemini.router)    # 추가

# ListeningMind SEO API
app.include_router(listeningmind_api.router)
```

### 3. 서버 재시작
```bash
# 서버 재시작 필요 (--reload 모드라면 자동)
```

---

## 📊 관련 문서

- **ListeningMind 통합**: `DOCS/04_LISTENINGMIND_INTEGRATION/00_PROJECT_STATUS.md`
- **현재 프로젝트 상태**: `DOCS/README.md`

---

## ⚠️ 주의사항

### 이미지 인식 문제
**현재 상태** (2025-12-06):
- ✅ 텍스트 프롬프트: 정상 작동
- ❌ 이미지 프롬프트: 텍스트로만 응답, 이미지 인식 안 됨

**원인 조사 필요**:
- OpenWebUI의 이미지 전송 방식 확인
- Gemini API의 이미지 입력 형식 확인
- 디버깅 필요

---

**작성자**: Claude Code
**최종 수정**: 2025-12-06
