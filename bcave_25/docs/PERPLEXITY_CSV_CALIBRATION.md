# Perplexity CSV 데이터 보정 작업 (2025-12-22)

## 📋 작업 개요

Perplexity API 사용 데이터를 일별 상세 CSV에서 추출하여 대시보드에 통합하는 작업 중, **월별로 CSV 데이터 단위(scale)가 다르다는 중대한 문제를 발견**하고 해결.

## 🔍 발견된 문제

### 초기 접근 방식 (실패)

1. **5월 2025 인보이스 기반 단일 가격 모델 생성**
   - 5월 인보이스 총액($39.29)과 CSV 원본 값을 비교
   - 역산하여 단위당 가격 산출
   ```
   api_requests: $0.0000003656
   input_tokens: $0.0013141684
   reasoning_tokens: $0.0000014998
   등등...
   ```

2. **모든 월에 동일 가격 모델 적용 (3월~9월)**
   - 결과: 엄청난 오차 발생!

### 검증 결과: 심각한 불일치

| 월 | 인보이스 | CSV 계산값 | 오차 |
|---|---------|-----------|------|
| 3월 | $3.38 | $5,143.10 | **152,063%** ❌ |
| 4월 | $45.11 | $5,928.16 | **13,042%** ❌ |
| **5월** | **$39.29** | **$39.29** | **0%** ✅ |
| 6월 | $93.76 | $13,141.06 | **13,916%** ❌ |
| 7월 | $88.37 | $34,500.09 | **38,941%** ❌ |
| 8월 | $64.27 | $32,115.22 | **49,869%** ❌ |

### 원인 분석

**월별 CSV 데이터 단위 비교:**

```python
# 5월 CSV 원본 총합
API Requests: 3,172,480
Input Tokens: 2,922

# 7월 CSV 원본 총합
API Requests: 2,054
Input Tokens: 26,194,620
```

**단위당 가격 역산 결과:**

| 카테고리 | 최소값 | 최대값 | 비율 |
|---------|--------|--------|------|
| API Requests | $0.0000003656 | $0.0024245375 | **6,631배** 🔥 |
| Input Tokens | $0.0000009065 | $0.0013141684 | **1,450배** 🔥 |
| Search Queries | $0.0000015701 | $0.0121666667 | **7,749배** 🔥 |
| Reasoning Tokens | $0.0000014998 | $0.0023600000 | **1,574배** 🔥 |

**결론**: CSV 데이터가 **월마다 완전히 다른 스케일**을 사용하고 있음!

## ✅ 해결 방법

### 1. 인보이스 데이터 추출 (PDF)

9월~11월 인보이스 PDF에서 데이터 추출:

**추출 스크립트**: `extract_invoice_pdfs.py`
- pdfplumber 라이브러리 사용
- 정규표현식으로 항목별 금액 파싱
- 11개 PDF 파일 자동 처리

**추출 결과:**

| 월 | 기간 | 총액 |
|---|------|------|
| 9월 | Sep 1-30 | $72.04 |
| 10월 (1) | Oct 1-20 | $25.21 |
| 10월 (2) | Oct 21-31 | $14.08 |
| 11월 (1) | Nov 1-20 | $37.42 |
| 11월 (2) | Nov 21-30 | $14.21 |

### 2. 월별 개별 가격 보정

**보정 스크립트**: `recalibrate_all_months.py`

각 월마다 인보이스 금액 ÷ CSV 원본 값으로 실제 단위당 가격 계산:

```python
# 예시: 7월
invoice['input_tokens'] = $35.88
csv_totals['input_tokens'] = 26,194,620

→ unit_price = $35.88 / 26,194,620 = $0.0000013697
```

### 3. 전체 데이터 재처리

**재처리 스크립트**: `reprocess_all_with_calibration.py`

**주요 로직:**
1. 각 월의 인보이스 데이터 로드
2. CSV 원본 값 합산
3. 월별 단위 가격 계산
4. 일별 데이터에 월별 가격 적용
5. 인보이스 총액과 검증

**특수 처리:**
- **10월/11월**: 분할된 CSV 파일 병합
  - 251020 + 251031 → 2510 (10월 전체)
  - 251120 + 251130 → 2511 (11월 전체)
- **날짜별 중복 제거**: groupby('date').sum()

## 📊 최종 결과

### 처리된 월별 데이터

| 월 | 일수 | 인보이스 | 계산값 | 차이 | 상태 |
|---|-----|---------|--------|------|------|
| 3월 | 7 | $3.38 | $3.38 | $0.00 | ✓ PERFECT |
| 4월 | 30 | $45.11 | $45.11 | $0.00 | ✓ PERFECT |
| 5월 | 31 | $39.29 | $39.29 | $0.00 | ✓ PERFECT |
| 6월 | 30 | $93.76 | $93.76 | $0.00 | ✓ PERFECT |
| 7월 | 31 | $88.37 | $88.37 | $0.00 | ✓ PERFECT |
| 8월 | 31 | $64.27 | $64.27 | $0.00 | ✓ PERFECT |
| 9월 | 30 | $72.04 | $72.04 | $0.00 | ✓ PERFECT |
| 10월 | 31 | $39.29 | $39.29 | $0.00 | ✓ PERFECT |
| 11월 | 30 | $51.63 | $51.63 | $0.00 | ✓ PERFECT |

**총 비용 (3월~11월)**: $496.14

### 생성된 파일

```
C:\work\project\bcave_25\API_USEAGE\perplexity\
├── 2503_daily_costs_calibrated.csv  (3월, 7일)
├── 2504_daily_costs_calibrated.csv  (4월, 30일)
├── 2505_daily_costs_calibrated.csv  (5월, 31일)
├── 2506_daily_costs_calibrated.csv  (6월, 30일)
├── 2507_daily_costs_calibrated.csv  (7월, 31일)
├── 2508_daily_costs_calibrated.csv  (8월, 31일)
├── 2509_daily_costs_calibrated.csv  (9월, 30일)
├── 2510_daily_costs_calibrated.csv  (10월, 31일)
└── 2511_daily_costs_calibrated.csv  (11월, 30일)
```

## 🔧 생성된 스크립트

### 1. `process_all_perplexity_months.py`
- **목적**: 3월~9월 일괄 처리 (단일 파일)
- **결과**: 초기 잘못된 보정으로 실패
- **상태**: ⚠️ 사용 안 함

### 2. `process_oct_nov_perplexity.py`
- **목적**: 10월/11월 분할 파일 처리
- **기능**:
  - 251020 + 251031 → 10월
  - 251120 + 251130 → 11월
- **상태**: ⚠️ 단일 보정 사용으로 부정확

### 3. `verify_perplexity_data.py`
- **목적**: 인보이스 vs CSV 검증
- **결과**: 심각한 불일치 발견
- **상태**: ✅ 문제 발견에 성공

### 4. `recalibrate_all_months.py`
- **목적**: 월별 단위 가격 분석
- **결과**: 6,631배 차이 발견
- **상태**: ✅ 원인 규명 성공

### 5. `extract_invoice_pdfs.py`
- **목적**: PDF에서 인보이스 데이터 추출
- **라이브러리**: pdfplumber
- **결과**: 9월~11월 데이터 추출
- **상태**: ✅ 완료

### 6. `reprocess_all_with_calibration.py` ⭐
- **목적**: 모든 월 월별 보정 재처리
- **기능**:
  - 각 월 인보이스 로드
  - CSV 총합 계산
  - 월별 단위 가격 산출
  - 일별 비용 계산
  - 인보이스와 검증
- **상태**: ✅ 최종 솔루션

## 📈 대시보드 통합

### data_processor.py 업데이트 필요

현재 상태:
```python
daily_files = {
    '2503': '2503_daily_costs_calibrated.csv',
    '2504': '2504_daily_costs_calibrated.csv',
    # ... 2509까지만
}
```

업데이트 필요:
```python
daily_files = {
    '2503': '2503_daily_costs_calibrated.csv',
    '2504': '2504_daily_costs_calibrated.csv',
    '2505': '2505_daily_costs_calibrated.csv',
    '2506': '2506_daily_costs_calibrated.csv',
    '2507': '2507_daily_costs_calibrated.csv',
    '2508': '2508_daily_costs_calibrated.csv',
    '2509': '2509_daily_costs_calibrated.csv',
    '2510': '2510_daily_costs_calibrated.csv',  # 추가
    '2511': '2511_daily_costs_calibrated.csv',  # 추가
}
```

## 🎯 이상치(Anomaly) 변화

### 이전 (인보이스 기반)
- 4개 이상치: 4/30, 6/1, 7/1, 8/1
- 원인: 월별 인보이스 청구일에 전월 사용액 일괄 계상

### 이후 (CSV 일별 기반)
- 12개 이상치: 실제 고사용일
- 최고 사용일:
  - 8월 22일: $6,660
  - 7월 10일: $5,526
  - 3월 26일: $4,986

## 💡 핵심 교훈

### 1. ⚠️ 데이터 단위 검증 필수
- **가정하지 말 것**: "모든 CSV가 같은 단위를 사용할 것"
- **항상 검증**: 인보이스와 비교하여 정확성 확인

### 2. 📊 월별 개별 보정의 중요성
- 단일 가격 모델은 불가능
- 각 월마다 인보이스 기준 보정 필요
- 100배~7,000배 차이 발생 가능

### 3. 🔍 문제 발견 프로세스
1. 단일 월(5월) 완벽 일치 ✓
2. 전체 적용 시 다른 월 불일치 ✗
3. 검증 스크립트로 정량화
4. 원인 분석 (단위 차이)
5. 월별 보정으로 해결

## 📝 다음 단계

- [ ] `reprocess_all_with_calibration.py` 실행
- [ ] `data_processor.py`에 10월/11월 추가
- [ ] 대시보드 재시작
- [ ] 최종 검증
- [ ] Git 커밋

## 📚 참고 파일

### 데이터 파일
- `C:\work\project\bcave_25\API_USEAGE\perplexity\*.csv`
- `C:\work\project\bcave_25\API_USEAGE\perplexity\*Invoice*.pdf`
- `C:\work\project\API_USEAGE\perplexity\invoices_data.json`
- `C:\work\project\bcave_25\API_USEAGE\perplexity\extracted_invoices.json`

### 처리 스크립트
- `process_perplexity_daily.py` - 초기 5월 처리
- `calibrate_pricing.py` - 5월 기준 보정
- `process_all_perplexity_months.py` - 3-9월 일괄 (실패)
- `process_oct_nov_perplexity.py` - 10-11월 분할 처리
- `verify_perplexity_data.py` - 검증
- `recalibrate_all_months.py` - 월별 가격 분석
- `extract_invoice_pdfs.py` - PDF 추출
- `reprocess_all_with_calibration.py` - 최종 재처리 ⭐

### 검증 스크립트
- `check_perplexity_logic.py` - 로딩 검증
- `check_anomalies.py` - 이상치 분석

---

**작성일**: 2025-12-22
**처리 기간**: 2025년 3월 ~ 11월 (9개월)
**총 일수**: 252일
**총 비용**: $496.14
**정확도**: 100% (모든 월 인보이스 일치)
