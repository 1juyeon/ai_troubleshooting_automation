import streamlit as st
import requests
from urllib.parse import urlencode

def debug_oauth_setup():
    """OAuth 설정 디버깅 도구"""
    
    st.markdown("## 🔧 OAuth 설정 디버깅")
    
    # 1. 클라이언트 ID 확인
    client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    
    st.markdown("### 1. Secrets 설정 확인")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if client_id:
            st.success("✅ 클라이언트 ID 설정됨")
            st.code(client_id[:20] + "...", language="text")
        else:
            st.error("❌ 클라이언트 ID 미설정")
    
    with col2:
        if client_secret:
            st.success("✅ 클라이언트 보안 비밀번호 설정됨")
            st.code(client_secret[:10] + "...", language="text")
        else:
            st.error("❌ 클라이언트 보안 비밀번호 미설정")
    
    with col3:
        if api_key:
            st.success("✅ API 키 설정됨")
            st.code(api_key[:10] + "...", language="text")
        else:
            st.error("❌ API 키 미설정")
    
    # 2. OAuth URL 생성 테스트
    st.markdown("### 2. OAuth URL 생성 테스트")
    
    if client_id:
        redirect_uri = "https://aitroubleshootingautomation-fxxn77xinek2wohl5qhpw8.streamlit.app/"
        
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        query_string = urlencode(params)
        full_auth_url = f"{auth_url}?{query_string}"
        
        st.success("✅ OAuth URL 생성됨")
        st.code(full_auth_url, language="text")
        
        # URL 테스트 버튼
        if st.button("🔗 OAuth URL 테스트"):
            st.markdown(f"[OAuth URL 테스트]({full_auth_url})")
    
    # 3. 문제 해결 가이드
    st.markdown("### 3. 403 오류 해결 체크리스트")
    
    st.markdown("""
    #### Google Cloud Console에서 확인:
    1. **OAuth 동의 화면** → **"저장 후 계속"** 클릭했는지 확인
    2. **테스트 사용자**에 본인 이메일이 정확히 등록되어 있는지 확인
    3. **범위 (Scopes)** 최소 1개 이상 추가했는지 확인:
       - `https://www.googleapis.com/auth/userinfo.email`
       - `https://www.googleapis.com/auth/userinfo.profile`
    
    #### 리디렉션 URI 확인:
    - Google Cloud Console: `https://aitroubleshootingautomation-fxxn77xinek2wohl5qhpw8.streamlit.app/`
    - 앱 URL과 정확히 일치하는지 확인
    
    #### 앱 재배포:
    - Streamlit Cloud에서 **"Deploy"** 버튼 클릭
    - 배포 완료 후 다시 테스트
    """)
    
    # 4. 수동 테스트
    st.markdown("### 4. 수동 테스트")
    
    if st.button("🔄 앱 재배포 안내"):
        st.info("""
        1. Streamlit Cloud에서 앱 관리 페이지로 이동
        2. "Deploy" 버튼 클릭
        3. 배포 완료 후 앱 URL 접속
        4. 사이드바에서 "Google 계정으로 로그인" 버튼 클릭
        """)

if __name__ == "__main__":
    debug_oauth_setup()
