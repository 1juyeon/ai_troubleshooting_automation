"""
환경변수 설정 모듈
Streamlit Cloud의 secrets와 로컬 .streamlit/secrets.toml 파일을 지원합니다.
"""
import os
import streamlit as st

def get_secret(key, default=None):
    """
    Streamlit secrets 또는 환경변수에서 값을 가져옵니다.
    우선순위: Streamlit secrets > 환경변수 > 기본값
    """
    # Streamlit Cloud에서 실행 중인 경우 secrets 사용
    if hasattr(st, 'secrets') and st.secrets:
        return st.secrets.get(key, default)
    
    # 로컬 개발 환경에서는 환경변수 사용
    return os.getenv(key, default)

# API 키 설정 (환경변수 또는 Streamlit secrets에서만 로드)
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY") or get_secret("GEMINI_API_KEY")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
MONGODB_URI = get_secret("MONGODB_URI")
SOLAPI_API_KEY = get_secret("SOLAPI_API_KEY")
SOLAPI_API_SECRET = get_secret("SOLAPI_API_SECRET")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

# 설정 검증 함수
def validate_config():
    """필수 설정값들이 모두 있는지 확인합니다."""
    required_keys = [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET", 
        "GOOGLE_API_KEY",
        "MONGODB_URI",
        "SOLAPI_API_KEY",
        "SOLAPI_API_SECRET",
        "OPENAI_API_KEY"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not get_secret(key):
            missing_keys.append(key)
    
    if missing_keys:
        st.error(f"다음 설정값들이 누락되었습니다: {', '.join(missing_keys)}")
        st.info("로컬 개발을 위해서는 .env 파일을 생성하고 필요한 키들을 설정해주세요.")
        return False
    
    return True

# 로컬 개발용 .env 파일 생성 가이드
def create_env_template():
    """로컬 개발용 .env 파일 템플릿을 생성합니다."""
    env_template = """# Google OAuth 설정
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Google API 키 (Gemini용)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_google_api_key_here

# MongoDB 연결 정보
MONGODB_URI=your_mongodb_uri_here

# SOLAPI 설정
SOLAPI_API_KEY=your_solapi_api_key_here
SOLAPI_API_SECRET=your_solapi_api_secret_here

# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    return env_template
