# bcave_25 Documentation

이 폴더는 bcave_25 프로젝트의 데이터 분석 관련 문서와 스크립트를 포함합니다.

## 📚 문서

### PERPLEXITY_CSV_CALIBRATION.md
Perplexity API 사용 데이터의 CSV 보정 작업 전체 문서
- 문제 발견 과정
- 해결 방법
- 월별 개별 가격 보정 방식
- 최종 결과 및 검증

**작성일**: 2025-12-22
**대상 기간**: 2025년 3월 ~ 11월

## 🔧 스크립트 (`scripts/`)

### 데이터 추출
- `extract_invoice_pdfs.py` - PDF 인보이스에서 데이터 자동 추출

### 데이터 분석
- `recalibrate_all_months.py` - 월별 단위 가격 역산 분석
- `verify_perplexity_data.py` - 인보이스 vs CSV 검증

### 데이터 처리
- `process_oct_nov_perplexity.py` - 10월/11월 분할 파일 처리
- `reprocess_all_with_calibration.py` - 전체 월 재처리 (월별 보정 적용)

## 📂 관련 데이터

실제 데이터 파일 위치:
```
C:\work\project\bcave_25\API_USEAGE\perplexity\
├── 2503-2511_daily_costs_calibrated.csv  (각 월별 일별 비용)
├── *-PERP-*.csv                          (원본 CSV 데이터)
├── *-PERP-Invoice-*.pdf                  (인보이스 PDF)
└── extracted_invoices.json               (추출된 인보이스 데이터)
```

## 🎯 사용 방법

### 새로운 월 데이터 추가 시

1. PDF 인보이스 추출
   ```bash
   python scripts/extract_invoice_pdfs.py
   ```

2. 전체 재처리
   ```bash
   python scripts/reprocess_all_with_calibration.py
   ```

3. 검증
   ```bash
   python scripts/verify_perplexity_data.py
   ```

## ⚠️ 중요 사항

- **월별 개별 보정 필수**: 단일 가격 모델 사용 불가 (최대 7,749배 차이)
- **인보이스 기준**: 모든 계산은 인보이스 총액과 100% 일치해야 함
- **분할 파일 처리**: 10월/11월은 2개 파일로 분할되어 있음

## 📊 처리 결과

- **총 기간**: 2025년 3월 ~ 11월 (9개월)
- **총 일수**: 252일
- **총 비용**: $496.14
- **정확도**: 100% (모든 월 인보이스 일치)

---

**최종 업데이트**: 2025-12-22
