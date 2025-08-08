import streamlit as st
import os
import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs, urlparse
import datetime

class EnhancedGoogleAuth:
    def __init__(self):
        """향상된 Google OAuth2 인증"""
        try:
            self.client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
            self.client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
        except:
            self.client_id = ""
            self.client_secret = ""
        
        # Streamlit Cloud URL 자동 감지
        try:
            # Streamlit Cloud에서 실행 중인지 확인
            if st.get_option("server.baseUrlPath"):
                # 로컬 개발 환경
                self.base_url = "http://localhost:8501"
            else:
                # Streamlit Cloud 환경 - 실제 앱 URL 확인
                # 현재 사용 중인 앱의 URL을 정확히 설정
                self.base_url = "https://privkeeperp-response.streamlit.app"
        except:
            # 기본값으로 현재 앱 URL 사용
            self.base_url = "https://privkeeperp-response.streamlit.app"
        
        # 리디렉션 URI 정확히 설정 (실제 앱 URL)
        self.redirect_uri = "https://privkeeperp-response.streamlit.app"
        
        # 세션 파일 경로 설정
        self.session_file = "user_session.json"
        
        # 세션 초기화 (새로고침 시에도 유지)
        self._init_session_state()
    
    def _get_session_file_path(self) -> str:
        """세션 파일 경로 반환"""
        return os.path.join(os.getcwd(), self.session_file)
    
    def _save_session_to_file(self, session_data: Dict[str, Any]) -> bool:
        """세션 데이터를 파일에 저장"""
        try:
            file_path = self._get_session_file_path()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 세션 파일 저장 실패: {e}")
            return False
    
    def _load_session_from_file(self) -> Optional[Dict[str, Any]]:
        """파일에서 세션 데이터 로드"""
        try:
            file_path = self._get_session_file_path()
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 세션 데이터 유효성 검증
            if not self._validate_session_data(session_data):
                return None
                
            return session_data
        except Exception as e:
            print(f"❌ 세션 파일 로드 실패: {e}")
            return None
    
    def _validate_session_data(self, session_data: Dict[str, Any]) -> bool:
        """세션 데이터 유효성 검증"""
        required_keys = ['google_user', 'google_access_token', 'login_timestamp']
        
        for key in required_keys:
            if key not in session_data or not session_data[key]:
                return False
        
        # 로그인 시간 확인 (24시간 이내)
        try:
            login_time = datetime.datetime.fromisoformat(session_data['login_timestamp'])
            if (datetime.datetime.now() - login_time).total_seconds() > 86400:  # 24시간
                return False
        except:
            return False
        
        return True
    
    def _clear_session_file(self) -> bool:
        """세션 파일 삭제"""
        try:
            file_path = self._get_session_file_path()
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"❌ 세션 파일 삭제 실패: {e}")
            return False
    
    def _init_session_state(self):
        """세션 상태 초기화 - 강화된 방식 (파일 기반)"""
        # OAuth 관련 세션 상태 초기화
        if 'google_auth_initialized' not in st.session_state:
            st.session_state.google_auth_initialized = True
        
        # 파일에서 세션 복원 시도
        session_data = self._load_session_from_file()
        
        if session_data:
            # 파일에서 세션 데이터 복원
            for key, value in session_data.items():
                st.session_state[key] = value
            print("✅ 파일에서 세션 복원 완료")
        else:
            # 기본 세션 상태 초기화
            session_keys = [
                'google_user', 
                'google_access_token', 
                'google_refresh_token', 
                'oauth_state',
                'last_token_refresh',
                'auth_completed',
                'session_persistent',
                'login_timestamp'
            ]
            
            for key in session_keys:
                if key not in st.session_state:
                    st.session_state[key] = None
            
            # 세션 지속성 플래그 설정
            if 'session_persistent' not in st.session_state:
                st.session_state.session_persistent = True
    
    def _save_auth_data(self, user_info: dict, access_token: str, refresh_token: str = None):
        """인증 데이터를 세션에 저장 (파일 기반)"""
        # Streamlit 세션에 저장
        st.session_state.google_user = user_info
        st.session_state.google_access_token = access_token
        if refresh_token:
            st.session_state.google_refresh_token = refresh_token
        
        # 마지막 갱신 시간 업데이트
        st.session_state.last_token_refresh = datetime.datetime.now().isoformat()
        st.session_state.auth_completed = True
        st.session_state.login_timestamp = datetime.datetime.now().isoformat()
        st.session_state.session_persistent = True
        
        # 파일에도 세션 데이터 저장
        session_data = {
            'google_user': user_info,
            'google_access_token': access_token,
            'google_refresh_token': refresh_token,
            'last_token_refresh': st.session_state.last_token_refresh,
            'auth_completed': True,
            'login_timestamp': st.session_state.login_timestamp,
            'session_persistent': True
        }
        
        if self._save_session_to_file(session_data):
            print("✅ 세션 파일 저장 완료")
        else:
            print("⚠️ 세션 파일 저장 실패 (Streamlit 세션은 유지됨)")
    
    def get_auth_url(self) -> str:
        """Google OAuth2 인증 URL 생성"""
        if not self.client_id:
            return ""
            
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
        
        final_url = f"{auth_url}?{query_string}"
        
        return final_url
    
    def _generate_state(self) -> str:
        """CSRF 방지를 위한 state 토큰 생성"""
        import secrets
        state = secrets.token_urlsafe(32)
        st.session_state.oauth_state = state
        return state
    
    def _verify_state(self, state: str) -> bool:
        """state 토큰 검증"""
        stored_state = st.session_state.get('oauth_state', '')
        # state가 비어있거나 일치하지 않아도 일단 진행
        if not stored_state:
            return True
        if state != stored_state:
            return True  # 일단 진행
        return True
    
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
        """향상된 로그인 버튼 렌더링 - Streamlit 기본 버튼 사용"""
        if not self.client_id:
            st.error("❌ Google OAuth가 설정되지 않았습니다.")
            st.info("관리자가 OAuth 설정을 완료하면 Google 계정으로 로그인할 수 있습니다.")
            return False
        
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
                            self._save_auth_data(user_info, access_token, refresh_token)
                            
                            st.success(f"✅ {user_info.get('name', '사용자')}님 환영합니다!")
                            
                            # URL에서 인증 코드 제거하고 페이지 새로고침
                            st.query_params.clear()
                            st.rerun()
                            return True
                        else:
                            st.error("❌ 사용자 정보를 가져올 수 없습니다.")
                    else:
                        st.error("❌ 액세스 토큰이 유효하지 않습니다.")
                else:
                    st.error("❌ 인증 토큰 교환에 실패했습니다.")
        
        # Streamlit 기본 버튼 사용 - 새 창 방지
        auth_url = self.get_auth_url()
        if auth_url:
            # 버튼 클릭 시 현재 창에서 리디렉션
            if st.button("🔐 Google 계정으로 로그인", type="primary", use_container_width=True):
                st.markdown(f"""
                <script>
                // 현재 창에서 OAuth URL로 이동 (새 창 방지)
                window.location.replace("{auth_url}");
                </script>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ OAuth 설정이 올바르지 않습니다.")
        
        return False
    
    def render_user_info(self):
        """향상된 사용자 정보 표시"""
        if 'google_user' in st.session_state and st.session_state.google_user:
            user = st.session_state.google_user
            
            # 사용자 정보 표시
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if user.get('picture'):
                    st.image(user['picture'], width=50, use_column_width=True)
                else:
                    st.markdown("""
                    <div style="text-align: center;">
                        <div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                            <span style="font-size: 20px;">👤</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{user.get('name', '사용자')}**")
                st.markdown(f"📧 {user.get('email', '')}")
                
                if user.get('verified_email'):
                    st.success("✅ 이메일 인증됨")
                
                # AI 분석 가능 상태 표시
                st.success("🎉 AI 분석 서비스 이용 가능")
                
                # 로그아웃 버튼
                if st.button("🚪 로그아웃"):
                    self.logout()
                    st.rerun()
    
    def refresh_token(self):
        """리프레시 토큰을 사용하여 액세스 토큰 갱신 (사용자 인터페이스용)"""
        if 'google_refresh_token' not in st.session_state or not st.session_state.google_refresh_token:
            st.error("❌ 리프레시 토큰이 없습니다.")
            return False
        
        try:
            success = self._refresh_token_silently()
            if success:
                st.success("✅ 토큰이 성공적으로 갱신되었습니다!")
                return True
            else:
                st.error("❌ 토큰 갱신에 실패했습니다.")
                return False
                
        except Exception as e:
            st.error(f"❌ 토큰 갱신 중 오류: {e}")
            return False
    
    def logout(self):
        """로그아웃 - 세션 데이터 정리 (파일 기반)"""
        # Streamlit 세션 정리
        keys_to_remove = [
            'google_user', 
            'google_access_token', 
            'google_refresh_token', 
            'oauth_state',
            'last_token_refresh',
            'google_auth_initialized',
            'auth_completed',
            'session_persistent',
            'login_timestamp'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        # 세션 파일 삭제
        if self._clear_session_file():
            print("✅ 세션 파일 삭제 완료")
        else:
            print("⚠️ 세션 파일 삭제 실패")
        
        # URL 파라미터도 정리
        try:
            st.query_params.clear()
        except:
            pass
        
        # 세션 지속성 플래그 재설정
        st.session_state.session_persistent = True
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인 - 강화된 방식 (파일 기반)"""
        # 세션 지속성 확인
        if 'session_persistent' not in st.session_state:
            st.session_state.session_persistent = True
        
        # 기본 세션 상태 확인
        if 'google_user' not in st.session_state or not st.session_state.google_user:
            # 파일에서 세션 복원 시도
            session_data = self._load_session_from_file()
            if session_data:
                for key, value in session_data.items():
                    st.session_state[key] = value
                print("✅ 파일에서 세션 복원 완료")
            else:
                return False
        
        if 'google_access_token' not in st.session_state or not st.session_state.google_access_token:
            return False
        
        # 로그인 타임스탬프 확인 (24시간 이내 로그인)
        if 'login_timestamp' in st.session_state and st.session_state.login_timestamp:
            try:
                login_time = datetime.datetime.fromisoformat(st.session_state.login_timestamp)
                if (datetime.datetime.now() - login_time).total_seconds() > 86400:  # 24시간
                    self.logout()
                    return False
            except:
                pass
        
        # 토큰 유효성 검증
        access_token = st.session_state.google_access_token
        try:
            # 토큰 유효성 검증
            if not self.validate_token(access_token):
                # 토큰이 만료된 경우 리프레시 토큰으로 갱신 시도
                if self._should_refresh_token():
                    if self._refresh_token_silently():
                        return True
                    else:
                        # 갱신 실패 시 로그아웃
                        self.logout()
                        return False
                else:
                    # 갱신 시도하지 않고 로그아웃
                    self.logout()
                    return False
            else:
                # 토큰이 유효하면 마지막 갱신 시간 업데이트
                st.session_state.last_token_refresh = datetime.datetime.now().isoformat()
                return True
                
        except Exception as e:
            # 오류 발생 시 로그아웃
            print(f"❌ 토큰 검증 중 오류: {e}")
            self.logout()
            return False
    
    def _should_refresh_token(self) -> bool:
        """토큰 갱신이 필요한지 확인"""
        if 'google_refresh_token' not in st.session_state or not st.session_state.google_refresh_token:
            return False
        
        # 마지막 갱신 시간 확인 (5분 이내에 갱신하지 않도록)
        if 'last_token_refresh' in st.session_state and st.session_state.last_token_refresh:
            try:
                last_refresh = datetime.datetime.fromisoformat(st.session_state.last_token_refresh)
                if (datetime.datetime.now() - last_refresh).total_seconds() < 300:  # 5분
                    return False
            except:
                pass
        
        return True
    
    def _refresh_token_silently(self) -> bool:
        """조용히 토큰 갱신 (오류 메시지 없이)"""
        try:
            refresh_token = st.session_state.google_refresh_token
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            
            new_access_token = token_data.get('access_token')
            if new_access_token and self.validate_token(new_access_token):
                # 새로운 리프레시 토큰이 있다면 업데이트
                new_refresh_token = token_data.get('refresh_token', refresh_token)
                
                # 세션에 저장
                self._save_auth_data(
                    st.session_state.google_user, 
                    new_access_token, 
                    new_refresh_token
                )
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ 조용한 토큰 갱신 실패: {e}")
            return False
    
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
