import streamlit as st
import os
import requests
from typing import Dict, Any, Optional

class SimpleGoogleAuth:
    def __init__(self):
        """간단한 Google OAuth 인증"""
        try:
            self.client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
            self.client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
        except:
            # secrets 파일이 없거나 설정되지 않은 경우
            self.client_id = ""
            self.client_secret = ""
        
        self.redirect_uri = "https://aitroubleshootingautomation-fxxn77xinek2wohl5qhpw8.streamlit.app/"
        
    def get_auth_url(self) -> str:
        """Google OAuth 인증 URL 생성"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        
        return f"{auth_url}?{query_string}"
    
    def exchange_code_for_token(self, authorization_code: str) -> Optional[Dict[str, Any]]:
        """인증 코드를 액세스 토큰으로 교환"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"토큰 교환 실패: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """액세스 토큰으로 사용자 정보 가져오기"""
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(userinfo_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"사용자 정보 가져오기 실패: {e}")
            return None
    
    def render_login_button(self):
        """로그인 버튼 렌더링"""
        if not self.client_id:
            st.error("Google OAuth 클라이언트 ID가 설정되지 않았습니다.")
            return False
        
        # URL 파라미터에서 인증 코드 확인
        code = st.query_params.get("code", None)
        
        if code:
            # 인증 코드를 토큰으로 교환
            token_data = self.exchange_code_for_token(code)
            if token_data:
                access_token = token_data.get('access_token')
                user_info = self.get_user_info(access_token)
                
                if user_info:
                    # 세션에 사용자 정보 저장
                    st.session_state.google_user = user_info
                    st.session_state.google_access_token = access_token
                    st.success(f"✅ {user_info.get('name', '사용자')}님 환영합니다!")
                    
                    # URL에서 인증 코드 제거
                    st.query_params.clear()
                    return True
        
        # 로그인 버튼 표시
        auth_url = self.get_auth_url()
        st.markdown(f"""
        <a href="{auth_url}" target="_self">
            <button style="
                background-color: #4285f4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <img src="https://developers.google.com/identity/images/g-logo.png" width="20" height="20">
                Google 계정으로 로그인
            </button>
        </a>
        """, unsafe_allow_html=True)
        
        return False
    
    def render_user_info(self):
        """사용자 정보 표시"""
        if 'google_user' in st.session_state:
            user = st.session_state.google_user
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if user.get('picture'):
                    st.image(user['picture'], width=50)
                else:
                    st.write("👤")
            
            with col2:
                st.write(f"**{user.get('name', '사용자')}**")
                st.write(f"📧 {user.get('email', '')}")
                
                if st.button("로그아웃"):
                    self.logout()
                    st.rerun()
    
    def logout(self):
        """로그아웃"""
        if 'google_user' in st.session_state:
            del st.session_state.google_user
        if 'google_access_token' in st.session_state:
            del st.session_state.google_access_token
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        return 'google_user' in st.session_state
    
    def get_user_email(self) -> str:
        """사용자 이메일 가져오기"""
        if self.is_authenticated():
            return st.session_state.google_user.get('email', '')
        return ""
    
    def get_user_name(self) -> str:
        """사용자 이름 가져오기"""
        if self.is_authenticated():
            return st.session_state.google_user.get('name', '')
        return ""
