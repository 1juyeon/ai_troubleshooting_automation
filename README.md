# PrivKeeper P 장애 대응 자동화 시스템

Gemini AI 기반 고객 문의 자동 분석 및 응답 도구

## 🚀 최근 업데이트

### OAuth 인증 개선 (2024년 12월)

**해결된 문제:**
- ✅ **새 창 방지**: Google 로그인 시 새 창이 열리는 문제 해결
- ✅ **세션 지속성**: 페이지 새로고침 시에도 로그인 상태 유지
- ✅ **자동 토큰 갱신**: 액세스 토큰 만료 시 자동 갱신
- ✅ **사용자 경험 개선**: 로그인 상태 실시간 표시

**기술적 개선사항:**
- JavaScript 기반 로그인 버튼으로 새 창 방지
- `session_state` 활용하여 세션 데이터 안정적 유지
- 자동 토큰 갱신 및 인증 상태 복원 기능
- 환경별 OAuth URL 자동 설정

## 🔧 주요 기능

### 1. AI 기반 문제 분류
- 고객 문의 자동 분석
- 문제 유형 자동 분류
- 신뢰도 점수 제공

### 2. 시나리오 기반 응답
- 사전 정의된 시나리오 매칭
- 조건별 해결책 제시
- 현장 출동 필요성 판단

### 3. 벡터 검색
- 유사 사례 자동 검색
- ChromaDB 기반 벡터 데이터베이스
- 실시간 유사도 계산

### 4. Gemini AI 응답 생성
- 고객 응답 이메일 자동 생성
- 조치 흐름 제시
- 요약 및 상세 분석

### 5. 다중 사용자 지원
- Google OAuth 인증
- 사용자별 이력 관리
- 권한 기반 접근 제어

## 🛠️ 기술 스택

- **AI 모델**: Google Gemini 1.5 Pro
- **웹 프레임워크**: Streamlit
- **벡터 데이터베이스**: ChromaDB
- **인증**: Google OAuth 2.0
- **데이터 저장**: SQLite + JSON
- **프로그래밍 언어**: Python

## 📋 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
export GOOGLE_API_KEY="your-api-key"
```

### 3. OAuth 설정
Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성 후 `.streamlit/secrets.toml`에 설정:

```toml
GOOGLE_CLIENT_ID = "your-client-id"
GOOGLE_CLIENT_SECRET = "your-client-secret"
GOOGLE_API_KEY = "your-api-key"
```

### 4. 앱 실행
```bash
streamlit run app.py
```

## 🔐 OAuth 설정 가이드

자세한 OAuth 설정 방법은 [oauth_setup_guide.md](oauth_setup_guide.md)를 참조하세요.

### 주요 설정 사항:
1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성
2. 승인된 리디렉션 URI 설정
3. OAuth 동의 화면 구성
4. Streamlit Secrets 설정
5. 앱 재배포

## 📊 사용 방법

### 1. 로그인
- 사이드바에서 "Google 계정으로 로그인" 클릭
- Google 계정으로 인증

### 2. 고객 문의 입력
- 고객 정보 및 문의 내용 입력
- 시스템이 자동으로 문제 유형 분류

### 3. AI 분석
- "AI 분석 요청" 버튼 클릭
- Gemini AI가 자동으로 분석 수행

### 4. 결과 확인
- AI 분석 결과 탭에서 상세 결과 확인
- 이메일 초안 복사 및 발송

## 🔍 문제 해결

### OAuth 관련 문제
- **새 창 방지**: JavaScript 기반 로그인 버튼 사용
- **세션 지속성**: `session_state` 활용하여 세션 데이터 유지
- **토큰 갱신**: 자동 토큰 갱신 기능 구현

### 디버깅 도구
OAuth 상태 확인을 위해 다음 URL 접속:
```
https://privkeeperp-response.streamlit.app/oauth_debug
```

## 📁 프로젝트 구조

```
streamlit_pratice/
├── app.py                      # 메인 애플리케이션
├── enhanced_google_auth.py     # OAuth 인증 모듈
├── classify_issue.py           # 문제 분류 모듈
├── scenario_db.py              # 시나리오 데이터베이스
├── vector_search.py            # 벡터 검색 모듈
├── gpt_handler.py              # Gemini AI 핸들러
├── database.py                 # 데이터베이스 모듈
├── multi_user_database.py      # 다중 사용자 DB
├── oauth_debug.py              # OAuth 디버깅 도구
├── requirements.txt            # 의존성 목록
├── oauth_setup_guide.md       # OAuth 설정 가이드
└── README.md                  # 프로젝트 문서
```

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

- **기술지원**: 02-678-1234
- **이메일**: support@privkeeper.com
- **긴급상황**: 010-3456-7890

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

---

© 2024 PrivKeeper P 장애 대응 자동화 시스템
