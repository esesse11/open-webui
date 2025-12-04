# ListeningMind 통합 - 빠른 시작 (5분)

> 5분 안에 ListeningMind API를 OpenWebUI에서 사용하기

---

## ✅ 체크리스트

### 1단계: API 키 확보 (1분)

- [ ] https://www.listeningmind.com 로그인
- [ ] API 키 복사 (예: `lm-abc123...`)

### 2단계: 환경 변수 설정 (2분)

**.env 파일 편집**:

```bash
# 파일 위치: C:\openwebui\source\open-webui\.env
# 파일 끝에 추가:

LISTENINGMIND_API_KEY='복사한-API-키'
LISTENINGMIND_API_BASE='https://listeningmind-mcp-api.ascentlab.io'
LISTENINGMIND_DEFAULT_GL='kr'
```

**저장 후 완료**

### 3단계: OpenWebUI 재시작 (2분)

**Windows**:

```bash
# PowerShell 실행
cd C:\openwebui\source\open-webui\backend
python -m uvicorn open_webui.main:app --reload --host 0.0.0.0 --port 8001
```

**또는 기존 방식 그대로 사용하면 됩니다**

---

## 🚀 사용하기

### UI에서 사용

```
1. OpenWebUI 웹 페이지 열기
   http://localhost:8001

2. 좌측 모델 드롭다운 클릭

3. "listeningmind-keyword" 찾기

4. 프롬프트 입력:
   냉장고, 세탁기, 에어컨

5. 엔터 또는 "Send" 클릭

6. 결과 보기:
   📊 키워드 분석 결과
   🔍 **냉장고**
   ...
```

---

## 🔧 빠른 테스트

### 연결 확인

```bash
curl http://localhost:8001/api/v1/listeningmind/models
```

### API 호출 테스트

```bash
curl -X POST "http://localhost:8001/api/v1/listeningmind/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "listeningmind-keyword",
    "messages": [{"role": "user", "content": "냉장고"}]
  }'
```

---

## ⚠️ 문제 해결

### 모델이 안 보임

```
→ 브라우저 캐시 삭제 (Ctrl + Shift + Delete)
→ 페이지 새로고침
→ 백엔드 재시작 후 2초 대기
```

### API 키 에러

```
→ .env 파일에서 LISTENINGMIND_API_KEY 확인
→ API 키 따옴표 확인
→ 백엔드 재시작
```

### 응답 없음

```
→ ListeningMind 크레딧 확인
→ 인터넷 연결 확인
→ API 서버 상태 확인
```

---

## 📚 더 알아보기

- **자세한 가이드**: `01_INTEGRATION_GUIDE.md` 읽기
- **스키마 정보**: `C:\work\project\listningmind-schema.txt` 참조
- **API 문서**: https://listeningmind-mcp-api.ascentlab.io/professional/docs

---

**완료!** 이제 OpenWebUI에서 ListeningMind API를 사용할 수 있습니다.
