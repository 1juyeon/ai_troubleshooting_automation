import streamlit as st
import os
import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs, urlparse

class EnhancedGoogleAuth:
    def __init__(self):
        """향상된 Google OAuth2 인증"""
        try:
            self.client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
            self.client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
        except:
            self.client_id = ""
            self.client_secret = ""
        
        # Streamlit Cloud URL 또는 로컬 URL
        try:
            self.base_url = st.get_option("server.baseUrlPath")
        except:
            self.base_url = "https://privkeeperp-response.streamlit.app/"
        
        # 리디렉션 URI 정확히 설정
        self.redirect_uri = "https://privkeeperp-response.streamlit.app/"
        
    def get_auth_url(self) -> str:
        """Google OAuth2 인증 URL 생성"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': self._generate_state()
        }
        
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        query_string = urlencode(params)
        
        return f"{auth_url}?{query_string}"
    
    def _generate_state(self) -> str:
        """CSRF 방지를 위한 state 토큰 생성"""
        import secrets
        state = secrets.token_urlsafe(32)
        st.session_state.oauth_state = state
        return state
    
    def _verify_state(self, state: str) -> bool:
        """state 토큰 검증"""
        return state == st.session_state.get('oauth_state', '')
    
    def exchange_code_for_token(self, authorization_code: str, state: str) -> Optional[Dict[str, Any]]:
        """인증 코드를 액세스 토큰으로 교환"""
        # state 검증
        if not self._verify_state(state):
            st.error("❌ 인증 상태 검증 실패")
            return None
        
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
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 토큰 교환 실패: {e}")
            return None
        except Exception as e:
            st.error(f"❌ 토큰 교환 중 오류: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """액세스 토큰으로 사용자 정보 가져오기"""
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(userinfo_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 사용자 정보 가져오기 실패: {e}")
            return None
        except Exception as e:
            st.error(f"❌ 사용자 정보 가져오기 중 오류: {e}")
            return None
    
    def validate_token(self, access_token: str) -> bool:
        """액세스 토큰 유효성 검증"""
        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v1/tokeninfo",
                params={'access_token': access_token},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def render_login_button(self):
        """향상된 로그인 버튼 렌더링"""
        if not self.client_id:
            st.error("❌ Google OAuth 클라이언트 ID가 설정되지 않았습니다.")
            st.info("Streamlit Cloud Secrets에 GOOGLE_CLIENT_ID를 설정해주세요.")
            return False
        
        # 디버깅 정보 표시
        st.info(f"🔧 디버깅: 클라이언트 ID 설정됨")
        st.info(f"🔧 디버깅: 리디렉션 URI: {self.redirect_uri}")
        
        # OAuth URL 생성 테스트
        auth_url = self.get_auth_url()
        st.info(f"🔧 디버깅: OAuth URL 생성됨")
        
        # URL 파라미터 확인
        st.info(f"🔧 디버깅: 생성된 OAuth URL:")
        st.code(auth_url, language="text")
        
        if st.button("🔗 OAuth URL 직접 테스트"):
            st.markdown(f"[OAuth URL 직접 테스트]({auth_url})")
        
        # URL 파라미터에서 인증 코드 확인
        code = st.query_params.get("code", None)
        state = st.query_params.get("state", None)
        
        if code and state:
            with st.spinner("🔐 인증 처리 중..."):
                # 인증 코드를 토큰으로 교환
                token_data = self.exchange_code_for_token(code, state)
                if token_data:
                    access_token = token_data.get('access_token')
                    refresh_token = token_data.get('refresh_token')
                    
                    # 토큰 유효성 검증
                    if self.validate_token(access_token):
                        user_info = self.get_user_info(access_token)
                        
                        if user_info:
                            # 세션에 사용자 정보 저장
                            st.session_state.google_user = user_info
                            st.session_state.google_access_token = access_token
                            if refresh_token:
                                st.session_state.google_refresh_token = refresh_token
                            
                            st.success(f"✅ {user_info.get('name', '사용자')}님 환영합니다!")
                            
                            # URL에서 인증 코드 제거
                            st.query_params.clear()
                            return True
                        else:
                            st.error("❌ 사용자 정보를 가져올 수 없습니다.")
                    else:
                        st.error("❌ 액세스 토큰이 유효하지 않습니다.")
                else:
                    st.error("❌ 인증 토큰 교환에 실패했습니다.")
        
        # 로그인 버튼 표시
        auth_url = self.get_auth_url()
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="{auth_url}" target="_self">
                <button style="
                    background: linear-gradient(45deg, #4285f4, #34a853);
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 12px;
                    box-shadow: 0 4px 8px rgba(66, 133, 244, 0.3);
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(66, 133, 244, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 8px rgba(66, 133, 244, 0.3)'">
                    <img src="https://developers.google.com/identity/images/g-logo.png" width="24" height="24" style="filter: brightness(0) invert(1);">
                    Google 계정으로 로그인
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("🔐 Google 계정으로 로그인하여 AI 분석 서비스를 이용하세요.")
        return False
    
    def render_user_info(self):
        """향상된 사용자 정보 표시"""
        if 'google_user' in st.session_state:
            user = st.session_state.google_user
            
            st.markdown("### 👤 로그인된 사용자")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if user.get('picture'):
                    st.image(user['picture'], width=60, use_column_width=True)
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 10px;">
                        <div style="width: 60px; height: 60px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                            <span style="font-size: 24px;">👤</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{user.get('name', '사용자')}**")
                st.markdown(f"📧 {user.get('email', '')}")
                
                if user.get('verified_email'):
                    st.markdown("✅ 이메일 인증됨")
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.button("🚪 로그아웃", use_container_width=True):
                        self.logout()
                        st.rerun()
                
                with col4:
                    if st.button("🔄 토큰 갱신", use_container_width=True):
                        self.refresh_token()
    
    def refresh_token(self):
        """리프레시 토큰을 사용하여 액세스 토큰 갱신"""
        if 'google_refresh_token' not in st.session_state:
            st.error("❌ 리프레시 토큰이 없습니다.")
            return
        
        refresh_token = st.session_state.google_refresh_token
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            
            new_access_token = token_data.get('access_token')
            if new_access_token and self.validate_token(new_access_token):
                st.session_state.google_access_token = new_access_token
                st.success("✅ 토큰이 성공적으로 갱신되었습니다!")
            else:
                st.error("❌ 토큰 갱신에 실패했습니다.")
                
        except Exception as e:
            st.error(f"❌ 토큰 갱신 중 오류: {e}")
    
    def logout(self):
        """로그아웃"""
        keys_to_remove = ['google_user', 'google_access_token', 'google_refresh_token', 'oauth_state']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        if 'google_user' not in st.session_state:
            return False
        
        # 토큰 유효성 검증
        access_token = st.session_state.get('google_access_token')
        if access_token and not self.validate_token(access_token):
            # 토큰이 만료된 경우 갱신 시도
            if 'google_refresh_token' in st.session_state:
                self.refresh_token()
                return 'google_access_token' in st.session_state
            else:
                # 갱신 토큰이 없으면 로그아웃
                self.logout()
                return False
        
        return True
    
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
    
    def get_access_token(self) -> str:
        """액세스 토큰 가져오기"""
        if self.is_authenticated():
            return st.session_state.get('google_access_token', '')
        return ""
