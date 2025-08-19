import streamlit as st
import os
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(
    page_title="MongoDB 상태 확인",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 MongoDB 연결 상태 확인")
st.markdown("Streamlit Cloud 환경에서 MongoDB Atlas 연결 상태를 모니터링합니다.")

# MongoDB 핸들러 import 시도
try:
    from mongodb_handler import MongoDBHandler
    mongo_available = True
except ImportError:
    mongo_available = False
    st.error("❌ MongoDB 핸들러를 불러올 수 없습니다.")

# 환경변수 확인
st.header("📋 환경 설정 확인")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Streamlit Secrets")
    if "MONGODB_URI" in st.secrets:
        st.success("✅ MONGODB_URI 설정됨")
        mongodb_uri = st.secrets["MONGODB_URI"]
        # 민감 정보 마스킹
        try:
            masked_uri = mongodb_uri.replace(mongodb_uri.split('@')[0].split('//')[1], "***:***")
            st.code(f"MongoDB URI: {masked_uri}")
        except:
            st.code("MongoDB URI: 설정됨")
    else:
        st.warning("⚠️ MONGODB_URI 미설정")
        st.info("💡 Streamlit Cloud Secrets에 MONGODB_URI를 추가하세요")

with col2:
    st.subheader("환경변수")
    mongodb_uri_env = os.getenv("MONGODB_URI")
    if mongodb_uri_env:
        st.success("✅ MONGODB_URI 환경변수 설정됨")
        try:
            masked_uri_env = mongodb_uri_env.replace(mongodb_uri_env.split('@')[0].split('//')[1], "***:***")
            st.code(f"MongoDB URI: {masked_uri_env}")
        except:
            st.code("MongoDB URI: 환경변수 설정됨")
    else:
        st.warning("⚠️ MONGODB_URI 환경변수 미설정")

# MongoDB 연결 테스트
st.header("🔗 MongoDB 연결 테스트")

if mongo_available:
    if st.button("🚀 MongoDB 연결 테스트 실행", type="primary"):
        try:
            with st.spinner("MongoDB에 연결 중..."):
                # MongoDB 핸들러 초기화
                mongo_handler = MongoDBHandler()
                
                # 연결 테스트
                connection_test = mongo_handler.test_connection()
                
                if connection_test.get('success'):
                    st.success("✅ MongoDB 연결 성공!")
                    
                    # 연결 정보 표시
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        st.metric("연결 상태", "✅ 연결됨")
                        st.metric("현재 데이터베이스", connection_test.get('current_db', 'N/A'))
                        st.metric("컬렉션 수", len(connection_test.get('collections', [])))
                    
                    with col4:
                        st.metric("전체 데이터베이스 수", len(connection_test.get('databases', [])))
                        st.metric("연결 시간", datetime.now().strftime("%H:%M:%S"))
                        st.metric("연결 소스", "Streamlit Secrets" if "MONGODB_URI" in st.secrets else "환경변수")
                    
                    # 데이터베이스 목록
                    st.subheader("📊 사용 가능한 데이터베이스")
                    db_list = connection_test.get('databases', [])
                    if db_list:
                        st.json(db_list[:10])  # 처음 10개만 표시
                    else:
                        st.info("사용 가능한 데이터베이스가 없습니다.")
                    
                    # 컬렉션 목록
                    st.subheader("📁 현재 데이터베이스 컬렉션")
                    collections = connection_test.get('collections', [])
                    if collections:
                        st.json(collections)
                    else:
                        st.info("현재 데이터베이스에 컬렉션이 없습니다.")
                    
                    # 세션 상태에 MongoDB 핸들러 저장
                    st.session_state.mongodb_connected = True
                    st.session_state.mongo_handler = mongo_handler
                    
                else:
                    st.error(f"❌ MongoDB 연결 실패: {connection_test.get('message')}")
                    st.session_state.mongodb_connected = False
                    
        except Exception as e:
            st.error(f"❌ MongoDB 연결 테스트 실패: {e}")
            st.session_state.mongodb_connected = False
            
            # 오류 상세 정보
            with st.expander("🔍 오류 상세 정보"):
                st.code(str(e))
                
                # 일반적인 해결 방법 제시
                st.markdown("### 🛠️ 일반적인 해결 방법")
                st.markdown("""
                1. **Streamlit Cloud Secrets 확인**
                   - Streamlit Cloud 대시보드 → Secrets
                   - `MONGODB_URI` 키가 올바르게 설정되었는지 확인
                
                2. **MongoDB Atlas 설정 확인**
                   - Network Access: `0.0.0.0/0` 추가 (모든 IP 허용)
                   - Database Access: 사용자 권한 확인
                   - 연결 문자열 형식 확인
                
                3. **연결 문자열 형식**
                   ```
                   mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
                   ```
                """)
    
    # 현재 연결 상태 표시
    st.subheader("📊 현재 연결 상태")
    if st.session_state.get('mongodb_connected'):
        st.success("✅ MongoDB 연결됨")
        
        # 연결 해제 버튼
        if st.button("🔌 연결 해제"):
            st.session_state.mongodb_connected = False
            if 'mongo_handler' in st.session_state:
                del st.session_state.mongo_handler
            st.success("✅ MongoDB 연결이 해제되었습니다.")
            st.rerun()
    else:
        st.warning("⚠️ MongoDB 연결되지 않음")
        
        # 수동 연결 시도
        if st.button("🔗 수동 연결 시도"):
            try:
                mongo_handler = MongoDBHandler()
                connection_test = mongo_handler.test_connection()
                
                if connection_test.get('success'):
                    st.session_state.mongodb_connected = True
                    st.session_state.mongo_handler = mongo_handler
                    st.success("✅ 수동 연결 성공!")
                    st.rerun()
                else:
                    st.error(f"❌ 수동 연결 실패: {connection_test.get('message')}")
            except Exception as e:
                st.error(f"❌ 수동 연결 시도 실패: {e}")

else:
    st.error("❌ MongoDB 핸들러를 사용할 수 없습니다.")
    st.info("💡 mongodb_handler.py 파일이 올바르게 설치되었는지 확인하세요.")

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
col5, col6 = st.columns(2)

with col5:
    st.subheader("Streamlit 환경")
    st.write(f"**Streamlit 버전**: {st.__version__}")
    st.write(f"**Python 버전**: {os.sys.version}")
    st.write(f"**운영체제**: {os.name}")

with col6:
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

# MongoDB 연결 상태 모니터링
st.header("📈 연결 상태 모니터링")

if st.session_state.get('mongodb_connected') and st.session_state.get('mongo_handler'):
    col7, col8 = st.columns(2)
    
    with col7:
        if st.button("🔄 연결 상태 새로고침"):
            try:
                test_result = st.session_state.mongo_handler.test_connection()
                if test_result.get('success'):
                    st.success("✅ 연결 상태 정상")
                else:
                    st.error(f"❌ 연결 상태 이상: {test_result.get('message')}")
            except Exception as e:
                st.error(f"❌ 연결 상태 확인 실패: {e}")
    
    with col8:
        if st.button("📊 데이터베이스 통계"):
            try:
                stats = st.session_state.mongo_handler.get_statistics()
                if stats:
                    st.json(stats)
                else:
                    st.info("통계 정보를 가져올 수 없습니다.")
            except Exception as e:
                st.error(f"❌ 통계 조회 실패: {e}")

st.markdown("---")
st.markdown("💡 **참고**: 이 페이지는 Streamlit Cloud 환경에서 MongoDB Atlas 연결을 모니터링합니다.")
