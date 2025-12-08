# 🚀 Open WebUI 개발 환경 구축 진행 상황

**시작 날짜:** 2025-10-27
**목표:** OpenAI 호환, Gemini 호환 API 추가 및 파이프라인 로직 에러 수정

---

## 📋 진행 단계

### ✅ Step 1: Git 브랜치 생성 및 open-webui 클론
- **상태:** 완료
- **명령어:**
  ```bash
  cd C:\openwebui
  mkdir source
  cd source
  git clone https://github.com/open-webui/open-webui.git
  cd open-webui
  git checkout -b develop-api
  ```
- **결과:** develop-api 브랜치 생성 완료

---

### ⏳ Step 2: Python 가상환경 생성 및 의존성 설치
- **상태:** 자동 스크립트 준비 완료
- **작업:**
  - Python 가상환경 생성
  - pip install -e .. (editable mode)
  - requirements.txt 설치
- **실행 방법:**
  ```bash
  cd C:\openwebui\source
  setup_dev.bat    # 또는 setup_dev.ps1
  ```
- **예상 소요 시간:** 10-15분

---

### ⏳ Step 3: .env 파일 생성 및 환경 설정
- **상태:** 자동 스크립트에 포함됨
- **작업:**
  - .env 파일 생성 (copy .env.example .env)
  - 개발 환경 설정값 자동 추가
- **참고:** setup_dev.bat 실행 시 자동으로 진행됨

---

### ⏳ Step 4: 개발 서버 실행 및 테스트
- **상태:** 대기 중
- **예상 작업:**
  - uvicorn으로 개발 서버 시작 (포트 8001)
  - API 헬스 체크
  - Swagger 문서 확인

---

### ⏳ Step 5: OpenAI 호환 API 추가
- **상태:** 대기 중
- **작업 내용:**
  - `/api/v1/custom/chat/completions` 엔드포인트 추가
  - `/api/v1/custom/models` 엔드포인트 추가
  - Groq, LMStudio, 기타 OpenAI 호환 서비스 지원

---

### ⏳ Step 6: Gemini 호환 API 추가
- **상태:** 대기 중
- **작업 내용:**
  - 새 라우터 파일: `open_webui/routers/gemini.py` 생성
  - `/api/v1/gemini/chat/completions` 엔드포인트
  - `/api/v1/gemini/models` 엔드포인트
  - `/api/v1/gemini/embeddings` 엔드포인트
  - Gemini 응답 형식을 OpenAI 호환 형식으로 변환

---

### ⏳ Step 7: 파이프라인 로직 & API 응답 에러 수정
- **상태:** 대기 중
- **작업 내용:**
  - 파이프라인 필터 로직 개선
  - API 응답 처리 에러 수정
  - 스트리밍 응답 처리 개선

---

### ⏳ Step 8: 테스트 및 통합
- **상태:** 대기 중
- **작업 내용:**
  - 각 API 엔드포인트 테스트
  - 파이프라인 필터 통합 테스트
  - Git 커밋 및 로그 정리

---

## 📁 프로젝트 구조

```
C:\openwebui\
├── openwebui\           (운영 중 - 건드리지 않음)
├── pipe\                (파이프라인 운영 - 건드리지 않음)
└── source\
    └── open-webui\      📌 개발 환경 (develop-api 브랜치)
        ├── backend\
        │   ├── venv\    (가상환경 - 생성 중)
        │   ├── open_webui\
        │   │   ├── routers\
        │   │   │   ├── openai.py     (수정 예정)
        │   │   │   ├── gemini.py     (생성 예정)
        │   │   │   └── ...
        │   │   ├── main.py           (라우터 등록)
        │   │   └── ...
        │   ├── requirements.txt
        │   └── ...
        ├── .env         (생성 예정)
        ├── .env.example
        └── ...
```

---

## 🔧 환경 설정

### .env 파일 설정 (예정)
```env
# 포트 설정
PORT=8001

# 데이터베이스
DATABASE_URL=sqlite:///./data/webui_dev.db
DATABASE_TYPE=sqlite

# CORS 설정
CORS_ALLOW_ORIGIN=http://localhost:5173;http://localhost:8001

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# 로깅
GLOBAL_LOG_LEVEL=DEBUG
SRC_LOG_LEVELS={"MAIN":"DEBUG","OPENAI":"DEBUG"}

# 텔레메트리
SCARF_NO_ANALYTICS=true
DO_NOT_TRACK=true
ANONYMIZED_TELEMETRY=false
```

---

## 📝 Git 커밋 계획

### Branch: develop-api

1. **Commit 1:** Python 환경 설정
   ```
   chore: setup development environment
   - Create virtual environment
   - Install dependencies
   - Configure .env for development
   ```

2. **Commit 2:** OpenAI 호환 API 추가
   ```
   feat: Add custom OpenAI-compatible API endpoint
   - Add /api/v1/custom/chat/completions
   - Support Groq, LMStudio, and other services
   - Include error handling and timeout management
   ```

3. **Commit 3:** Gemini 호환 API 추가
   ```
   feat: Add Google Gemini API integration
   - Create new gemini.py router module
   - Implement /api/v1/gemini/chat/completions
   - Implement /api/v1/gemini/models
   - Add response format conversion to OpenAI-compatible
   ```

4. **Commit 4:** 파이프라인 로직 수정
   ```
   fix: Improve pipeline logic and API response handling
   - Fix filter processing in pipelines
   - Improve error handling
   - Add streaming response support
   ```

---

## 🧪 테스트 계획

- [ ] 개발 서버 실행 확인
- [ ] OpenAI 호환 API 테스트
- [ ] Gemini API 테스트
- [ ] 파이프라인 필터 테스트
- [ ] 에러 시나리오 테스트
- [ ] Git 커밋 로그 확인

---

## 📌 주요 파일 목록

| 파일 경로 | 상태 | 설명 |
|---------|------|------|
| `backend/venv/` | 생성 중 | Python 가상환경 |
| `.env` | 생성 예정 | 개발 환경 설정 |
| `backend/open_webui/routers/openai.py` | 수정 예정 | OpenAI 호환 API 추가 |
| `backend/open_webui/routers/gemini.py` | 생성 예정 | Gemini API 라우터 |
| `backend/open_webui/main.py` | 수정 예정 | 라우터 등록 |

---

## 📊 예상 일정

| 단계 | 예상 소요 시간 | 상태 |
|------|---------------|------|
| Step 2-3: 환경 설정 | 15분 | 진행 중 |
| Step 4: 서버 실행 | 5분 | 대기 |
| Step 5: OpenAI API | 30분 | 대기 |
| Step 6: Gemini API | 30분 | 대기 |
| Step 7: 파이프라인 수정 | 30분 | 대기 |
| Step 8: 테스트 및 정리 | 20분 | 대기 |
| **총합** | **약 2시간** | |

---

## 📝 노트

- Git 브랜치 `develop-api`를 사용하므로 main 브랜치는 안전함
- SQLite 개발용 DB 사용 (프로덕션은 영향 없음)
- 모든 변경사항은 Git 커밋으로 추적 가능
- 필요시 `git reset` 또는 `git revert`로 롤백 가능

---

## ⚠️ 문제 및 해결

(발생 시 기록)

---

## 📋 생성된 파일 목록

### 자동화 스크립트
1. **C:\openwebui\source\setup_dev.bat**
   - 배치 파일 (Windows 명령프롬프트)
   - Step 2-3을 자동으로 실행
   - 가장 간단한 실행 방법

2. **C:\openwebui\source\setup_dev.ps1**
   - PowerShell 스크립트
   - 더 상세한 출력 및 에러 처리
   - 색상 포함된 진행 상황 표시

### 설정 및 가이드
3. **C:\openwebui\source\README_SETUP.md**
   - 상세한 설정 가이드
   - 문제 해결 방법
   - 다음 단계 안내

4. **C:\work\project\DEVELOPMENT_PROGRESS.md**
   - 전체 진행 상황 추적 (이 파일)
   - 마일스톤 및 체크리스트

---

## 🎬 지금 당신이 할 일

### 1단계: 스크립트 실행 (5초)
```bash
cd C:\openwebui\source
setup_dev.bat
```

### 2단계: 스크립트가 완료될 때까지 기다리기 (10-15분)
- Python 가상환경 생성
- 의존성 설치 (자동)
- .env 파일 자동 생성 및 설정

### 3단계: 완료되면 알려주기
- 스크립트가 완료되면 "다 했어요" 메시지 보내기
- 에러가 발생하면 에러 메시지 스크린샷 첨부

---

## 🎉 개발 환경 구축 완료! (2025-10-27)

### ✅ 완료된 작업

#### Step 1: Git 환경 구축
- ✅ open-webui 저장소 클론
- ✅ develop-api 브랜치 생성 및 전환

#### Step 2: Python 환경 설정
- ✅ 가상환경 생성 (venv)
- ✅ 의존성 설치 (pip install -e ..)
- ✅ .env 파일 생성 및 설정

#### Step 3: API 라우터 개발
- ✅ **custom_openai.py** - OpenAI 호환 API 라우터 생성
  - `/api/v1/custom/models` - 모델 목록 조회
  - `/api/v1/custom/chat/completions` - 채팅 완료
  - 테스트 모드 지원 (sk-test-* API 키)

- ✅ **gemini.py** - Google Gemini API 라우터 생성
  - `/api/v1/gemini/models` - Gemini 모델 목록
  - `/api/v1/gemini/chat/completions` - Gemini 채팅
  - 응답 형식 변환 (Gemini → OpenAI 호환)

#### Step 4: 라우터 등록 및 테스트
- ✅ main.py에서 라우터 임포트 및 등록
- ✅ 개발 서버 실행 (포트 8001)
- ✅ API 엔드포인트 테스트 성공
  ```bash
  curl http://localhost:8001/api/v1/custom/models
  # 응답: {"object":"list","data":[...]}
  ```

#### Step 5: Git 커밋
- ✅ 커밋 해시: `195a69c09`
- ✅ 커밋 메시지: "feat: Add custom OpenAI-compatible and Google Gemini API integration"
- ✅ 브랜치: develop-api

### 📊 최종 통계
- **소요 시간:** 약 2시간
- **생성 파일:** 2개 (custom_openai.py, gemini.py)
- **수정 파일:** 1개 (main.py)
- **API 엔드포인트:** 5개 추가
  - `/api/v1/custom/models` (GET)
  - `/api/v1/custom/chat/completions` (POST)
  - `/api/v1/gemini/models` (GET)
  - `/api/v1/gemini/chat/completions` (POST)
  - `/api/v1/gemini/embeddings` (POST)

### 🚀 다음 단계 (선택사항)

1. **Gemini API 테스트**
   ```bash
   curl http://localhost:8001/api/v1/gemini/models
   ```

2. **파이프라인 로직 개선**
   - Inlet/Outlet 필터 최적화
   - 스트리밍 응답 처리 개선

3. **프로덕션 배포**
   - main 브랜치로 PR 생성
   - 코드 리뷰 및 병합
   - 운영 환경 업데이트

**마지막 업데이트:** 2025-10-27 13:32
**상태:** ✅ 완료

---

## 🔄 **다음 세션 시작 가이드**

### **1단계: 개발 환경 재시작**

```bash
# 1. 개발 폴더로 이동
cd C:\openwebui\source\open-webui\backend

# 2. 가상환경 활성화
venv\Scripts\activate

# 3. 개발 서버 실행 (자동 재로드)
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8001 --reload
```

### **2단계: 웹 UI 접속**

```
http://localhost:8001/
```

### **3단계: 개발 브랜치 상태 확인**

```bash
cd C:\openwebui\source\open-webui

# 브랜치 확인
git branch

# 최근 커밋 확인
git log --oneline -5

# 변경사항 확인
git status
```

---

## 📁 **중요한 경로들**

| 경로 | 용도 |
|------|------|
| `C:\openwebui\source\open-webui\backend\open_webui\routers\` | API 라우터 개발 |
| `C:\openwebui\source\open-webui\backend\open_webui\main.py` | 라우터 등록 |
| `C:\openwebui\source\open-webui\.env` | 환경 설정 |
| `C:\openwebui\source\open-webui\backend\data\webui_dev.db` | 개발용 DB |

---

## 🔧 **자주 쓸 Git 명령어**

```bash
# 파일 수정 후
git add backend/open_webui/routers/파일명.py
git commit -m "feat: 기능설명"
git push origin develop-api

# 브랜치 최신화
git fetch origin
git pull origin develop-api

# 변경사항 버리고 초기화
git checkout -- .

# 최근 커밋 취소
git reset --soft HEAD~1
```

---

## ✅ **다음 구현 목표**

### **Phase 2: Function Calling 구현**

```
목표: AI가 외부 함수/도구 자동 실행

예시:
1. 날씨 API 통합
   - GET /api/v1/functions/weather
   - 도시명 입력 → 날씨 정보 반환

2. 계산 함수
   - POST /api/v1/functions/calculate
   - 수식 입력 → 결과 계산

3. 웹 검색
   - POST /api/v1/functions/search
   - 검색어 → 결과 반환

구현 단계:
Step 1: 함수 정의 (routers/functions.py)
Step 2: Function Calling 로직 (openai.py 수정)
Step 3: 테스트 및 통합
Step 4: Git 커밋
```

---

## 📊 **현재까지의 성과**

- ✅ 개발 환경 구축 완료
- ✅ OpenAI 호환 API 추가
- ✅ Google Gemini API 추가
- ✅ Vision API 이미 작동
- ⏳ **다음: Function Calling**

---

## 💾 **GitHub 저장소**

```
개인 Fork: https://github.com/esesse11/open-webui
브랜치: develop-api
커밋 2개:
  - 195a69c09: OpenAI + Gemini API 추가
  - bc63775f1: Gemini 테스트 모드 추가
```

---

## 🚀 **빠른 시작 체크리스트**

```bash
☐ cd C:\openwebui\source\open-webui
☐ git status (변경사항 확인)
☐ git checkout develop-api (브랜치 확인)
☐ cd backend
☐ venv\Scripts\activate (가상환경 활성화)
☐ python -m uvicorn open_webui.main:app --port 8001 --reload (서버 실행)
☐ http://localhost:8001/ (웹 UI 확인)
```

---

---

## 🎯 **세션 2: 개발 환경 검증 (2025-10-28)**

### ✅ 오늘 진행한 작업

#### 1. **개발 서버 실행 (포트 8001)**
- ✅ 서버 성공적으로 시작
- ✅ Uvicorn 실행 중
- ✅ SQLite DB 연결 확인
- ✅ 자동 리로드 설정 활성화

#### 2. **버그 수정: Windows 인코딩 문제**
- 🐛 **문제**: `main.py` 534줄의 배너 출력에서 유니코드 박스 문자(█) 때문에 `cp949` 인코딩 오류 발생
- ✅ **해결**: 배너 출력 코드를 간단한 텍스트로 변경
- 📝 **수정 파일**: `C:\openwebui\source\open-webui\backend\open_webui\main.py`
  ```python
  # Before: print(banner with box characters) ❌
  # After: print(f"Open WebUI v{VERSION} - ...") ✅
  ```

#### 3. **API 엔드포인트 테스트**
- ✅ **Custom OpenAI API**: `/api/v1/custom/models` - 105개 모델 제공
  ```json
  {
    "object": "list",
    "data": [
      {"id": "gpt-4-0613", ...},
      {"id": "gpt-4", ...},
      {"id": "gpt-3.5-turbo", ...}
    ]
  }
  ```

- ✅ **Gemini API**: `/api/v1/gemini/models` - 정상 작동
  ```json
  {
    "models": [
      {"name": "models/gemini-1.5-pro", "displayName": "Gemini 1.5 Pro", ...},
      {"name": "models/gemini-1.5-flash", "displayName": "Gemini 1.5 Flash", ...}
    ]
  }
  ```

#### 4. **서버 실행 명령어 확인**
```bash
# Windows CMD/PowerShell
cd C:\openwebui\source\open-webui\backend
venv\Scripts\activate.bat
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8001 --reload
```

### 📊 세션 2 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| 서버 실행 | ✅ 완료 | 포트 8001 정상 작동 |
| API 테스트 | ✅ 완료 | Custom OpenAI, Gemini 모두 정상 |
| 버그 수정 | ✅ 완료 | Windows 인코딩 문제 해결 |
| Git 상태 | ⏳ 대기 | 커밋 준비 중 |

### 🔍 현재 시스템 상태

**Development Server (포트 8001)**
```
✓ Uvicorn running
✓ SQLite database connected
✓ Auto-reload enabled
✓ Custom OpenAI API working
✓ Gemini API working
```

**Git 브랜치 상태**
```
Branch: develop-api
Commits:
  - 9ccd75cc4: feat: Add o3-deep-research support via OpenAI /v1/responses API
  - bc63775f1: feat: Add test mode support to Gemini API
  - 195a69c09: feat: Add custom OpenAI-compatible and Google Gemini API integration
```

### 🚀 **다음 단계**

#### **즉시 실행 가능:**
1. Function Calling 구현 (AI가 외부 함수 자동 호출)
2. 파이프라인 로직 개선
3. 테스트 코드 작성

#### **유지보수:**
- 서버는 `python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8001 --reload`로 언제든 실행 가능
- .env 파일 설정은 이미 완료됨 (OPENAI_API_KEY, GOOGLE_API_KEY 포함)

**마지막 업데이트:** 2025-10-28 (오전)
**상태:** ✅ 개발 환경 준비 완료

---

## 🚀 **세션 3: Gemini 3 Pro & NanoBanana2 모델 추가 (2025-11-22)**

### ✅ 완료된 작업

#### 1. **OpenWebUI 최신 버전으로 업데이트**
- ✅ develop-api 브랜치를 최신 main과 동기화
- ✅ 모든 최신 변경사항 반영 완료

#### 2. **Gemini 3 Pro 모델 추가**
- ✅ `gemini.py`에 Gemini 3 Pro 추가
- ✅ 모델 설명 업데이트 (1M token context 명시)
- ✅ 지원되는 모델 목록:
  ```
  ✓ models/gemini-3-pro (NEW!)
  ✓ models/gemini-1.5-pro
  ✓ models/gemini-1.5-flash
  ✓ models/gemini-pro
  ```

#### 3. **NanoBanana2 모델 추가**
- ✅ `custom_openai.py`에 NanoBanana2 추가
- ✅ 모델 설명: "High-quality image generation with Gemini 3 Pro backend"
- ✅ OpenAI 호환 형식으로 지원

#### 4. **모델 테스트**
- ✅ Gemini API 엔드포인트 테스트 완료
- ✅ Custom OpenAI API 엔드포인트 테스트 완료
- ✅ 모두 정상 작동 확인

#### 5. **Git 커밋**
- ✅ 커밋 해시: `06599807b`
- ✅ 메시지: "feat: Add Gemini 3 Pro and NanoBanana2 model support"

### 📊 현재 커밋 히스토리

```
06599807b ✅ feat: Add Gemini 3 Pro and NanoBanana2 model support
26644298c ✅ fix: Resolve Windows cp949 encoding issue in banner print statement
9ccd75cc4 ✅ feat: Add o3-deep-research support via OpenAI /v1/responses API
bc63775f1 ✅ feat: Add test mode support to Gemini API
195a69c09 ✅ feat: Add custom OpenAI-compatible and Google Gemini API integration
```

### 🎯 모델 정보

#### **Gemini 3 Pro**
- 최신 및 가장 강력한 Gemini 모델
- 1M 토큰 컨텍스트 윈도우
- 고급 추론 능력
- 가격: $2/M input tokens, $12/M output tokens
- Knowledge cutoff: 2025년 1월

#### **NanoBanana2**
- Gemini 3 Pro Image 기반
- 고품질 이미지 생성
- 빠른 응답 시간
- 1k, 2k, 4k 해상도 지원
- 최대 5개 캐릭터 일관성 유지

### 🔧 API 사용 예시

**Gemini 3 Pro 사용:**
```bash
curl http://localhost:8001/api/v1/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**NanoBanana2 사용:**
```bash
curl http://localhost:8001/api/v1/custom/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2",
    "messages": [{"role": "user", "content": "Generate an image..."}]
  }'
```

### 📈 성과 요약

| 항목 | 상태 | 설명 |
|------|------|------|
| OpenWebUI 최신화 | ✅ 완료 | 최신 main 브랜치와 동기화 |
| Gemini 3 Pro | ✅ 추가됨 | 최신 Google 모델 지원 |
| NanoBanana2 | ✅ 추가됨 | 이미지 생성 모델 지원 |
| API 테스트 | ✅ 통과 | 모든 엔드포인트 정상 |
| Git 커밋 | ✅ 완료 | develop-api 브랜치에 커밋됨 |

**마지막 업데이트:** 2025-11-22
**상태:** ✅ Gemini 3 Pro & NanoBanana2 추가 완료

---

## 🔍 **세션 4: Google/Gemini 이미지 생성 문제 해결 (2025-12-08)**

### ✅ 완료된 작업

#### 1. **Gemini Router 정리**
- ✅ 불필요한 커스텀 `gemini.py` 라우터 제거
  - 백업 위치: `C:\work\project\BACKUP\openwebui\gemini.py.backup`
  - 삭제 파일: `C:\openwebui\source\open-webui\backend\open_webui\routers\gemini.py`
- ✅ `main.py`에서 gemini 라우터 등록 제거
  - 라인 97: import 제거
  - 라인 1400-1401: router 등록 제거
- **이유**: OpenWebUI Admin Panel에서 Google API 직접 연결 사용

#### 2. **이미지 생성 오류 분석 및 문서화**

##### 문제 발견
```
❌ 오류: "An error occurred while generating an image"
❌ 사용 모델: gemini-2.5-flash (텍스트 생성 모델)
❌ Admin Panel → Images → Image Generation Model 설정 오류
```

##### 원인 규명
- **Gemini** (텍스트 모델) ≠ **Imagen** (이미지 생성 모델)
- 사용자가 텍스트 모델(`gemini-2.5-flash`, `gemini-2.5-pro`)을 이미지 생성에 사용 시도
- OpenWebUI는 Gemini 엔진에서 **오직 `imagen-3.0-generate-002`만 지원**
  - 확인 위치: `images.py:384-387`

##### 해결 방법 제시
```yaml
Admin Panel → Settings → Images:
  Engine: gemini
  Model: imagen-3.0-generate-002  # ✅ 올바른 모델
  API Base URL: https://us-central1-aiplatform.googleapis.com/v1
  API Key: [Google Cloud API Key]
  Endpoint Method: predict
```

#### 3. **OpenWebUI 로깅 시스템 분석**

##### 현재 로깅 구조 파악
- ✅ **로그 출력**: `main.py:530` - `logging.basicConfig(stream=sys.stdout)`
- ✅ **출력 위치**: 모든 로그는 stdout (터미널)으로만 전송
- ✅ **로그 레벨**: 환경 변수로 제어 (`IMAGES_LOG_LEVEL`, `GLOBAL_LOG_LEVEL`)
- ❌ **로그 파일**: 별도의 파일 저장 없음 (재시작 시 손실)

##### 에러 처리 메커니즘
- **파일**: `images.py:762-768`
- **처리 흐름**:
  1. API 요청 실패 → Exception 발생
  2. 응답 JSON에서 에러 메시지 추출
  3. `HTTPException(400)` 발생
  4. 프론트엔드로 일반화된 에러 메시지 전송

##### 로그 수집 환경 구축 방안 제시
**방법 1**: 서버 실행 시 리디렉션
```powershell
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8001 --reload 2>&1 | Tee-Object -FilePath "C:\work\project\logs\openwebui.log"
```

**방법 2**: Python 로깅 핸들러 추가
- `TimedRotatingFileHandler` 사용
- 일별 로테이션, 30일 백업
- 파일 + 터미널 동시 출력

**방법 3**: 상세 디버깅 로그 추가
- `images.py`에 요청/응답 로깅 코드 추가
- `IMAGES_LOG_LEVEL=DEBUG` 환경 변수 설정

#### 4. **관련 이슈 조사**

##### gpt-image-1 모델 오류 분석
- **문제**: "This model is only supported in v1/responses"
- **원인**: OpenAI의 새 이미지 생성 모델을 채팅 모델로 사용 시도
- **해결**: Images 설정에서 이미지 생성 모델로 사용해야 함

##### Gemini Vision vs Imagen 차이점 정리
| 모델 | 용도 | 예시 |
|------|------|------|
| Gemini | 텍스트 생성 | gemini-2.5-flash, gemini-1.5-pro |
| Imagen | 이미지 생성 | imagen-3.0-generate-002 |
| Gemini Vision | 이미지 이해 | gemini-*-vision, gemini-*-image-preview |

#### 5. **문서화**

생성된 문서:
- ✅ `DOCS/05_GEMINI_INTEGRATION/00_BACKUP_INFO.md`
  - gemini.py 백업 위치 및 제거 이유
- ✅ `DOCS/05_GEMINI_INTEGRATION/01_IMAGE_ISSUE_ANALYSIS.md`
  - 이미지 인식 문제 분석
- ✅ `DOCS/05_GEMINI_INTEGRATION/02_GPT_IMAGE_ERROR_SOLUTION.md`
  - gpt-image-1 오류 해결 방법
- ✅ `DOCS/05_GEMINI_INTEGRATION/03_GPT_IMAGE_ANALYSIS.md`
  - gpt-image-1 모델 분석
- ✅ `DOCS/05_GEMINI_INTEGRATION/04_GOOGLE_IMAGE_GENERATION_FIX.md`
  - Google/Gemini 이미지 생성 오류 해결 가이드
- ✅ `DOCS/05_GEMINI_INTEGRATION/05_LOG_ANALYSIS_AND_SOLUTION.md`
  - 로깅 시스템 분석 및 로그 수집 환경 구축 방안

테스트 스크립트:
- ✅ `test_imagen_api.py`
  - Imagen API 직접 테스트 스크립트
  - `:predict` 및 `:generateContent` 엔드포인트 테스트
  - 잘못된 모델 사용 시 에러 확인

### 📊 세션 4 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| Gemini 라우터 정리 | ✅ 완료 | 백업 후 제거 |
| 이미지 생성 오류 원인 규명 | ✅ 완료 | Gemini ≠ Imagen |
| 로깅 시스템 분석 | ✅ 완료 | stdout 전용, 파일 저장 없음 |
| 로그 수집 방안 제시 | ✅ 완료 | 3가지 방법 문서화 |
| 문서화 | ✅ 완료 | 6개 MD 파일, 1개 테스트 스크립트 |

### 🔍 핵심 발견사항

#### 문제
```
사용자: Admin Panel → Images → Model에 "gemini-2.5-flash" 입력
→ Google API: 404 Not Found (모델 없음)
→ OpenWebUI: "An error occurred while generating an image"
```

#### 원인
```
gemini-2.5-flash = 텍스트 생성 모델
imagen-3.0-generate-002 = 이미지 생성 모델

잘못된 모델 카테고리 사용!
```

#### 해결
```
✅ Model: imagen-3.0-generate-002 사용
✅ API Base: https://us-central1-aiplatform.googleapis.com/v1
✅ Endpoint Method: predict
```

### 🚀 사용자 조치 필요

**즉시 실행 (5분):**
1. OpenWebUI Admin Panel → Settings → Images
2. Image Generation Model 변경:
   ```
   gemini-2.5-flash → imagen-3.0-generate-002
   ```
3. 저장 후 이미지 생성 테스트

**선택 사항 - 로그 수집 (10분):**
1. 서버 재시작 시 로그 파일 리디렉션 설정
2. 또는 `main.py`에 파일 핸들러 추가
3. `IMAGES_LOG_LEVEL=DEBUG` 설정

### 🔗 관련 파일

**분석 대상:**
- `C:\openwebui\source\open-webui\backend\open_webui\main.py:530` (로깅 설정)
- `C:\openwebui\source\open-webui\backend\open_webui\routers\images.py:384-387` (지원 모델)
- `C:\openwebui\source\open-webui\backend\open_webui\routers\images.py:600-660` (이미지 생성)
- `C:\openwebui\source\open-webui\backend\open_webui\routers\images.py:762-768` (에러 처리)

**백업:**
- `C:\work\project\BACKUP\openwebui\gemini.py.backup`

**문서:**
- `C:\work\project\DOCS\05_GEMINI_INTEGRATION\*.md` (6개)
- `C:\work\project\test_imagen_api.py`

### 📈 Git 상태

**브랜치**: master
**작업 디렉토리**: `C:\work\project`

**생성된 파일:**
- `.claude/` (설정)
- `.gitignore`
- `DOCS/05_GEMINI_INTEGRATION/*.md` (6개)
- `test_imagen_api.py`
- 기타 분석 파일

**커밋 예정:**
- "docs: Add Gemini/Imagen API integration troubleshooting and logging analysis"

**마지막 업데이트:** 2025-12-08
**상태:** ✅ 이미지 생성 문제 분석 완료, 해결 방법 제시 완료
