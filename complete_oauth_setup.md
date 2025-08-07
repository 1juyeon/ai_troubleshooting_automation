# 완전한 OAuth 설정 가이드

## **1. Google Cloud Console 설정**

### **1-1. OAuth 동의 화면 완전 설정**

1. **Google Cloud Console** → **"API 및 서비스" → "OAuth 동의 화면"**

2. **사용자 유형**: **"외부"** 선택

3. **앱 정보 입력**:
   ```
   앱 이름: AI Troubleshooting Automation
   사용자 지원 이메일: (회사 이메일)
   개발자 연락처 정보: (회사 이메일)
   ```

4. **범위 추가** (중요!):
   - **"범위 추가 또는 삭제"** 클릭
   - 다음 범위들을 **모두** 추가:
     ```
     https://www.googleapis.com/auth/userinfo.email
     https://www.googleapis.com/auth/userinfo.profile
     https://www.googleapis.com/auth/generative-language.retrieval
     ```

5. **테스트 사용자 추가**:
   - **"테스트 사용자"** 섹션
   - **"테스트 사용자 추가"** 클릭
   - **본인 이메일** 정확히 입력
   - **사용할 다른 이메일들**도 추가

6. **저장**: **"저장 후 계속"** 클릭

### **1-2. OAuth 클라이언트 ID 확인**

1. **"API 및 서비스" → "사용자 인증 정보"**

2. **OAuth 2.0 클라이언트 ID** 확인:
   - 애플리케이션 유형: **"웹 애플리케이션"**
   - 승인된 리디렉션 URI: `https://aitroubleshootingautomation-fxxn77xinek2wohl5qhpw8.streamlit.app/`

### **1-3. API 키 생성**

1. **"사용자 인증 정보 만들기" → "API 키"**
2. 생성된 **API 키** 복사 (AIzaSy로 시작)

## **2. Streamlit Cloud Secrets 설정**

```toml
GOOGLE_CLIENT_ID = "your_client_id_here"
GOOGLE_CLIENT_SECRET = "your_client_secret_here"
GOOGLE_API_KEY = "your_api_key_here"
```

## **3. 앱 재배포**

1. **Streamlit Cloud**에서 앱 관리 페이지
2. **"Deploy"** 버튼 클릭
3. 배포 완료 대기

## **4. 테스트**

1. 앱 URL 접속
2. 사이드바에서 **"Google 계정으로 로그인"** 버튼 클릭
3. Google 계정으로 로그인

## **5. 403 오류 해결**

### **가장 흔한 원인:**
1. **테스트 사용자 미등록** (90%)
2. **범위 미추가** (5%)
3. **OAuth 동의 화면 미저장** (5%)

### **확인 사항:**
- ✅ 테스트 사용자에 본인 이메일 등록됨
- ✅ 범위 최소 1개 이상 추가됨
- ✅ "저장 후 계속" 클릭됨
- ✅ 앱 재배포 완료됨
