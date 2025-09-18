# 로컬 개발 환경 설정 가이드

## 개요
이 프로젝트는 Streamlit Cloud의 secrets와 로컬 .env 파일을 모두 지원합니다.

## 로컬 개발 설정

### 1. .env 파일 생성
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Google OAuth 설정
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Google API 키 (Gemini용)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_google_api_key_here

# MongoDB 연결 정보
MONGODB_URI=your_mongodb_uri_here

# SOLAPI 설정
SOLAPI_API_KEY=your_solapi_api_key_here
SOLAPI_API_SECRET=your_solapi_api_secret_here

# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here
```

**실제 키 값들은 보안상 이 문서에 포함하지 않습니다.**
**로컬 개발을 위해서는 실제 API 키들을 `.env` 파일에 입력해주세요.**

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

## 환경변수 우선순위
1. **Streamlit Cloud Secrets** (최우선)
2. **로컬 .env 파일** (로컬 개발시)
3. **시스템 환경변수** (차선)

## Streamlit Cloud 배포
Streamlit Cloud에서는 `.env` 파일 대신 Secrets를 사용합니다. Streamlit Cloud 대시보드에서 다음 키들을 설정하세요:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_API_KEY` 또는 `GEMINI_API_KEY`
- `MONGODB_URI`
- `SOLAPI_API_KEY`
- `SOLAPI_API_SECRET`
- `OPENAI_API_KEY`

## 보안 주의사항
- `.env` 파일은 절대 Git에 커밋하지 마세요
- 실제 API 키는 안전하게 보관하세요
- 프로덕션 환경에서는 환경변수나 secrets를 사용하세요
