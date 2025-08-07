import streamlit as st
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json
from typing import Dict, Any, Optional

class GoogleAuthHandler:
    def __init__(self):
        """Google OAuth 인증 핸들러 초기화"""
        self.SCOPES = [
            'https://www.googleapis.com/auth/generative-language.retrieval',
            'https://www.googleapis.com/auth/cloud-platform'
        ]
        self.credentials = None
        self.token_file = 'token.pickle'
        
    def get_credentials(self) -> Optional[Credentials]:
        """Google 인증 정보 가져오기"""
        # 토큰 파일에서 기존 인증 정보 로드
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # 인증 정보가 없거나 만료된 경우
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                except Exception as e:
                    print(f"토큰 갱신 실패: {e}")
                    self.credentials = None
            
            # 새로운 인증 정보가 필요한 경우
            if not self.credentials:
                return None
                
        return self.credentials
    
    def save_credentials(self, credentials: Credentials):
        """인증 정보 저장"""
        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(credentials, token)
            self.credentials = credentials
            return True
        except Exception as e:
            print(f"인증 정보 저장 실패: {e}")
            return False
    
    def clear_credentials(self):
        """인증 정보 삭제"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            self.credentials = None
            return True
        except Exception as e:
            print(f"인증 정보 삭제 실패: {e}")
            return False
    
    def get_auth_url(self) -> str:
        """OAuth 인증 URL 생성"""
        try:
            # OAuth 클라이언트 설정
            client_config = {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8501"]
                }
            }
            
            flow = InstalledAppFlow.from_client_config(
                client_config, 
                scopes=self.SCOPES
            )
            
            # 인증 URL 생성
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return auth_url
            
        except Exception as e:
            print(f"인증 URL 생성 실패: {e}")
            return ""
    
    def handle_auth_callback(self, authorization_response: str) -> bool:
        """OAuth 콜백 처리"""
        try:
            # OAuth 클라이언트 설정
            client_config = {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8501"]
                }
            }
            
            flow = InstalledAppFlow.from_client_config(
                client_config, 
                scopes=self.SCOPES
            )
            
            # 인증 코드로 토큰 교환
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            
            # 인증 정보 저장
            return self.save_credentials(credentials)
            
        except Exception as e:
            print(f"인증 콜백 처리 실패: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        credentials = self.get_credentials()
        return credentials is not None and credentials.valid
    
    def get_user_info(self) -> Dict[str, Any]:
        """사용자 정보 가져오기"""
        if not self.is_authenticated():
            return {}
        
        try:
            # Google People API를 사용하여 사용자 정보 가져오기
            from googleapiclient.discovery import build
            
            service = build('oauth2', 'v2', credentials=self.credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                'email': user_info.get('email', ''),
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', ''),
                'verified_email': user_info.get('verified_email', False)
            }
            
        except Exception as e:
            print(f"사용자 정보 가져오기 실패: {e}")
            return {}
    
    def get_api_key_from_credentials(self) -> Optional[str]:
        """인증 정보에서 API 키 추출 (실제로는 별도 설정 필요)"""
        # 실제 구현에서는 Google Cloud Console에서 API 키를 별도로 설정해야 함
        # 여기서는 환경변수에서 가져오는 방식 사용
        return os.getenv("GOOGLE_API_KEY")
