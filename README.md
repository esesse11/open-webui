# AI API 사용량 분석 대시보드

Claude, OpenAI, Perplexity API 사용량을 종합적으로 분석하고 시각화하는 인터랙티브 대시보드입니다.

## 주요 기능

### 📊 1. 대시보드 개요 (Executive Summary)
- 총 누적 비용 및 전월 대비 증감률
- 일평균 비용
- 제공자별 비용 비중 (파이 차트)
- 이번 달 현황

### 📈 2. 시계열 분석 (Time Series Analysis)
- **일별 크레딧 사용량**: 비용 구간별 색상 코딩 (< $5, $5-20, ≥ $20)
- **이동평균 추이 분석**: 7일/30일 이동평균선 포함
- **월별 비용 추이**: 제공자별 누적 영역 차트
- **워터폴 차트**: 월간 비용 증감 분석 (신규)

### 🔍 3. 패턴 분석 (Pattern Analysis) - 신규
- **히트맵**: 요일별/주차별 사용 패턴 시각화
- **박스플롯**: 제공자별 비용 분포 및 이상치 탐지

### 🌳 4. 계층 분석 (Hierarchical Analysis) - 신규
- **선버스트 차트**: 제공자 > 모델 계층 구조 인터랙티브 탐색
- 드릴다운/드릴업 기능으로 상세 비용 분석

### 💰 5. 비용 예측 및 예산 관리
- **게이지 차트**: 월 예산 사용률 실시간 모니터링 (신규)
- 향후 3개월 비용 예측
- 예산 초과 경고 알림

### ⚠️ 6. 이상 탐지 및 알림 (Anomaly Detection)
- 비정상 사용 패턴 자동 감지 (Z-score 기반)
- 이상치 발생일 상세 표시

### 📊 7. 상세 통계 테이블 (Detailed Statistics)
- 월별 요약 테이블 (제공자별 비용)
- Claude 모델별 상세 분석

### 🎯 8. 인사이트 및 권장사항 (Insights & Recommendations)
- 자동 생성 인사이트
- 주요 패턴 분석 결과

## 설치 방법

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

## 사용 방법

### 방법 1: HTML 대시보드 생성 (추천)

```bash
python generate_report.py
```

이 명령은 `api_usage_dashboard.html` 파일을 생성합니다. 웹 브라우저에서 이 파일을 열어 대시보드를 확인할 수 있습니다.

### 방법 2: Streamlit 대시보드 실행

```bash
# 필요한 패키지 설치 (첫 실행 시)
pip install streamlit plotly

# 대시보드 실행
streamlit run dashboard.py
```

브라우저에서 자동으로 대시보드가 열립니다. (기본: http://localhost:8501)

### 데이터 프로세서 단독 실행

```bash
python data_processor.py
```

## 파일 구조

```
C:\work\project\
├── API_USEAGE/                  # API 사용 데이터
│   ├── claude/                 # Claude API 데이터
│   ├── openai/                 # OpenAI API 데이터
│   └── perplexity/             # Perplexity API 데이터
├── etc/                        # 참고 자료
├── data_processor.py           # 데이터 처리 모듈
├── dashboard.py                # Streamlit 대시보드
├── generate_report.py          # HTML 리포트 생성기 (추천)
├── api_usage_dashboard.html    # 생성된 HTML 대시보드
├── requirements.txt            # 필요 패키지 목록
└── README.md                  # 이 파일
```

## 데이터 형식

### Claude
- **비용 파일**: `claude_api_cost_YYYY_MM_DD_to_YYYY_MM_DD.csv`
  - 컬럼: usage_date_utc, model, token_type, cost_usd 등
- **토큰 파일**: `claude_api_tokens_YYYY_MM.csv`
  - 컬럼: usage_date_utc, model_version, usage_input_tokens_*, usage_output_tokens 등

### OpenAI
- 서비스별 파일: `{service}_usage_YYYY-MM-DD_YYYY-MM-DD.csv`
- 서비스: completions, embeddings, images, audio_speeches, audio_transcriptions, vector_stores, code_interpreter_sessions, file_searches, web_searches

### Perplexity
- PDF 인보이스: `Invoice-*.pdf`

## 주요 기능 상세

### 필터 옵션
- 날짜 범위 선택
- 제공자 선택 (Claude, OpenAI, Perplexity)

### 시각화
- 바 차트 (일별 비용, 색상 구간별)
- 라인 차트 (이동평균)
- 파이 차트 (제공자별 비중)
- 영역 차트 (월별 누적 추이)

### 분석 기능
- 월별 요약 통계
- 모델별 비용 분석
- 토큰 사용량 분석
- 이상치 탐지 (평균 대비 2σ 이상)

## 참고 이미지

대시보드는 `C:\work\project\etc` 폴더의 참고 이미지를 기반으로 디자인되었습니다:
- 일별크레딧사용량.png: 비용 구간별 바 차트
- 1인당 일별 크레딧 사용량 추이 분석.png: 이동평균선 포함 차트

## 기술 스택

- **Python**: 데이터 처리 및 분석
- **Streamlit**: 인터랙티브 웹 대시보드
- **Plotly**: 동적 차트 시각화
- **Pandas**: 데이터 처리
- **NumPy**: 수치 계산

## 라이선스

내부 사용 목적

## 차트 목록

### 기본 차트
- ✅ Bar Chart - 일별 비용 (색상 구간별)
- ✅ Line Chart - 이동평균선
- ✅ Pie/Donut Chart - 제공자별 비중
- ✅ Stacked Area Chart - 월별 누적 추이

### 고급 차트 (신규 추가)
- 🆕 **Heatmap** - 요일별 사용 패턴
- 🆕 **Sunburst** - 제공자-모델 계층 구조
- 🆕 **Box Plot** - 비용 분포 및 이상치
- 🆕 **Gauge Chart** - 예산 사용률
- 🆕 **Waterfall Chart** - 월간 증감 분석

## 업데이트 이력

- 2025-10-21: 고급 차트 5개 추가
  - 히트맵, 선버스트, 박스플롯, 게이지, 워터폴 차트 구현
  - 섹션 재구성 (8개 → 8개, 내용 확장)
  - 예산 관리 기능 강화 (인터랙티브 예산 설정)
  - 패턴 분석 섹션 신설
  - 계층 분석 섹션 신설

- 2025-10-20: 초기 버전 생성
  - Claude, OpenAI, Perplexity 데이터 통합
  - 8개 주요 섹션 구현
  - 이상 탐지 기능 추가
  - 한글 지원
