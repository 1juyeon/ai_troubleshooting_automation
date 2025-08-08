# Google OAuth 설정 가이드

## 🔧 문제 해결

### 1. 새 창에서 실행되는 문제 해결

**문제:** Google 로그인 시 새 창이 열리는 문제

**해결 방법:**
- ✅ JavaScript 기반 로그인 버튼으로 변경
- ✅ `window.location.href` 사용하여 현재 창에서 리디렉션
- ✅ `preventDefault()` 사용하여 기본 동작 방지

### 2. 페이지 새로고침시 로그아웃 문제 해결

**문제:** 페이지 새로고침 시 로그인 상태가 사라지는 문제

**해결 방법:**
- ✅ `session_state` 활용하여 세션 데이터 유지
- ✅ 토큰 자동 갱신 기능 추가
- ✅ 세션 지속성 플래그 설정
- ✅ 인증 상태 자동 복원

## 📋 설정 단계

### 1. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. **API 및 서비스** → **사용자 인증 정보**
4. **사용자 인증 정보 만들기** → **OAuth 2.0 클라이언트 ID**
5. 애플리케이션 유형: **웹 애플리케이션** 선택

### 2. 승인된 리디렉션 URI 설정

**Streamlit Cloud 환경:**
```
https://privkeeperp-response.streamlit.app
```

**로컬 개발 환경:**
```
http://localhost:8501
```

### 3. OAuth 동의 화면 설정

1. **OAuth 동의 화면** 탭으로 이동
2. **외부** 선택
3. 필수 정보 입력:
   - 앱 이름
   - 사용자 지원 이메일
   - 개발자 연락처 정보
4. **범위 (Scopes)** 추가:
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
5. **테스트 사용자**에 본인 이메일 추가
6. **저장 후 계속** 클릭

### 4. Streamlit Secrets 설정

**Streamlit Cloud:**
1. 앱 관리 페이지에서 **Settings** 클릭
2. **Secrets** 섹션에서 다음 추가:

```toml
GOOGLE_CLIENT_ID = "your-client-id-here"
GOOGLE_CLIENT_SECRET = "your-client-secret-here"
GOOGLE_API_KEY = "your-api-key-here"
```

**로컬 개발:**
1. `.streamlit/secrets.toml` 파일 생성
2. 위와 동일한 내용 추가

### 5. 앱 재배포

1. Streamlit Cloud에서 **Deploy** 버튼 클릭
2. 배포 완료 후 앱 URL 접속
3. 사이드바에서 **Google 계정으로 로그인** 버튼 테스트

## 🔍 문제 진단

### 디버깅 도구 사용

앱에 다음 URL로 접속하여 OAuth 상태 확인:
```
https://privkeeperp-response.streamlit.app/oauth_debug
```

### 일반적인 오류 및 해결책

**403 오류:**
- OAuth 동의 화면에서 **저장 후 계속** 클릭 확인
- 테스트 사용자에 이메일 정확히 등록 확인
- 범위 (Scopes) 최소 1개 이상 추가 확인

**리디렉션 URI 오류:**
- Google Cloud Console의 리디렉션 URI와 앱 URL 정확히 일치하는지 확인
- 끝에 슬래시(/) 제거 확인

**토큰 만료 오류:**
- 자동 토큰 갱신 기능이 작동하는지 확인
- 리프레시 토큰이 올바르게 저장되는지 확인

## 🚀 개선 사항

### 최근 업데이트

1. **새 창 방지:**
   - JavaScript 기반 로그인 버튼 구현
   - 현재 창에서 OAuth 진행

2. **세션 지속성:**
   - `session_state` 활용하여 세션 데이터 유지
   - 페이지 새로고침 시에도 로그인 상태 유지
   - 자동 토큰 갱신 기능

3. **사용자 경험 개선:**
   - 로그인 상태 실시간 표시
   - 자동 인증 상태 복원
   - 오류 메시지 개선

## 📞 지원

문제가 지속되는 경우:
1. 디버깅 도구 사용하여 상태 확인
2. Google Cloud Console 설정 재확인
3. 앱 재배포 후 재테스트
