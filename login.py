import streamlit as st
import os
import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs, urlparse
import datetime

# 페이지 설정
st.set_page_config(
    page_title="PrivKeeper P 로그인",
    page_icon="🔐",
    layout="wide"
)

class GoogleOAuthLogin:
    def __init__(self):
        """Google OAuth 로그인 전용 클래스"""
        # OAuth 설정 로드
        self.client_id = ""
        self.client_secret = ""
        
        try:
            if hasattr(st, 'secrets'):
                self.client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
                self.client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
                print(f"✅ OAuth 설정 로드 - Client ID: {bool(self.client_id)}")
            else:
                print("❌ st.secrets에 접근할 수 없습니다")
        except Exception as e:
            print(f"❌ OAuth 설정 로드 실패: {e}")
            try:
                self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
                self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
                print(f"✅ 환경변수에서 OAuth 설정 로드 - Client ID: {bool(self.client_id)}")
            except Exception as e2:
                print(f"❌ 환경변수에서도 로드 실패: {e2}")
        
        # 리다이렉트 URI 설정
        self.redirect_uri = "https://privkeeperp-response.streamlit.app/login"
        self.base_url = "https://privkeeperp-response.streamlit.app"
        
        # 세션 초기화
        self._init_session_state()
    
    def _init_session_state(self):
        """세션 상태 초기화"""
        if 'login_completed' not in st.session_state:
            st.session_state.login_completed = False
        if 'google_user' not in st.session_state:
            st.session_state.google_user = None
        if 'google_access_token' not in st.session_state:
            st.session_state.google_access_token = None
    
    def get_auth_url(self) -> str:
        """Google OAuth2 인증 URL 생성"""
        if not self.client_id:
            return ""
        
        # state 토큰 생성
        import secrets
        state = secrets.token_urlsafe(32)
        st.session_state.oauth_state = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }
        
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        query_string = urlencode(params, safe='')
        final_url = f"{auth_url}?{query_string}"
        
        return final_url
    
    def exchange_code_for_token(self, authorization_code: str, state: str) -> Optional[Dict[str, Any]]:
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
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"❌ 토큰 교환 실패: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """액세스 토큰으로 사용자 정보 가져오기"""
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(userinfo_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"❌ 사용자 정보 가져오기 실패: {e}")
            return None
    
    def handle_oauth_callback(self):
        """OAuth 콜백 처리"""
        code = st.query_params.get("code", None)
        state = st.query_params.get("state", None)
        
        if code and state:
            with st.spinner("🔐 로그인 처리 중..."):
                # 토큰 교환
                token_data = self.exchange_code_for_token(code, state)
                if token_data:
                    access_token = token_data.get('access_token')
                    user_info = self.get_user_info(access_token)
                    
                    if user_info:
                        # 세션에 사용자 정보 저장
                        st.session_state.google_user = user_info
                        st.session_state.google_access_token = access_token
                        st.session_state.login_completed = True
                        
                        st.success(f"✅ {user_info.get('name', '사용자')}님 로그인 성공!")
                        
                        # URL 파라미터 정리
                        st.query_params.clear()
                        
                        # 메인 페이지로 리다이렉트
                        st.markdown(f"""
                        <script>
                        window.location.href = "{self.base_url}";
                        </script>
                        """, unsafe_allow_html=True)
                        
                        return True
                    else:
                        st.error("❌ 사용자 정보를 가져올 수 없습니다.")
                else:
                    st.error("❌ 인증 토큰 교환에 실패했습니다.")
        
        return False
    
    def render_login_page(self):
        """로그인 페이지 렌더링"""
        # 헤더
        st.markdown("""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom:2rem;'>
            <h1>🔐 PrivKeeper P 로그인</h1>
            <p>Google 계정으로 로그인하여 시스템에 접근하세요</p>
        </div>
        """, unsafe_allow_html=True)
        
        # OAuth 콜백 처리
        if self.handle_oauth_callback():
            return
        
        # 로그인 버튼들
        if not self.client_id:
            st.error("❌ Google OAuth가 설정되지 않았습니다.")
            st.info("관리자에게 OAuth 설정을 요청하세요.")
            return
        
        auth_url = self.get_auth_url()
        if not auth_url:
            st.error("❌ OAuth 설정이 올바르지 않습니다.")
            return
        
        # 로그인 버튼들
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <a href="{auth_url}" target="_blank" style="
                background: linear-gradient(90deg, #4285f4 0%, #34a853 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-decoration: none;
                display: block;
                text-align: center;
            ">
                🔐 Google 계정으로 로그인
            </a>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4285f4;">
                <h4>📋 로그인 방법</h4>
                <ol style="margin: 0; padding-left: 20px;">
                    <li>위 버튼을 클릭하세요</li>
                    <li>새 창에서 Google 로그인을 완료하세요</li>
                    <li>로그인 완료 후 새 창을 닫으세요</li>
                    <li>이 페이지가 자동으로 메인 시스템으로 이동합니다</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        # 디버그 정보
        if st.checkbox("🔧 디버그 정보 표시"):
            st.json({
                "client_id_set": bool(self.client_id),
                "client_secret_set": bool(self.client_secret),
                "redirect_uri": self.redirect_uri,
                "auth_url_length": len(auth_url),
                "auth_url_preview": auth_url[:100] + "..." if len(auth_url) > 100 else auth_url
            })

# 메인 실행
if __name__ == "__main__":
    oauth_login = GoogleOAuthLogin()
    oauth_login.render_login_page()
