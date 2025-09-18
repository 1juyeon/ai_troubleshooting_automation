# 🚀 Streamlit Cloud 안전 배포 가이드

## 📋 배포 전 체크리스트

### ✅ **보안 설정**
- ✅ **API 키**들은 Streamlit Cloud에서만 관리
- ✅ **환경변수**는 민감한 정보 포함 금지
- ✅ **GitHub**에는 절대 API 키 커밋 금지

### ✅ **의존성 관리**
- ✅ `requirements.txt` 최신화
- ✅ 불필요한 패키지 제거
- ✅ 버전 호환성 확인

### ✅ **코드 품질**
- ✅ 디버그 코드 제거
- ✅ 하드코딩된 값 제거
- ✅ 에러 핸들링 구현

## 🔑 API 키 설정

### 1. Streamlit Cloud Secrets 설정
Streamlit Cloud 대시보드에서 다음 설정을 추가하세요:

```toml
# Gemini API 키 (필수 - 모든 Gemini 모델 사용 가능)
GEMINI_API_KEY = "your-actual-gemini-api-key"

# OpenAI API 키 (선택사항 - GPT 모델 사용)
OPENAI_API_KEY = "your-openai-api-key"

# MongoDB Atlas 연결 문자열 (선택사항 - 클라우드 데이터 저장)
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority"

# SOLAPI API 키 (선택사항 - SMS 발송 기능)
SOLAPI_API_KEY = "your-solapi-api-key"
SOLAPI_API_SECRET = "your-solapi-api-secret"

# 기존 호환성 유지 (선택사항)
GOOGLE_API_KEY = "your-google-api-key"
```

### 2. 환경변수 설정 (선택사항)
로컬 개발 시 환경변수로 설정:

```bash
export GEMINI_API_KEY="your-actual-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export MONGODB_URI="your-mongodb-connection-string"
export SOLAPI_API_KEY="your-solapi-api-key"
export SOLAPI_API_SECRET="your-solapi-api-secret"
export GOOGLE_API_KEY="your-google-api-key"
```

## 🌐 배포 단계

### 1. GitHub 저장소 준비
```bash
# 현재 변경사항 커밋
git add .
git commit -m "Remove OAuth functionality and simplify authentication"
git push origin main
```

### 2. Streamlit Cloud 연결
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. GitHub 저장소 연결
3. 배포 설정 확인

### 3. 배포 후 확인
- ✅ 앱이 정상적으로 실행되는지 확인
- ✅ API 키가 올바르게 로드되는지 확인
- ✅ 모든 기능이 정상 작동하는지 테스트

## 🔍 배포 후 모니터링

### 1. 로그 확인
- Streamlit Cloud 대시보드에서 로그 모니터링
- 에러 발생 시 즉시 확인

### 2. 성능 모니터링
- 응답 시간 확인
- 메모리 사용량 모니터링
- API 호출 횟수 추적

### 3. 사용자 피드백
- 사용자 경험 개선점 파악
- 버그 리포트 수집 및 대응

## ⚠️ 주의사항

### 1. 보안
- **절대** API 키를 코드에 하드코딩하지 마세요
- **절대** GitHub에 API 키를 커밋하지 마세요
- Streamlit Cloud Secrets만 사용하세요

### 2. 성능
- 대용량 데이터 처리 시 메모리 사용량 주의
- API 호출 횟수 제한 확인
- 캐싱 전략 활용

### 3. 유지보수
- 정기적인 의존성 업데이트
- 보안 패치 적용
- 백업 및 복구 계획 수립

## 🆘 문제 해결

### 1. 배포 실패
- 로그 확인
- 의존성 충돌 검사
- API 키 설정 재확인

### 2. 런타임 오류
- 에러 메시지 분석
- 로컬 환경에서 재현 시도
- 디버그 모드 활성화

### 3. 성능 이슈
- 메모리 사용량 분석
- API 응답 시간 측정
- 캐싱 전략 검토

## 📞 지원

문제가 발생하면 다음 연락처로 문의하세요:
- **기술지원**: 02-678-1234
- **이메일**: support@privkeeper.com
- **긴급상황**: 010-3456-7890

---

**성공적인 배포를 위한 핵심: 보안, 성능, 모니터링!** 🚀
