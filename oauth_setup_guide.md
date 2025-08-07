# Google OAuth 설정 완료 가이드

## **1. OAuth 동의 화면 설정**

### **필수 설정 항목:**
1. **앱 정보**:
   - ✅ 앱 이름: "AI Troubleshooting Automation"
   - ✅ 사용자 지원 이메일: (회사 이메일)
   - ✅ 개발자 연락처 정보: (회사 이메일)

2. **범위 (Scopes)**:
   - ✅ `https://www.googleapis.com/auth/userinfo.email`
   - ✅ `https://www.googleapis.com/auth/userinfo.profile`
   - ✅ `https://www.googleapis.com/auth/generative-language.retrieval`

3. **테스트 사용자**:
   - ✅ 사용할 이메일 주소들 추가

## **2. OAuth 클라이언트 ID 설정**

### **웹 애플리케이션 설정:**
- ✅ 애플리케이션 유형: "웹 애플리케이션"
- ✅ 승인된 리디렉션 URI: `https://aitroubleshootingautomation-fxxn77xinek2wohl5qhpw8.streamlit.app/`

## **3. Streamlit Cloud Secrets 설정**

```toml
GOOGLE_CLIENT_ID = "your_client_id_here"
GOOGLE_CLIENT_SECRET = "your_client_secret_here"
GOOGLE_API_KEY = "your_api_key_here"
```

## **4. 403 오류 해결 방법**

### **원인 1: OAuth 동의 화면 미완성**
- 모든 필수 항목이 입력되었는지 확인
- "저장 후 계속" 클릭했는지 확인

### **원인 2: 테스트 사용자 미등록**
- OAuth 동의 화면에서 테스트 사용자 추가
- 사용할 이메일 주소 정확히 입력

### **원인 3: 클라이언트 ID 오류**
- 올바른 클라이언트 ID가 Secrets에 설정되었는지 확인
- 웹 애플리케이션 클라이언트 ID 사용

### **원인 4: 리디렉션 URI 불일치**
- Google Cloud Console의 리디렉션 URI와 앱 URL이 정확히 일치하는지 확인
