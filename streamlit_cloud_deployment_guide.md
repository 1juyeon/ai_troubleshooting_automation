# Streamlit Cloud 배포 가이드

## 1. Streamlit Cloud 설정

### 1.1 Secrets 설정

Streamlit Cloud에서 다음 환경변수들을 설정해야 합니다:

#### 필수 설정
```toml
# .streamlit/secrets.toml 또는 Streamlit Cloud Secrets
GEMINI_API_KEY = "your_gemini_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
MONGODB_URI = "your_mongodb_connection_string"
```

#### 선택적 설정
```toml
# SOLAPI 설정 (SMS 발송 기능 사용시)
SOLAPI_API_KEY = "your_solapi_api_key"
SOLAPI_API_SECRET = "your_solapi_api_secret"
```

### 1.2 API 키 발급 방법

#### Gemini API 키
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. API 키 생성
3. 생성된 API 키를 `GEMINI_API_KEY`에 설정

#### OpenAI API 키
1. [OpenAI Platform](https://platform.openai.com/) 접속
2. API Keys → Create new secret key
3. 생성된 API 키를 `OPENAI_API_KEY`에 설정

#### MongoDB 연결 문자열
1. [MongoDB Atlas](https://cloud.mongodb.com/) 접속
2. Database → Connect → Connect your application
3. 연결 문자열을 `MONGODB_URI`에 설정

### 1.3 Streamlit Cloud에서 Secrets 설정하는 방법

1. Streamlit Cloud 대시보드에서 앱 선택
2. Settings → Secrets
3. 위의 키-값 쌍을 추가
4. Save 버튼 클릭

## 2. 배포 단계

### 2.1 GitHub 저장소 준비
```bash
git add .
git commit -m "Add Streamlit Cloud deployment support"
git push origin main
```

### 2.2 Streamlit Cloud에서 배포
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. "New app" 클릭
3. GitHub 저장소 선택
4. 메인 파일 경로: `app.py`
5. Deploy 클릭

## 3. 배포 후 확인사항

### 3.1 로그 확인
- Streamlit Cloud → 앱 선택 → Logs
- API 키 로딩 메시지 확인
- 오류 메시지 확인

### 3.2 기능 테스트
- AI 분석 기능 테스트
- MongoDB 연결 테스트
- SMS 발송 기능 테스트 (SOLAPI 설정시)

## 4. 문제 해결

### 4.1 API 키 오류
```
❌ AI API 키가 설정되지 않았습니다.
```
- Streamlit Cloud Secrets에서 API 키 확인
- 키 이름이 정확한지 확인 (`GEMINI_API_KEY`, `OPENAI_API_KEY`)

### 4.2 MongoDB 연결 오류
```
⚠️ DB 연결 실패 - 로컬 저장소 사용
```
- MongoDB 연결 문자열 확인
- IP 화이트리스트 설정 확인
- 사용자명/비밀번호 확인

### 4.3 SOLAPI 오류
```
❌ SOLAPI API 키가 설정되지 않았습니다.
```
- SOLAPI API 키와 시크릿 확인
- 계정 활성화 상태 확인

## 5. 보안 고려사항

- API 키는 절대 코드에 하드코딩하지 마세요
- Streamlit Cloud Secrets 사용을 권장합니다
- 환경변수는 로컬 개발용으로만 사용하세요
- API 키는 정기적으로 갱신하세요

## 6. 비용 최적화

### 6.1 API 사용량 모니터링
- Gemini API: Google Cloud Console에서 사용량 확인
- OpenAI API: OpenAI Platform에서 사용량 확인
- MongoDB: Atlas 대시보드에서 사용량 확인

### 6.2 비용 절약 팁
- 적절한 모델 선택 (GPT-3.5 Turbo vs GPT-4o)
- 요청 빈도 제한
- 응답 토큰 수 제한
- MongoDB 인덱스 최적화
