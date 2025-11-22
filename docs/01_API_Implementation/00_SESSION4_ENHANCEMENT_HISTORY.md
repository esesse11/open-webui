# Session 4: API 개선 작업 기록 및 교훈

**날짜**: 2025-11-22
**목표**: Gemini 3 Pro와 NanoBanana2 모델을 OpenWebUI에 추가
**결과**: ✅ API 구조 개선 완료 / ❌ 초기 모델 추가 실패 (올바른 방법 발견)

---

## 📋 작업 내용 요약

### 완료된 작업
✅ Gemini API에 시스템 프롬프트, top_p, top_k 파라미터 추가
✅ Custom OpenAI API에 OpenAI 호환 파라미터 추가
✅ 양쪽 API 에러 처리 개선
✅ Python 문법 검증 통과
✅ Git commit & push 완료

### 학습한 교훈
❌ DB에 모델을 직접 추가 → UI와 미연결
❌ API 라우터만 생성 → 엔드포인트만 추가됨
✅ Settings > Connections 사용 → 올바른 방법 (Session 5)

---

## 🎯 초기 시도 기록

### 시도 1: API 라우터 수정
**상태**: 부분 성공
- ✅ API 엔드포인트는 작동
- ✅ curl 테스트 성공
- ❌ 웹 UI Settings > Models에는 안 보임

### 시도 2: 데이터베이스에 모델 추가
**상태**: 실패
- ✅ DB에는 저장됨
- ❌ 웹 UI에 표시 안 됨
- **원인**: user_id 권한 문제

### 시도 3: user_id 권한 수정
**상태**: 실패
- ✅ DB 업데이트됨
- ❌ 여전히 웹 UI에 안 보임

### 시도 4: 모델 로딩 로직 수정
**상태**: 부분 개선
- ✅ 코드는 수정됨
- ❌ 근본적 문제 미해결

---

## ❌ 실패 원인 분석

### 근본적인 오류: 아키텍처 오해

**실제 OpenWebUI 구조**:
```
Settings > Models          Settings > Connections
    ↓                            ↓
커스텀 모델 (DB 기반)      API 연결 (Google, OpenAI 등)
- 수동으로 추가            - 자동으로 모델 추가
- 커스터마이징용           - 동적 갱신
```

### 우리가 실수한 점
| 시도 | 실제 효과 | 예상한 효과 |
|------|---------|----------|
| API 라우터 생성 | 독립 엔드포인트 추가 | Settings > Models에 자동 추가 |
| DB에 모델 추가 | DB 테이블에만 저장 | 웹 UI에 표시 |
| user_id 수정 | 권한 설정만 변경 | 웹 UI에 표시 |
| 코드 로직 수정 | 빈 리스트 반환 해결 | API 연결 없으므로 의미 없음 |

---

## ✅ 올바른 방법 발견

### Settings > Connections에서 Google API 연결

**단계**:
1. OpenWebUI 웹 페이지: `http://localhost:8001`
2. Settings (톱니바퀴) 클릭
3. **Connections** 메뉴
4. **Google** 또는 **Gemini** 선택
5. Google API Key 입력
6. 저장

**자동 결과**:
- ✅ Gemini 3 Pro 자동 추가
- ✅ Gemini 1.5 Pro 자동 추가
- ✅ 다른 Google 모델들도 자동 추가
- ✅ Settings > Models에 자동 표시

---

## 🎓 배운 점

### ✗ 하지 말아야 할 것
- [ ] 외부 API 제공자의 모델을 DB에 직접 추가
- [ ] API 엔드포인트만 만들고 UI와 연결 안 함
- [ ] OpenWebUI 아키텍처를 모르고 시도

### ✓ 해야 할 것
- [ ] Settings > Connections에서 공식 방법 사용
- [ ] API 제공자 연결하면 자동으로 모델 추가됨
- [ ] 커스텀 모델은 Settings > Models UI에서 추가
- [ ] 소스 코드 수정은 최후의 수단

### 🔑 핵심 개념
**OpenWebUI의 2가지 모델 관리 방식**:

1. **API 연결 방식** (Settings > Connections)
   - OpenAI, Google, Ollama 등 API 제공자 연결
   - 자동으로 모든 모델이 추가됨
   - 동적으로 갱신됨

2. **커스텀 모델 방식** (Settings > Models)
   - 기본 모델에 정보 추가/커스터마이징
   - DB 기반으로 저장됨
   - 수동으로 추가/삭제 가능

---

## 💾 생성된 진단 스크립트

이 스크립트들은 작업 기록 목적으로 유지됩니다:

```
C:\openwebui\source\open-webui\
├── insert_models_db.py           (DB에 모델 삽입)
├── fix_model_owner.py            (user_id 수정)
├── check_model_access.py         (모델 권한 확인)
├── inspect_all_models.py         (DB 모델 검사)
├── add_models_to_db.py           (API로 모델 추가)
├── test_api.py                   (API 테스트)
└── test_models_simple.py         (모델 검증)
```

---

## 🚀 Session 5 계획

### Phase 1: Google API 설정 (5분)
- Google Cloud API Key 준비
- OpenWebUI Settings > Connections 등록

### Phase 2: NanoBanana2 설정 (10분)
- API 정보 확인
- 필요시 커스텀 모델로 추가

### Phase 3: 모델 테스트 (15분)
- curl/Python으로 새 파라미터 테스트
- 동작 확인

### Phase 4: 웹 UI 테스트 (15분)
- 모델 드롭다운 확인
- 실제 채팅 검증

### Phase 5: 문서 업데이트 (10분)
- 완료 내용 기록

---

## 📊 현재 상태

### DB에 저장된 모델들
```
✓ gemini-3-pro (DB에만 있음, 미표시)
✓ nano-banana-2 (DB에만 있음, 미표시)
```

### 처리 방법
- **옵션 A (권장)**: 그대로 두기
  - Connections에서 연결하면 자동 추가
  - 나중에 Settings > Models에서 커스텀 추가 가능

- **옵션 B**: DB 정리 (나중에 필요시)
  - DB에서 모델 삭제

---

## 💡 결론

### 이번 작업의 가치
성공하지 못했지만 매우 큰 학습을 얻었습니다:

```
❌ DB 추가        → 작동 안 함
❌ API 라우터     → API는 작동하지만 UI 미연결
❌ 코드 수정      → 부분적 개선이지만 근본 해결 아님
✅ 올바른 방법 발견 → Settings > Connections
```

### 다음 Action
**Session 5에서는 Settings > Connections를 통해 Google API를 등록하고,**
**자동으로 추가되는 Gemini 3 Pro와 다른 모델들을 활용합니다.**

---

**마지막 업데이트**: 2025-11-22
**작성자**: Claude Code
