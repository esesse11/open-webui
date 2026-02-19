# API 사용량 데이터 현황

## 📊 데이터 상태

### ✅ **Claude API** (완전한 데이터)
```
위치: C:\work\project\API_USEAGE\claude\
파일:
- claude_api_cost_*.csv (비용 데이터)
- claude_api_tokens_*.csv (토큰 데이터)

포함 정보:
✅ 일별 비용 (cost_usd)
✅ 모델별 사용량
✅ 토큰 사용량 (input, output, cache)
✅ 사용 날짜
```

**상태**: 대시보드에 **완전히 표시됨** ✅

---

### ❌ **OpenAI API** (빈 데이터)
```
위치: C:\work\project\API_USEAGE\openai\
파일: 100개 CSV 파일

포함 정보:
❌ 타임스탬프만 있음 (start_time, end_time)
❌ 비용 데이터 없음
❌ 사용량 데이터 없음
```

**문제**: OpenAI Usage Dashboard에서 데이터를 다운로드했으나 실제 사용 내역이 없음

**원인**:
1. 해당 기간에 OpenAI API를 사용하지 않음
2. 또는 다른 Organization ID에서 사용

**해결 방법**:
```bash
# 1. OpenAI Usage Dashboard 접속
https://platform.openai.com/usage

# 2. 올바른 Organization 선택

# 3. 기간 설정 후 데이터 다운로드

# 4. CSV 파일을 API_USEAGE/openai/ 폴더에 저장
```

**상태**: 대시보드에 **표시 안 됨** (데이터 없음)

---

### ✅ **Perplexity API** (인보이스 데이터)
```
위치: C:\work\project\API_USEAGE\perplexity\
파일: Invoice-*.pdf

포함 정보:
✅ 인보이스 날짜
✅ 총 비용
✅ 사용 기간
```

**상태**: 대시보드에 **표시됨** ✅

---

## 🎯 대시보드 표시 현황

### 현재 보이는 제공자:
- ✅ **Claude** (주요 데이터)
- ✅ **Perplexity** (인보이스만)

### 표시 안 되는 제공자:
- ❌ **OpenAI** (데이터 없음)

---

## 📝 OpenAI 데이터 추가 방법

### 1. OpenAI Platform에서 데이터 다운로드

```bash
# OpenAI Usage Dashboard
https://platform.openai.com/usage

1. Organization 선택
2. 날짜 범위 선택
3. "Export" 또는 "Download CSV" 클릭
4. 각 서비스별 CSV 다운로드:
   - Completions
   - Embeddings
   - Images
   - Audio (TTS, Whisper)
   등
```

### 2. CSV 파일 구조 확인

올바른 CSV 형식:
```csv
start_time,end_time,snapshot_id,model,usage_type,tokens,cost
1735689600,1735776000,abc123,gpt-4,completion,1000,0.03
```

필수 컬럼:
- `start_time` 또는 `start_time_iso`
- `cost` 또는 `amount`
- `model` (옵션)

### 3. 파일 배치

```bash
API_USEAGE/openai/
├── completions_usage_2025-01-01_2025-01-31.csv
├── embeddings_usage_2025-01-01_2025-01-31.csv
└── ...
```

### 4. 대시보드 새로고침

```bash
# Streamlit이 자동으로 데이터 다시 로드
# 또는 브라우저 새로고침
```

---

## 💡 참고사항

### 왜 OpenAI 데이터가 비어있나요?

**현재 파일 내용**:
```csv
start_time,end_time,start_time_iso,end_time_iso
1735689600,1735776000,2025-01-01T00:00:00+00:00,2025-01-02T00:00:00+00:00
```

→ **비용 컬럼이 없음!**

**올바른 파일 내용**:
```csv
start_time,end_time,model,tokens,cost
1735689600,1735776000,gpt-4,1500,0.045
```

→ **비용 데이터 포함**

### 데이터 확인 방법

```bash
# 파일에 비용 데이터가 있는지 확인
head API_USEAGE/openai/completions_usage_*.csv

# 컬럼에 'cost' 또는 'amount'가 있어야 함
```

---

## 🔧 문제 해결

### OpenAI 데이터가 표시 안 될 때

1. **파일 확인**
   ```bash
   # 파일에 헤더만 있는지 확인
   wc -l API_USEAGE/openai/*.csv
   # 2행 이상이어야 함 (헤더 + 데이터)
   ```

2. **컬럼 확인**
   ```bash
   # cost 컬럼 확인
   head -1 API_USEAGE/openai/completions_usage_*.csv
   ```

3. **데이터 재다운로드**
   - OpenAI Platform에서 다시 다운로드
   - 올바른 Organization 선택
   - API 사용 기록이 있는 기간 선택

---

## ✅ 권장사항

현재 상태에서는:
- **Claude 데이터만 사용** (완전한 분석 가능)
- **Perplexity는 보조 데이터**로 활용
- **OpenAI 데이터는 실제 사용 시 추가**

OpenAI API를 실제로 사용하고 있다면:
1. OpenAI Platform에서 데이터 다운로드
2. CSV 파일에 비용 데이터 포함되었는지 확인
3. API_USEAGE/openai/ 폴더에 저장
4. 대시보드 자동 업데이트

---

**작성일**: 2025-10-21
**작성자**: Claude Code
