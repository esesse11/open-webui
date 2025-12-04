# ListeningMind API를 OpenWebUI에 통합하기

> ListeningMind SEO API를 OpenWebUI의 커스텀 모델로 활용하는 완벽한 가이드

**작성일**: 2025-12-04
**상태**: 구현 완료 ✓
**테스트 상태**: 준비 대기

---

## 📋 목차

1. [개요](#개요)
2. [설치 및 설정](#설치-및-설정)
3. [API 엔드포인트](#api-엔드포인트)
4. [사용 방법](#사용-방법)
5. [테스트](#테스트)
6. [문제 해결](#문제-해결)

---

## 개요

### 통합 개요

ListeningMind API는 SEO 및 키워드 분석 API이며, 이를 OpenWebUI의 텍스트 생성 모델처럼 활용하기 위해 다음과 같이 통합되었습니다:

```
사용자 입력 (프롬프트)
    ↓
자동 키워드 추출
    ↓
ListeningMind API 호출
    ↓
응답 요약 및 형식화
    ↓
OpenAI 호환 응답 형식으로 반환
```

### 주요 기능

| 기능 | 설명 |
|------|------|
| 자동 키워드 추출 | 사용자 프롬프트에서 자동으로 키워드 추출 |
| 한글 지원 | 한국어 프롬프트 완벽 지원 |
| ChatCompletion 호환 | OpenAI 표준 응답 형식 |
| 읽기 좋은 요약 | JSON 대신 마크다운 형식의 읽기 좋은 요약 |
| 실시간 API 호출 | 각 요청마다 최신 데이터 조회 |

---

## 설치 및 설정

### 1단계: API 키 준비

ListeningMind API 키를 준비해주세요:

```
1. https://www.listeningmind.com 방문
2. 계정 로그인
3. API 키 생성/확인
```

### 2단계: 환경 변수 설정

`.env` 파일을 열어 다음 정보를 설정합니다:

```bash
# C:\openwebui\source\open-webui\.env

# ListeningMind API Configuration
LISTENINGMIND_API_KEY='your-actual-api-key-here'
LISTENINGMIND_API_BASE='https://listeningmind-mcp-api.ascentlab.io'
LISTENINGMIND_DEFAULT_GL='kr'  # kr, us, jp 중 선택
```

**설정 항목**:

| 항목 | 설명 | 예시 |
|------|------|------|
| `LISTENINGMIND_API_KEY` | API 키 (필수) | `lm-abc123...` |
| `LISTENINGMIND_API_BASE` | API 베이스 URL | `https://listeningmind-mcp-api.ascentlab.io` |
| `LISTENINGMIND_DEFAULT_GL` | 기본 지역 코드 | `kr` (한국) |

### 3단계: OpenWebUI 재시작

```bash
# 백엔드 재시작 (Windows)
cd C:\openwebui\source\open-webui\backend
python -m uvicorn open_webui.main:app --reload

# 또는 Docker 사용 시
docker-compose down
docker-compose up
```

---

## API 엔드포인트

### 1. ChatCompletion 호환 (텍스트 생성 모델)

**엔드포인트**: `POST /api/v1/listeningmind/chat/completions`

**요청**:

```json
{
  "model": "listeningmind-keyword",
  "messages": [
    {
      "role": "user",
      "content": "냉장고\n세탁기\n에어컨"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**응답**:

```json
{
  "id": "listeningmind-1733289456",
  "object": "chat.completion",
  "created": 1733289456,
  "model": "listeningmind-keyword",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "📊 키워드 분석 결과\n\n🔍 **냉장고**\n  • 검색량: 356,033\n  • 경쟁도: HIGH\n  • CPC: $0.56\n  • SERP 특징: 이미지, 동영상, 관련검색\n  • 검색의도: Information(정보), Transactional(거래)\n\n💳 남은 크레딧: 99999"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 3,
    "completion_tokens": 150,
    "total_tokens": 153
  }
}
```

### 2. 모델 목록

**엔드포인트**: `GET /api/v1/listeningmind/models`

**응답**:

```json
{
  "object": "list",
  "data": [
    {
      "id": "listeningmind-keyword",
      "object": "model",
      "owned_by": "listeningmind",
      "description": "ListeningMind Keyword Research API - SEO 분석"
    }
  ]
}
```

### 3. Raw API (고급 사용자용)

**엔드포인트**: `POST /api/v1/listeningmind/raw-keyword`

원본 ListeningMind API 응답을 그대로 받을 수 있습니다 (가공 없음).

**요청**:

```json
{
  "keywords": ["냉장고", "세탁기"],
  "gl": "kr"
}
```

**응답**: ListeningMind 원본 API 응답 (JSON)

---

## 사용 방법

### OpenWebUI UI에서 사용

#### 1단계: 모델 확인

OpenWebUI 웹 UI에서:

```
1. 좌측 모델 드롭다운 클릭
2. "listeningmind-keyword" 모델 확인
```

이 모델이 보이지 않으면:
- 백엔드가 올바르게 재시작되었는지 확인
- API 키가 설정되었는지 확인 (`.env` 파일)
- 브라우저 캐시 삭제 후 새로고침

#### 2단계: 모델 선택

```
1. 모델 드롭다운에서 "listeningmind-keyword" 선택
```

#### 3단계: 프롬프트 입력

키워드를 쉼표나 개행으로 분리하여 입력:

```
냉장고, 세탁기, 에어컨
```

또는

```
냉장고
세탁기
에어컨
```

#### 4단계: 결과 보기

AI가 ListeningMind API를 호출하고 요약 결과를 반환합니다:

```
📊 키워드 분석 결과

🔍 **냉장고**
  • 검색량: 356,033
  • 경쟁도: HIGH
  • CPC: $0.56
  ...
```

### API 호출 (Python)

```python
import requests

url = "http://localhost:8001/api/v1/listeningmind/chat/completions"

payload = {
    "model": "listeningmind-keyword",
    "messages": [
        {
            "role": "user",
            "content": "냉장고\n세탁기"
        }
    ]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### API 호출 (curl)

```bash
curl -X POST "http://localhost:8001/api/v1/listeningmind/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "listeningmind-keyword",
    "messages": [
      {
        "role": "user",
        "content": "냉장고, 세탁기"
      }
    ]
  }'
```

---

## 테스트

### 1단계: 연결 테스트

```bash
curl http://localhost:8001/api/v1/listeningmind/models
```

**예상 응답**:

```json
{
  "object": "list",
  "data": [
    {
      "id": "listeningmind-keyword",
      "object": "model",
      "owned_by": "listeningmind",
      "description": "ListeningMind Keyword Research API - SEO 분석"
    }
  ]
}
```

### 2단계: API 호출 테스트

```bash
curl -X POST "http://localhost:8001/api/v1/listeningmind/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "listeningmind-keyword",
    "messages": [{"role": "user", "content": "냉장고"}]
  }'
```

### 3단계: 에러 확인

**에러**: `401 - API key not configured`

```
해결: .env 파일에서 LISTENINGMIND_API_KEY를 설정하고 백엔드 재시작
```

**에러**: `ListeningMind API error: ...`

```
해결:
1. API 키가 유효한지 확인
2. 인터넷 연결 확인
3. ListeningMind 서버 상태 확인
```

---

## 문제 해결

### Q1: 모델이 드롭다운에 나타나지 않습니다

**A**:

```
1. 백엔드 로그 확인:
   - main.py 임포트 오류 확인
   - listeningmind_api.py 경로 확인

2. 브라우저 캐시 삭제:
   - Ctrl + Shift + Delete → 캐시 삭제
   - 페이지 새로고침

3. 백엔드 재시작:
   - OpenWebUI 완전 종료 후 재시작
```

### Q2: API 호출 시 "API key not configured" 에러

**A**:

```
1. .env 파일 확인:
   - 경로: C:\openwebui\source\open-webui\.env
   - LISTENINGMIND_API_KEY 존재 확인

2. API 키 형식 확인:
   - 공백 없음
   - 따옴표 올바른지 확인

3. 백엔드 재시작:
   - 환경변수 변경 후 반드시 재시작 필요
```

### Q3: 응답이 비정상적입니다

**A**:

```
1. Raw API 테스트:
   POST /api/v1/listeningmind/raw-keyword
   - 원본 API 응답이 정상인지 확인

2. 키워드 추출 확인:
   - 프롬프트에 키워드가 포함되어 있는지 확인
   - 한글 키워드 정상 여부 확인

3. ListeningMind 크레딧:
   - API 응답의 remain_credits 확인
   - 크레딧 부족 시 충전 필요
```

---

## 파일 구조

```
C:\openwebui\source\open-webui\
├── backend\
│   ├── open_webui\
│   │   ├── main.py (수정됨 - 라우터 임포트 및 등록)
│   │   ├── routers\
│   │   │   └── listeningmind_api.py (새로 생성됨)
│   │   └── ...
│   └── .env (수정됨 - 환경변수 추가)
└── ...
```

---

## 코드 구조

### listeningmind_api.py

| 함수 | 설명 |
|------|------|
| `extract_keywords_from_prompt()` | 프롬프트에서 키워드 자동 추출 |
| `format_keyword_response_as_text()` | API 응답을 요약 텍스트로 변환 |
| `listeningmind_chat_completion()` | ChatCompletion 호환 엔드포인트 |
| `listeningmind_list_models()` | 모델 목록 반환 |
| `listeningmind_raw_keyword()` | 원본 API 응답 반환 |

### 핵심 로직

1. **프롬프트 파싱**: 쉼표, 개행으로 분리된 단어를 키워드로 추출
2. **API 호출**: ListeningMind API에 키워드 전송
3. **응답 변환**: 복잡한 JSON을 읽기 좋은 마크다운으로 변환
4. **형식화**: OpenAI ChatCompletion 표준 형식으로 반환

---

## 성능 고려사항

| 항목 | 값 |
|------|-----|
| 최대 키워드 | 100개 |
| 요청 타임아웃 | 60초 |
| 최대 응답 키워드 | 5개 (표시) |

---

## 보안

### API 키 보호

```bash
# ✅ 올바른 방법
LISTENINGMIND_API_KEY='your-actual-key'

# ❌ 위험한 방법
# 실제 API 키를 .env 파일에 평문으로 저장하지 말 것
# 프로덕션 환경에서는 환경변수나 Secret Manager 사용
```

### CORS 설정

OpenWebUI는 기본적으로 CORS를 허용합니다 (`CORS_ALLOW_ORIGIN='*'`).
프로덕션 환경에서는 특정 도메인만 허용하도록 제한하세요.

---

## 다음 단계

### 추가 개선 사항

- [ ] 모델 설정 UI에서 파라미터 조정 가능하게 개선
- [ ] 요청 결과 캐싱 추가
- [ ] 배치 처리 지원 (여러 키워드 동시 분석)
- [ ] 추가 엔드포인트 지원 (/path_finder, /google_serp 등)
- [ ] 웹훅 지원 (장시간 요청)

### 추가 API 엔드포인트

ListeningMind는 다음 엔드포인트도 지원합니다:

- `/path_finder` - 키워드 검색 경로 분석
- `/google_serp` - Google SERP 수집
- `/google_ads` - Google Ads 데이터
- `/cluster` - 키워드 관계 정보

이들 엔드포인트도 추가로 구현할 수 있습니다.

---

## 지원

문제 발생 시:

1. **로그 확인**: OpenWebUI 백엔드 로그 확인
2. **테스트**: curl로 API 직접 호출
3. **문서 확인**: 이 가이드의 문제 해결 섹션
4. **피드백**: 개선 사항 제안

---

**마지막 업데이트**: 2025-12-04
**버전**: 1.0.0
