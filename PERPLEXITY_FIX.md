# Perplexity 데이터 수정 완료 (최종)

## 문제 이해

Perplexity는 **선불 크레딧 방식**으로 작동합니다:
1. **크레딧 구매**: $50씩 선불로 크레딧을 구매 (인보이스 발행)
2. **실제 사용**: API를 사용하면 크레딧에서 차감되고 세부 사용 내역 인보이스 발행

### 기존 문제
- 크레딧 구매 인보이스($50)와 실제 사용 인보이스를 구분 못함
- 2개의 인보이스만 하드코딩되어 있었음
- 실제로는 14개의 인보이스 존재

## 해결 방법

### 1. 인보이스 타입 구분

#### 크레딧 구매 인보이스 (무시)
```
Description: Credits
Quantity: 50
Amount: $50.00
Memo: Manual credits purchase
```
→ **대시보드에 포함하지 않음**

#### 사용 내역 인보이스 (파싱)
```
API Requests: $1.16
Citation Tokens: $1.92
Input Tokens: $3.84
Number of Search Queries: $7.30
Output Tokens: $2.99
Reasoning Tokens: $22.08
---
Total Usage: $39.29
Pre-purchase applied: -$38.87
Amount due: $0.42
```
→ **Total Usage를 대시보드에 표시**

### 2. 추출 스크립트 (`extract_perplexity.py`)

#### 주요 기능
1. **타입 감지**
   - "Manual credits purchase" → credits_purchase (무시)
   - "API Requests", "Tokens" 등 존재 → usage (파싱)

2. **세부 항목 추출**
   ```python
   - API Requests
   - Citation Tokens
   - Input Tokens
   - Output Tokens
   - Reasoning Tokens
   - Number of Search Queries
   - Total Usage (합계)
   - Amount Due (크레딧으로 커버 안 된 금액)
   ```

3. **결과 저장**
   - `invoices_data.json`에 모든 인보이스 데이터 저장

### 3. 데이터 프로세서 업데이트

**변경 사항**:
```python
# total_usage를 amount로 사용 (실제 API 사용 비용)
if invoice.get('type') == 'usage':
    date = invoice.get('date')
    total_usage = invoice.get('total_usage', 0)

    if date and total_usage > 0:
        perplexity_data.append({
            'date': pd.to_datetime(date),
            'amount': total_usage,  # 실제 사용 비용
            'provider': 'Perplexity'
        })
```

## 최종 결과

### 인보이스 분류 (14개)

#### 크레딧 구매 (7개) - 무시
- Invoice-00001: 2025-03-25, $50.00
- Invoice-00005: 2025-05-08, $50.00
- Invoice-00006: 2025-05-28, $50.00
- Invoice-00008: 2025-06-20, $50.00
- Invoice-00010: 2025-07-03, $50.00
- Invoice-00011: 2025-07-23, $50.00
- Invoice-00013: 날짜 미상, $50.00

**총 크레딧 구매**: $350.00

#### 실제 사용 (7개) - 대시보드에 표시

| 인보이스 | 날짜 | 사용 기간 | Total Usage | Amount Due |
|---------|------|-----------|-------------|------------|
| Invoice-00002 | 2025-04-01 | Mar 25-31 | $3.38 | $0.00 |
| Invoice-00003 | 2025-04-30 | Apr 1-30 | $45.11 | $0.00 |
| Invoice-00004 | 2025-05-01 | - | $0.00 | $0.00 |
| Invoice-00007 | 2025-06-01 | May 1-31 | $39.29 | $0.42 |
| Invoice-00009 | 2025-07-01 | Jun 1-30 | $93.76 | $0.00 |
| Invoice-00012 | 2025-08-01 | Jul 1-31 | $88.37 | $0.00 |
| Invoice-00014 | 날짜 미상 | Aug 1-31 | $64.27 | $0.00 |

**총 API 사용**: $334.18
**실제 결제 금액**: $0.42 (크레딧 초과분)

### 대시보드 월별 표시

```
2025-04: $48.49 (Invoice-00002 + 00003)
2025-06: $39.29 (Invoice-00007)
2025-07: $93.76 (Invoice-00009)
2025-08: $88.37 (Invoice-00012)
```

## 이점

### 1. ✅ 정확한 비용 추적
- 크레딧 구매($350)와 실제 사용($334.18)을 명확히 구분
- 대시보드에는 **실제 API 사용 비용**만 표시

### 2. ✅ 세부 사용 내역 파악
- API Requests, Tokens, Search Queries 등 항목별 비용 추출
- 어떤 항목에 비용이 많이 드는지 분석 가능

### 3. ✅ 자동화
- 새 인보이스 추가 시 자동으로 파싱
- PDF만 폴더에 추가하고 스크립트 실행

### 4. ✅ 크레딧 잔액 추적 가능
- 구매 크레딧: $350.00
- 사용 크레딧: $334.18
- 남은 크레딧: $15.82
- 실제 결제: $0.42 (크레딧 부족분)

## 사용 방법

### 새 인보이스 추가
```bash
# 1. PDF 파일 저장
# C:\work\project\API_USEAGE\perplexity\Invoice-LISGSS-XXXXX.pdf

# 2. 파싱 스크립트 실행
python extract_perplexity.py

# 3. 대시보드 확인
streamlit run dashboard.py
# 자동으로 새 데이터 반영됨
```

### 출력 예시
```
Processing: Invoice-LISGSS-00007.pdf
  ✓ Usage Invoice
    Date: 2025-06-01
    Period: May 1 to 31, 2025
    Total Usage: $39.29
    Amount Due: $0.42

Processing: Invoice-LISGSS-00008.pdf
  ⊗ Credits Purchase (skipped)

============================================================
Total invoices: 14
  - Usage invoices: 7
  - Credits purchases: 7
  - Unknown: 0

USAGE SUMMARY (excluding credits purchases):
  Total API Usage: $334.18
  Amount Due (not covered by credits): $0.42
```

## 파일 목록

- `extract_perplexity.py`: PDF 파싱 스크립트 (신규)
- `API_USEAGE/perplexity/invoices_data.json`: 추출 데이터 (자동 생성)
- `data_processor.py`: 데이터 로더 (업데이트)
- `dashboard.py`: 대시보드 (자동 반영)

## 중요 개념

### Total Usage vs Amount Due

- **Total Usage**: 실제 API 사용 총액 (크레딧 차감 전)
  - 대시보드에 표시할 실제 비용
  - 예: $39.29

- **Amount Due**: 크레딧으로 커버 안 된 금액 (실제 청구액)
  - 보통 $0.00 (크레딧으로 모두 지불)
  - 크레딧 부족 시에만 발생
  - 예: $0.42

**대시보드 표시**: Total Usage 사용 (실제 API 사용량을 추적하기 위해)

---

**최종 수정일**: 2025-10-21
**처리 인보이스**: 14건
- 크레딧 구매: 7건 ($350.00) → 무시
- 실제 사용: 7건 ($334.18) → 대시보드 표시
- 실제 결제: $0.42
