# OpenWebUI Gemini & Custom API Integration

> OpenWebUI에 Gemini API와 Custom OpenAI API를 통합하고 API 파라미터를 개선한 프로젝트

**상태**: Session 4 완료 ✓ / Session 5 준비 중 / **ListeningMind 통합 진행 중** 🚀
**최종 업데이트**: 2025-12-04

---

## 📁 문서 구조

```
DOCS/
├── README.md                                    ← 지금 읽는 파일
├── 01_API_Implementation/                       ← API 구현 관련 (Session 4)
│   ├── 00_SESSION4_ENHANCEMENT_HISTORY.md
│   ├── 01_API_STRUCTURE_GUIDE.md
│   ├── 02_IMPLEMENTATION_DETAILS.md
│   └── 03_TESTING_GUIDE.md
├── 02_Setup_Guide/                              ← 다음 단계 설정 가이드 (Session 5)
│   └── 01_GOOGLE_API_SETUP_TODO.md
├── 03_Reference/                                ← 빠른 참조
│   └── 01_QUICK_REFERENCE.md
└── 04_LISTENINGMIND_INTEGRATION/                ← ListeningMind API 통합 🆕
    ├── 00_PROJECT_STATUS.md                     ← 현재 프로젝트 상태
    ├── 01_INTEGRATION_GUIDE.md                  ← 상세 통합 가이드
    ├── 02_QUICK_START.md                        ← 5분 빠른 시작
    └── 03_IMPLEMENTATION_DETAILS.md             ← 기술 상세
```

---

## 🚀 빠른 시작

### Session 4 - API 개선 (완료 ✓)
✓ Gemini API에 `top_p`, `top_k`, `system_prompt` 파라미터 추가
✓ Custom OpenAI API에 OpenAI 호환 파라미터 추가
✓ 양쪽 API 에러 처리 개선
✓ Git commit & push 완료

**관련 문서**:
- `01_API_Implementation/00_SESSION4_ENHANCEMENT_HISTORY.md` - 작업 배경 및 교훈
- `01_API_Implementation/02_IMPLEMENTATION_DETAILS.md` - 변경 사항 상세
- `03_Reference/01_QUICK_REFERENCE.md` - 5분 요약

### Session 5 - Google API 등록 (다음 작업)
다음 할 일: Google API 등록 후 Gemini 3 Pro 및 NanoBanana2 모델 추가

**관련 문서**:
- `02_Setup_Guide/01_GOOGLE_API_SETUP_TODO.md` - 단계별 설정 가이드

### 🆕 ListeningMind API 통합 (현재 진행 중)
ListeningMind SEO API를 OpenWebUI에 커스텀 모델로 통합

**상태**:
- ✅ 백엔드 코드 구현 완료
- ✅ API 엔드포인트 테스트 완료 (curl로 확인)
- ⏳ UI 표시 문제 해결 중 (캐시 문제로 추정)

**관련 문서**:
- `04_LISTENINGMIND_INTEGRATION/00_PROJECT_STATUS.md` - 프로젝트 현황 ⭐ **여기서 시작**
- `04_LISTENINGMIND_INTEGRATION/01_INTEGRATION_GUIDE.md` - 상세 가이드
- `04_LISTENINGMIND_INTEGRATION/02_QUICK_START.md` - 5분 빠른 시작
- `04_LISTENINGMIND_INTEGRATION/03_IMPLEMENTATION_DETAILS.md` - 기술 상세

---

## 📚 문서 선택 가이드

| 상황 | 문서 | 소요 시간 |
|------|------|---------|
| 빠르게 변경 내용 알고 싶음 | `03_Reference/01_QUICK_REFERENCE.md` | 5분 |
| API 구조 완벽히 이해 | `01_API_Implementation/01_API_STRUCTURE_GUIDE.md` | 15분 |
| 테스트 방법 알고 싶음 | `01_API_Implementation/03_TESTING_GUIDE.md` | 10분 |
| 정확한 코드 변경 보고 싶음 | `01_API_Implementation/02_IMPLEMENTATION_DETAILS.md` | 20분 |
| 실패 이유와 교훈 알고 싶음 | `01_API_Implementation/00_SESSION4_ENHANCEMENT_HISTORY.md` | 10분 |
| 다음 단계 어떻게? | `02_Setup_Guide/01_GOOGLE_API_SETUP_TODO.md` | 55분 실행 |
| ListeningMind 통합 상황? | `04_LISTENINGMIND_INTEGRATION/00_PROJECT_STATUS.md` | 10분 |
| ListeningMind 사용하려면? | `04_LISTENINGMIND_INTEGRATION/02_QUICK_START.md` | 5분 |

---

## 📖 권장 읽기 순서

### 🔍 현재 상황 파악 (30분)
1. 이 README 읽기 (현재)
2. `03_Reference/01_QUICK_REFERENCE.md` - "한눈에 보기" 섹션
3. `01_API_Implementation/00_SESSION4_ENHANCEMENT_HISTORY.md` - 배경 이해

### 📐 상세 학습 (45분)
1. `01_API_Implementation/01_API_STRUCTURE_GUIDE.md` - API 구조 이해
2. `01_API_Implementation/02_IMPLEMENTATION_DETAILS.md` - 변경 사항 상세
3. `01_API_Implementation/03_TESTING_GUIDE.md` - 테스트 방법

### 🎯 다음 작업 (55분 실행)
1. `02_Setup_Guide/01_GOOGLE_API_SETUP_TODO.md` 읽고 따라하기

---

## ✨ Session 4 주요 성과

### 구현된 기능
- **Gemini API 개선**
  - `top_p`: Nucleus sampling 파라미터
  - `top_k`: Top-K sampling 파라미터
  - `system_prompt`: 시스템 프롬프트 지원

- **Custom OpenAI API 개선**
  - `top_p`, `top_k`: 샘플링 파라미터
  - `frequency_penalty`, `presence_penalty`: 텍스트 다양성 제어
  - `stop`: 생성 중단 시퀀스
  - None 필드 자동 제외로 API 호환성 향상

- **에러 처리 개선**
  - 구조화된 에러 응답 (status, message, model, endpoint)
  - 더 자세한 로깅

### 코드 변경
- 총 **63줄 추가, 10줄 제거**
- 2개 파일 수정 (gemini.py, custom_openai.py)
- **Python 문법 검증 통과** ✓

### 문서 생성
- 7개의 상세 문서 (~75KB, 2,354줄)
- 30+ 코드 예제
- 15+ 테스트 예시

---

## 🔗 핵심 파일 위치

### 구현 코드
```
C:\openwebui\source\open-webui\
backend\open_webui\routers\
├── gemini.py               (수정됨 ✓)
│   ├── 라인 23-31: 요청 모델 확장
│   ├── 라인 75-96: Payload 생성 로직
│   └── 라인 109-118: 에러 처리
└── custom_openai.py        (수정됨 ✓)
    ├── 라인 20-30: 요청 모델 확장
    ├── 라인 53-75: Payload 생성 로직
    └── 라인 85-95: 에러 처리
```

### Git Commit
```
커밋 해시: 0caf5427a
브랜치: develop-api
메시지: feat: Enhance Gemini and Custom OpenAI API with advanced parameters
```

---

## 🎯 다음 단계 (Session 5)

### Phase 1: Google API 설정 (5분)
- Google Cloud API Key 준비
- OpenWebUI Settings > Connections에서 등록

### Phase 2: NanoBanana2 모델 설정 (10분)
- API 정보 확인
- 필요시 커스텀 모델로 추가

### Phase 3: 모델 테스트 (15분)
- curl/Python으로 새 파라미터 테스트
- Gemini 3 Pro, NanoBanana2 동작 확인

### Phase 4: 웹 UI 테스트 (15분)
- 모델 드롭다운에서 선택 가능 확인
- 실제 채팅으로 기능 검증

### Phase 5: 문서 업데이트 (10분)
- 완료 내용 기록
- 최종 보고서 작성

**총 예상 소요 시간: 55분**

상세 가이드: `02_Setup_Guide/01_GOOGLE_API_SETUP_TODO.md`

---

## 📊 통계

| 항목 | 수치 |
|------|------|
| 생성 문서 | 7개 |
| 총 라인 수 | 2,354 라인 |
| 총 크기 | ~75 KB |
| 테스트 예제 | 30+ 개 |
| 코드 변경 | +63, -10 라인 |
| Git 커밋 | 1개 |

---

## 🔑 핵심 개념

### OpenWebUI의 모델 관리 2가지 방식
1. **API 연결 방식** (Settings > Connections)
   - Google Gemini, OpenAI 등 API 제공자 연결
   - 자동으로 모든 모델 추가
   - 동적 갱신

2. **커스텀 모델 방식** (Settings > Models)
   - 기본 모델에 정보 추가/커스터마이징
   - DB 기반 저장
   - 수동 추가/삭제

### Session 4의 교훈
❌ DB에 모델 추가 → UI와 미연결
❌ API 라우터만 생성 → 엔드포인트만 추가
✅ Settings > Connections 사용 → 올바른 방법 (Session 5)

---

## 💡 문서 사용 팁

- **처음 접하는 경우**: 이 README → QUICK_REFERENCE → SESSION4_HISTORY 순서로
- **구체적 코드 확인**: IMPLEMENTATION_DETAILS에서 diff 형식 코드 비교
- **테스트 실행**: TESTING_GUIDE의 curl/Python 예제 직접 실행
- **다음 단계**: GOOGLE_API_SETUP_TODO를 체크박스로 하나씩 진행

---

## ❓ FAQ

**Q: 어떤 문서부터 읽어야 하나요?**
A: 시간이 없으면 QUICK_REFERENCE, 완벽히 이해하려면 이 README → SESSION4_HISTORY → STRUCTURE_GUIDE 순서

**Q: 코드는 어디에 있나요?**
A: `C:\openwebui\source\open-webui\backend\open_webui\routers\` 폴더의 `gemini.py`와 `custom_openai.py`

**Q: 테스트는 어떻게 하나요?**
A: TESTING_GUIDE의 curl 또는 Python 예제를 실행하세요

**Q: 언제 Google API를 연결하나요?**
A: GOOGLE_API_SETUP_TODO를 따라 (예상 55분 소요)

---

**프로젝트 저장소**: https://github.com/esesse11/open-webui (develop-api 브랜치)
**마지막 업데이트**: 2025-11-22
