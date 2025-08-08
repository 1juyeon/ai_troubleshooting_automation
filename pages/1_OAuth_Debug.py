import streamlit as st
import os
import json
from datetime import datetime

def debug_oauth_session():
    """OAuth 세션 상태 디버깅"""
    st.markdown("## 🔍 OAuth 세션 디버깅")
    
    # 현재 세션 상태 확인
    oauth_keys = [
        'google_user', 
        'google_access_token', 
        'google_refresh_token', 
        'oauth_state',
        'last_token_refresh',
        'auth_completed',
        'login_timestamp',
        'session_persistent',
        'auth_checked',
        'login_success',
        'user_authenticated',
        'google_auth_initialized'
    ]
    
    st.markdown("### 📊 세션 상태")
    
    for key in oauth_keys:
        value = st.session_state.get(key, "Not set")
        if key in ['google_access_token', 'google_refresh_token'] and value:
            # 토큰은 일부만 표시
            display_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
        else:
            display_value = str(value)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"**{key}:**")
        with col2:
            st.code(display_value)
    
    # 환경 변수 확인
    st.markdown("### 🔧 환경 설정")
    
    env_vars = {
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID', 'Not set'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET', 'Not set'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY', 'Not set')
    }
    
    for key, value in env_vars.items():
        if 'SECRET' in key or 'KEY' in key:
            display_value = f"{value[:10]}..." if value != 'Not set' else 'Not set'
        else:
            display_value = value
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"**{key}:**")
        with col2:
            st.code(display_value)
    
    # Streamlit secrets 확인
    st.markdown("### 🔐 Streamlit Secrets")
    
    try:
        secrets = {
            'GOOGLE_CLIENT_ID': st.secrets.get('GOOGLE_CLIENT_ID', 'Not set'),
            'GOOGLE_CLIENT_SECRET': st.secrets.get('GOOGLE_CLIENT_SECRET', 'Not set')
        }
        
        for key, value in secrets.items():
            if 'SECRET' in key:
                display_value = f"{value[:10]}..." if value != 'Not set' else 'Not set'
            else:
                display_value = value
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**{key}:**")
            with col2:
                st.code(display_value)
    except Exception as e:
        st.error(f"Secrets 접근 오류: {e}")
    
    # 세션 정리 버튼
    st.markdown("### 🧹 세션 정리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ OAuth 세션 정리"):
            for key in oauth_keys:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ OAuth 세션이 정리되었습니다!")
            st.rerun()
    
    with col2:
        if st.button("🔄 페이지 새로고침"):
            st.rerun()

def check_oauth_configuration():
    """OAuth 설정 상태 확인"""
    st.markdown("## ⚙️ OAuth 설정 확인")
    
    # 클라이언트 ID 확인
    client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    
    if not client_id:
        st.error("❌ Google Client ID가 설정되지 않았습니다.")
        st.info("""
        **설정 방법:**
        1. Streamlit Cloud의 앱 설정에서 Secrets 추가
        2. 또는 로컬에서 `.streamlit/secrets.toml` 파일 생성
        3. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성
        """)
        return False
    
    if not client_secret:
        st.error("❌ Google Client Secret이 설정되지 않았습니다.")
        return False
    
    st.success("✅ OAuth 설정이 완료되었습니다!")
    
    # 리디렉션 URI 확인
    st.markdown("### 🔗 리디렉션 URI 설정")
    
    # 현재 환경 확인
    try:
        current_url = st.get_option("server.baseUrlPath")
        if current_url and current_url != "":
            redirect_uri = "http://localhost:8501"
            environment = "로컬 개발 환경"
        else:
            redirect_uri = "https://privkeeperp-response.streamlit.app"
            environment = "Streamlit Cloud"
    except:
        redirect_uri = "https://privkeeperp-response.streamlit.app"
        environment = "Streamlit Cloud (기본값)"
    
    st.info(f"**현재 환경:** {environment}")
    st.info(f"**리디렉션 URI:** {redirect_uri}")
    
    st.markdown("""
    **Google Cloud Console 설정:**
    1. [Google Cloud Console](https://console.cloud.google.com/) 접속
    2. API 및 서비스 → 사용자 인증 정보
    3. OAuth 2.0 클라이언트 ID 선택
    4. 승인된 리디렉션 URI에 위 URI 추가
    """)
    
    return True

# 페이지 설정
st.set_page_config(
    page_title="OAuth 디버깅", 
    page_icon="🔍",
    layout="wide"
)

# 페이지 제목
st.title("🔍 OAuth 디버깅 도구")

# 메인 페이지로 돌아가기 버튼
st.link_button("🏠 메인 페이지로 돌아가기", "/", use_container_width=True)

# 탭 생성
tab1, tab2 = st.tabs(["📊 세션 디버깅", "⚙️ 설정 확인"])

with tab1:
    debug_oauth_session()

with tab2:
    check_oauth_configuration()
