import streamlit as st
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# 페이지 설정
st.set_page_config(
    page_title="MongoDB 연결 테스트",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 MongoDB 연결 테스트")
st.markdown("Streamlit Cloud 환경에서 MongoDB Atlas 연결을 테스트합니다.")

# 환경변수 확인
st.header("📋 환경변수 확인")

# Streamlit Secrets 확인
st.subheader("Streamlit Secrets")
if "MONGODB_URI" in st.secrets:
    st.success("✅ MONGODB_URI가 Streamlit Secrets에 설정되어 있습니다.")
    mongodb_uri = st.secrets["MONGODB_URI"]
    # 민감 정보 마스킹
    masked_uri = mongodb_uri.replace(mongodb_uri.split('@')[0].split('//')[1], "***:***")
    st.code(f"MongoDB URI: {masked_uri}")
else:
    st.warning("⚠️ MONGODB_URI가 Streamlit Secrets에 설정되지 않았습니다.")

# 환경변수 확인
st.subheader("환경변수")
mongodb_uri_env = os.getenv("MONGODB_URI")
if mongodb_uri_env:
    st.success("✅ MONGODB_URI 환경변수가 설정되어 있습니다.")
    # 민감 정보 마스킹
    masked_uri_env = mongodb_uri_env.replace(mongodb_uri_env.split('@')[0].split('//')[1], "***:***")
    st.code(f"MongoDB URI: {masked_uri_env}")
else:
    st.warning("⚠️ MONGODB_URI 환경변수가 설정되지 않았습니다.")

# 연결 테스트
st.header("🔗 연결 테스트")

if st.button("MongoDB 연결 테스트 실행"):
    try:
        # 연결 문자열 선택
        if "MONGODB_URI" in st.secrets:
            connection_string = st.secrets["MONGODB_URI"]
            source = "Streamlit Secrets"
        elif mongodb_uri_env:
            connection_string = mongodb_uri_env
            source = "환경변수"
        else:
            st.error("❌ MongoDB URI가 설정되지 않았습니다.")
            st.stop()
        
        st.info(f"🔍 {source}에서 MongoDB URI를 사용하여 연결을 시도합니다...")
        
        # 연결 시도
        with st.spinner("MongoDB에 연결 중..."):
            client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
            
            # 연결 테스트
            client.admin.command('ping')
            st.success("✅ MongoDB 연결 성공!")
            
            # 데이터베이스 목록 조회
            db_list = client.list_database_names()
            st.write(f"📊 사용 가능한 데이터베이스: {len(db_list)}개")
            st.json(db_list[:10])  # 처음 10개만 표시
            
            # 연결 정보
            st.subheader("📊 연결 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("연결 상태", "✅ 연결됨")
                st.metric("데이터베이스 수", len(db_list))
            
            with col2:
                st.metric("연결 소스", source)
                st.metric("타임아웃", "10초")
            
            client.close()
            
    except ConnectionFailure as e:
        st.error(f"❌ MongoDB 연결 실패 (ConnectionFailure): {e}")
        st.info("💡 MongoDB Atlas 네트워크 접근 설정을 확인해주세요.")
        
    except ServerSelectionTimeoutError as e:
        st.error(f"❌ MongoDB 연결 실패 (ServerSelectionTimeoutError): {e}")
        st.info("💡 MongoDB Atlas 서버가 응답하지 않습니다. 네트워크 설정을 확인해주세요.")
        
    except Exception as e:
        st.error(f"❌ MongoDB 연결 실패: {e}")
        st.info("💡 연결 문자열 형식과 인증 정보를 확인해주세요.")

# 문제 해결 가이드
st.header("🛠️ 문제 해결 가이드")

with st.expander("MongoDB Atlas 설정 확인"):
    st.markdown("""
    ### 1. 네트워크 접근 설정
    - MongoDB Atlas 대시보드 → Network Access
    - IP 주소 추가: `0.0.0.0/0` (모든 IP 허용)
    
    ### 2. 데이터베이스 사용자 확인
    - MongoDB Atlas 대시보드 → Database Access
    - 사용자 권한: `readWrite` 또는 `atlasAdmin`
    
    ### 3. 연결 문자열 형식
    ```
    mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
    ```
    
    ### 4. Streamlit Cloud Secrets 설정
    - Streamlit Cloud 대시보드 → Secrets
    - `MONGODB_URI` 키로 연결 문자열 추가
    """)

with st.expander("일반적인 오류 해결"):
    st.markdown("""
    ### ConnectionFailure
    - 네트워크 접근 설정 확인
    - 방화벽 설정 확인
    
    ### ServerSelectionTimeoutError
    - MongoDB Atlas 서버 상태 확인
    - 연결 문자열의 클러스터 이름 확인
    
    ### AuthenticationFailed
    - 사용자명/비밀번호 확인
    - 데이터베이스 사용자 권한 확인
    """)

# 환경 정보
st.header("🌍 환경 정보")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Streamlit 환경")
    st.write(f"**Streamlit 버전**: {st.__version__}")
    st.write(f"**Python 버전**: {os.sys.version}")
    st.write(f"**운영체제**: {os.name}")

with col2:
    st.subheader("MongoDB 드라이버")
    try:
        import pymongo
        st.write(f"**PyMongo 버전**: {pymongo.__version__}")
    except ImportError:
        st.error("PyMongo가 설치되지 않았습니다.")
    
    try:
        import dns
        st.write(f"**DNS Python 버전**: {dns.__version__}")
    except ImportError:
        st.error("DNS Python이 설치되지 않았습니다.")

st.markdown("---")
st.markdown("💡 **참고**: 이 테스트는 Streamlit Cloud 환경에서 MongoDB Atlas 연결을 확인합니다.")
