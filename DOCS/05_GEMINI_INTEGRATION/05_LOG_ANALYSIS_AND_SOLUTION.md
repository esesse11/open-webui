# OpenWebUI 로그 분석 및 이미지 생성 오류 해결

**작성일**: 2025-12-06
**분석 대상**: 이미지 생성 오류 ("An error occurred while generating an image")

---

## 🔍 로깅 시스템 분석 결과

### 현재 로깅 구성

#### 1. 로그 출력 위치
**파일**: `C:\openwebui\source\open-webui\backend\open_webui\main.py:530`
```python
logging.basicConfig(stream=sys.stdout, level=GLOBAL_LOG_LEVEL)
log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])
```

**결론**:
- ✅ 모든 로그는 **stdout**(터미널 출력)으로 전송
- ❌ 별도의 로그 파일 **없음**
- ⚠️ 서버 재시작 시 로그 **손실**

#### 2. 이미지 라우터 로깅 설정
**파일**: `C:\openwebui\source\open-webui\backend\open_webui\routers\images.py:32-33`
```python
log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["IMAGES"])
```

**로그 레벨 환경 변수**:
- `IMAGES_LOG_LEVEL`: 이미지 생성/편집 관련 로그 레벨 제어
- 기본값: `GLOBAL_LOG_LEVEL`

#### 3. 에러 처리 코드
**파일**: `C:\openwebui\source\open-webui\backend\open_webui\routers\images.py:762-768`
```python
except Exception as e:
    error = e
    if r != None:
        data = r.json()
        if "error" in data:
            error = data["error"]["message"]
    raise HTTPException(status_code=400, detail=ERROR_MESSAGES.DEFAULT(error))
```

**에러 메시지 포맷**:
```python
# constants.py:23-24
DEFAULT = lambda err="": f'{"Something went wrong :/" if err == "" else "[ERROR: " + str(err) + "]"}'
```

**처리 흐름**:
1. API 요청 실패 시 Exception 발생
2. 응답 객체(`r`)가 있으면 JSON에서 에러 메시지 추출
3. `HTTPException(400)` 발생 → 프론트엔드로 전송
4. 프론트엔드가 "An error occurred while generating an image" 표시

---

## 🐛 실제 오류 분석

### 발생한 오류
```
models/gemini-2.5-flash - An error occurred while generating an image
```

### 오류 원인

#### 1. 잘못된 모델 사용
사용자가 **Gemini 텍스트 모델**을 **이미지 생성**에 사용 시도:
```
❌ gemini-2.5-flash → 텍스트 생성 모델
❌ gemini-2.5-pro → 텍스트 생성 모델
✅ imagen-3.0-generate-002 → 이미지 생성 모델
```

#### 2. API 요청 실패 과정

**OpenWebUI 내부 흐름**:
```
사용자: 이미지 생성 요청
  ↓
OpenWebUI Admin 설정:
  - Engine: gemini
  - Model: gemini-2.5-flash ❌ (잘못된 모델)
  - API Base: https://us-central1-aiplatform.googleapis.com/v1
  ↓
images.py (라인 600-634):
  - URL: {API_BASE}/models/gemini-2.5-flash:predict
  - Body: {
      "instances": {"prompt": "..."},
      "parameters": {...}
    }
  ↓
Google Vertex AI API:
  ❌ 404 Not Found 또는 400 Bad Request
  → 오류: "Model not found" 또는 "Invalid model for this operation"
  ↓
images.py (라인 636):
  r.raise_for_status() → Exception 발생
  ↓
images.py (라인 762-768):
  → HTTPException(400)
  ↓
프론트엔드:
  → "An error occurred while generating an image"
```

#### 3. 실제 API 에러 (추정)

Google API가 반환했을 실제 에러:
```json
{
  "error": {
    "code": 404,
    "message": "Model gemini-2.5-flash:predict not found",
    "status": "NOT_FOUND"
  }
}
```
또는
```json
{
  "error": {
    "code": 400,
    "message": "Model gemini-2.5-flash does not support image generation",
    "status": "INVALID_ARGUMENT"
  }
}
```

#### 4. 지원되는 모델 확인
**파일**: `images.py:384-387`
```python
elif request.app.state.config.IMAGE_GENERATION_ENGINE == "gemini":
    return [
        {"id": "imagen-3.0-generate-002", "name": "imagen-3.0 generate-002"},
    ]
```

**결론**: OpenWebUI는 Gemini 엔진에서 **오직 imagen-3.0-generate-002만** 지원

---

## 💡 해결 방법

### ✅ 즉시 해결: 올바른 모델로 변경

#### Admin Panel 설정
```
OpenWebUI → Admin Panel → Settings → Images

Image Generation:
  Engine: gemini
  Model: imagen-3.0-generate-002  ⬅️ 여기 수정!

Gemini API:
  Base URL: https://us-central1-aiplatform.googleapis.com/v1
  API Key: [실제 Google Cloud API 키]
  Endpoint Method: predict
```

#### 저장 후 테스트
1. 설정 저장
2. 채팅창에서 이미지 생성 버튼 클릭
3. 프롬프트 입력: "귀여운 고양이, 만화 스타일"
4. 생성 확인

---

## 📊 로그 수집 환경 구축

### 방법 1: 서버 실행 시 로그 파일로 리디렉션 ⭐ 추천

#### Windows (PowerShell)
```powershell
cd C:\openwebui\source\open-webui\backend

# 로그 디렉토리 생성
New-Item -ItemType Directory -Force -Path "C:\work\project\logs"

# 서버 실행 + 로그 파일 저장
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8001 --reload 2>&1 | Tee-Object -FilePath "C:\work\project\logs\openwebui_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

#### 실시간 로그 확인
```powershell
# 새 터미널에서
Get-Content "C:\work\project\logs\openwebui_*.log" -Wait -Tail 50
```

### 방법 2: Python 로깅 설정 수정

#### 파일 수정: `main.py`

**Before (라인 530)**:
```python
logging.basicConfig(stream=sys.stdout, level=GLOBAL_LOG_LEVEL)
```

**After**:
```python
import logging.handlers

# 로그 디렉토리 생성
LOG_DIR = Path("C:/work/project/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 로그 파일 경로
LOG_FILE = LOG_DIR / f"openwebui_{time.strftime('%Y%m%d')}.log"

# 로깅 설정
logging.basicConfig(
    level=GLOBAL_LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # 파일 핸들러 (일별 로테이션)
        logging.handlers.TimedRotatingFileHandler(
            LOG_FILE,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        ),
        # 콘솔 핸들러 (기존 stdout 유지)
        logging.StreamHandler(sys.stdout)
    ]
)
```

**장점**:
- ✅ 파일 + 터미널 동시 출력
- ✅ 일별 자동 로테이션
- ✅ 30일 백업 보관
- ✅ UTF-8 인코딩 (한글 지원)

### 방법 3: 특정 라우터만 상세 로깅

#### 환경 변수 설정
```powershell
# 이미지 라우터만 DEBUG 레벨로
$env:IMAGES_LOG_LEVEL = "DEBUG"

# 서버 실행
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8001 --reload
```

#### images.py에 디버그 로그 추가

**파일**: `images.py:600-640`

**추가할 로그**:
```python
elif request.app.state.config.IMAGE_GENERATION_ENGINE == "gemini":
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": request.app.state.config.IMAGES_GEMINI_API_KEY,
    }

    data = {}

    if (
        request.app.state.config.IMAGES_GEMINI_ENDPOINT_METHOD == ""
        or request.app.state.config.IMAGES_GEMINI_ENDPOINT_METHOD == "predict"
    ):
        model = f"{model}:predict"
        data = {
            "instances": {"prompt": form_data.prompt},
            "parameters": {
                "sampleCount": form_data.n,
                "outputOptions": {"mimeType": "image/png"},
            },
        }

    # ✅ 추가: 요청 정보 로깅
    log.info(f"Gemini Image Generation Request:")
    log.info(f"  Model: {model}")
    log.info(f"  URL: {request.app.state.config.IMAGES_GEMINI_API_BASE_URL}/models/{model}")
    log.info(f"  Prompt: {form_data.prompt}")
    log.debug(f"  Request Data: {json.dumps(data, indent=2)}")

    try:
        r = await asyncio.to_thread(
            requests.post,
            url=f"{request.app.state.config.IMAGES_GEMINI_API_BASE_URL}/models/{model}",
            json=data,
            headers=headers,
        )

        # ✅ 추가: 응답 정보 로깅
        log.info(f"API Response Status: {r.status_code}")
        log.debug(f"API Response Headers: {dict(r.headers)}")

        r.raise_for_status()
        res = r.json()

        log.info(f"Image generation successful, processing {len(res.get('predictions', []))} images")

    except requests.exceptions.HTTPError as e:
        # ✅ 추가: 상세 에러 로깅
        log.error(f"Gemini API HTTP Error: {e}")
        log.error(f"Response Status Code: {r.status_code}")
        log.error(f"Response Body: {r.text}")
        raise
    except Exception as e:
        # ✅ 추가: 일반 에러 로깅
        log.error(f"Gemini Image Generation Error: {e}", exc_info=True)
        raise
```

**효과**:
```
# 성공 시 로그
2025-12-06 10:30:15 - open_webui.routers.images - INFO - Gemini Image Generation Request:
2025-12-06 10:30:15 - open_webui.routers.images - INFO -   Model: imagen-3.0-generate-002:predict
2025-12-06 10:30:15 - open_webui.routers.images - INFO -   URL: https://us-central1-aiplatform.googleapis.com/v1/models/imagen-3.0-generate-002:predict
2025-12-06 10:30:15 - open_webui.routers.images - INFO -   Prompt: 귀여운 고양이
2025-12-06 10:30:17 - open_webui.routers.images - INFO - API Response Status: 200
2025-12-06 10:30:17 - open_webui.routers.images - INFO - Image generation successful, processing 1 images

# 실패 시 로그 (잘못된 모델)
2025-12-06 10:25:10 - open_webui.routers.images - INFO - Gemini Image Generation Request:
2025-12-06 10:25:10 - open_webui.routers.images - INFO -   Model: gemini-2.5-flash:predict
2025-12-06 10:25:10 - open_webui.routers.images - INFO -   URL: https://us-central1-aiplatform.googleapis.com/v1/models/gemini-2.5-flash:predict
2025-12-06 10:25:10 - open_webui.routers.images - INFO -   Prompt: 귀여운 고양이
2025-12-06 10:25:11 - open_webui.routers.images - ERROR - Gemini API HTTP Error: 404 Client Error
2025-12-06 10:25:11 - open_webui.routers.images - ERROR - Response Status Code: 404
2025-12-06 10:25:11 - open_webui.routers.images - ERROR - Response Body: {"error":{"code":404,"message":"Model gemini-2.5-flash:predict not found"}}
```

---

## 🚀 추천 조치 순서

### 1단계: 즉시 해결 (5분)
```
✅ Admin Panel → Images → Model 변경
   gemini-2.5-flash → imagen-3.0-generate-002
✅ 저장 후 테스트
```

### 2단계: 로그 수집 시작 (10분)
```
✅ 방법 1 선택: 서버 재시작 시 로그 파일 리디렉션
   - 간단하고 코드 수정 불필요
   - 즉시 적용 가능
```

### 3단계: 상세 로깅 추가 (30분) - 선택사항
```
✅ images.py에 디버그 로그 추가
✅ IMAGES_LOG_LEVEL=DEBUG 설정
✅ 서버 재시작
```

### 4단계: 로그 분석 도구 설치 (선택사항)
```
# 로그 뷰어 도구
pip install glogg  # 대용량 로그 뷰어

# 또는 PowerShell로 필터링
Get-Content logs\*.log | Select-String "ERROR|WARN"
```

---

## 📋 체크리스트

### 즉시 실행
- [ ] Admin Panel → Images → Model → `imagen-3.0-generate-002`
- [ ] 설정 저장
- [ ] 이미지 생성 테스트

### 로그 수집 환경 구축
- [ ] 로그 디렉토리 생성: `C:\work\project\logs`
- [ ] 서버 실행 시 로그 리디렉션 설정
- [ ] 로그 파일 정상 생성 확인

### 디버깅 강화 (선택)
- [ ] `images.py`에 디버그 로그 추가
- [ ] `IMAGES_LOG_LEVEL=DEBUG` 환경 변수 설정
- [ ] 상세 로그 확인

---

## 🔗 관련 파일

- **로깅 설정**: `C:\openwebui\source\open-webui\backend\open_webui\main.py:530`
- **이미지 라우터**: `C:\openwebui\source\open-webui\backend\open_webui\routers\images.py`
- **에러 처리**: `images.py:762-768`
- **지원 모델**: `images.py:384-387`
- **로그 레벨**: `C:\openwebui\source\open-webui\backend\open_webui\env.py:104-111`

---

## 💡 핵심 요약

### 문제
```
❌ gemini-2.5-flash (텍스트 모델)를 이미지 생성에 사용
→ Google API: 404 Not Found
→ OpenWebUI: "An error occurred while generating an image"
```

### 원인
```
Gemini ≠ Imagen
- Gemini: 텍스트 생성 모델
- Imagen: 이미지 생성 모델
```

### 해결
```
✅ Model: imagen-3.0-generate-002
✅ API Base: https://us-central1-aiplatform.googleapis.com/v1
✅ Endpoint Method: predict
```

### 로그 수집
```
현재: stdout만 (터미널)
개선: 파일 + 터미널 (리디렉션 또는 핸들러 추가)
```

---

**작성자**: Claude Code
**최종 수정**: 2025-12-06
**상태**: 분석 완료 ✅ | 해결 방법 제시 완료 ✅
