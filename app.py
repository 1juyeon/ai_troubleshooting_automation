import streamlit as st
import datetime
import pandas as pd
import json
import os
import requests
from urllib.parse import urlencode
from typing import Dict, Any

# 커스텀 모듈 import
from classify_issue import IssueClassifier
from scenario_db import ScenarioDB
from vector_search import VectorSearchWrapper
from gpt_handler import GPTHandler
from database import HistoryDB
from multi_user_database import MultiUserHistoryDB
from enhanced_google_auth import EnhancedGoogleAuth

# 페이지 설정
st.set_page_config(
    page_title="PrivKeeper P 장애 대응 자동화",
    page_icon="🤖",
    layout="wide"
)

# 세션 상태 초기화 - session_state 활용
def init_session_state():
    """세션 상태 초기화 - session_state 활용"""
    # OAuth 인증 관련 세션 키들
    oauth_keys = {
        'auth_checked': False,
        'login_success': False,
        'user_authenticated': False,
        'google_auth_initialized': False,
        'session_persistent': True,
        'login_completed': False
    }
    
    # 분석 결과 관련 세션 키들
    analysis_keys = {
        'analysis_result': None,
        'inquiry_data': None,
        'history_search_results': None,
        'history_search_performed': False,
        'analysis_completed': False,
        'page_initialized': True
    }
    
    # 모든 세션 키 초기화 (기존 값 보존)
    all_keys = {**oauth_keys, **analysis_keys}
    
    for key, default_value in all_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # OAuth 인증 상태 확인 및 복원
    if 'google_user' in st.session_state and st.session_state.google_user:
        st.session_state.user_authenticated = True
        st.session_state.auth_checked = True
        st.session_state.login_completed = True
        print("✅ 세션에서 인증 상태 복원됨")
    
    # 디버깅용 로그
    if st.session_state.get('user_authenticated'):
        print("✅ 세션에서 인증 상태 복원됨")

# 세션 상태 초기화
init_session_state()

# 인증 체크 - 로그인되지 않은 경우 로그인 페이지 표시
def check_authentication():
    """인증 상태 확인 및 로그인 페이지 표시"""
    if not st.session_state.get('login_completed', False) or not st.session_state.get('google_user'):
        # 로그인 페이지 표시
        render_login_page()
        st.stop()
    else:
        st.session_state.user_authenticated = True
        st.session_state.auth_checked = True

def render_login_page():
    """로그인 페이지 렌더링"""
    # 헤더
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom:2rem;'>
        <h1>🔐 PrivKeeper P 로그인</h1>
        <p>Google 계정으로 로그인하여 시스템에 접근하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # OAuth 설정 확인
    try:
        client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
        client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    except:
        client_id = ""
        client_secret = ""
    
    if not client_id:
        st.error("❌ Google OAuth가 설정되지 않았습니다.")
        st.info("관리자에게 OAuth 설정을 요청하세요.")
        return
    
    # OAuth 콜백 처리
    code = st.query_params.get("code", None)
    state = st.query_params.get("state", None)
    
    if code and state:
        with st.spinner("🔐 로그인 처리 중..."):
            # 토큰 교환 및 사용자 정보 가져오기
            if handle_oauth_callback(code, state):
                st.success("✅ 로그인 성공! 페이지를 새로고침하세요.")
                st.rerun()
    
    # 로그인 버튼 표시
    auth_url = get_auth_url()
    if auth_url:
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
                    <li>이 페이지를 새로고침하세요</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        # 디버그 정보
        if st.checkbox("🔧 디버그 정보 표시"):
            st.json({
                "client_id_set": bool(client_id),
                "client_secret_set": bool(client_secret),
                "auth_url_length": len(auth_url),
                "auth_url_preview": auth_url[:100] + "..." if len(auth_url) > 100 else auth_url
            })

def get_auth_url():
    """Google OAuth2 인증 URL 생성"""
    try:
        client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
        if not client_id:
            return ""
        
        # state 토큰 생성
        import secrets
        state = secrets.token_urlsafe(32)
        st.session_state.oauth_state = state
        
        redirect_uri = "https://privkeeperp-response.streamlit.app"
        
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
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
    except Exception as e:
        st.error(f"❌ 인증 URL 생성 실패: {e}")
        return ""

def handle_oauth_callback(code, state):
    """OAuth 콜백 처리"""
    try:
        client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
        client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
        redirect_uri = "https://privkeeperp-response.streamlit.app"
        
        # 토큰 교환
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(token_url, data=data, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data.get('access_token')
        if access_token:
            # 사용자 정보 가져오기
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            user_response = requests.get(userinfo_url, headers=headers, timeout=10)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # 세션에 사용자 정보 저장
            st.session_state.google_user = user_info
            st.session_state.google_access_token = access_token
            st.session_state.login_completed = True
            
            return True
        
        return False
    except Exception as e:
        st.error(f"❌ OAuth 콜백 처리 실패: {e}")
        return False

# 인증 체크 실행
check_authentication()

# OAuth 세션 상태는 EnhancedGoogleAuth 클래스에서 자동으로 초기화됨

# 컴포넌트 초기화
@st.cache_resource
def init_components():
    """컴포넌트 초기화"""
    classifier = IssueClassifier()
    scenario_db = ScenarioDB()
    vector_search = VectorSearchWrapper()
    
    # API 키 설정
    api_key = os.getenv("GOOGLE_API_KEY")
    
    gpt_handler = GPTHandler(api_key=api_key)
    
    # API 키 상태 확인
    if not api_key:
        st.error("❌ Google API 키가 설정되지 않았습니다.")
        st.info("관리자가 API 키를 설정하면 AI 분석이 가능합니다.")
        st.stop()
    
    # 기존 데이터베이스 (호환성 유지)
    history_db = HistoryDB()
    
    # 다중 사용자 데이터베이스
    multi_user_db = MultiUserHistoryDB()
    
    # 벡터 DB에 초기 샘플 데이터 추가 (데이터가 없을 경우)
    try:
        stats = vector_search.get_statistics()
        if stats.get('total_documents', 0) == 0:
            print("📝 벡터 DB에 초기 샘플 데이터를 추가합니다...")
            vector_search.add_initial_sample_data()
            print("✅ 초기 샘플 데이터 추가 완료")
    except Exception as e:
        print(f"⚠️ 초기 데이터 추가 실패: {e}")
    
    return classifier, scenario_db, vector_search, gpt_handler, history_db, multi_user_db

# 컴포넌트 초기화 (OAuth 제외)
classifier, scenario_db, vector_search, gpt_handler, history_db, multi_user_db = init_components()

# Google OAuth2 인증 (캐시하지 않음)
google_auth = EnhancedGoogleAuth()

# 사이드바
with st.sidebar:
    st.markdown("## 🔐 인증")
    
    # Google OAuth 로그인 (OAuth가 설정된 경우에만 표시)
    if google_auth.client_id:
        # 인증 상태 확인 - session_state 활용
        if not st.session_state.get('auth_checked', False):
            st.session_state.auth_checked = True
        
        # 인증 상태 확인 (EnhancedGoogleAuth에서 관리)
        is_auth = google_auth.is_authenticated()
        
        # 세션에 인증 상태 저장
        st.session_state.user_authenticated = is_auth
        
        if not is_auth:
            st.markdown("### Google 계정으로 로그인")
            # 로그인 버튼 렌더링
            login_success = google_auth.render_login_button()
            if login_success:
                st.session_state.login_success = True
                st.rerun()
            st.markdown("---")
        else:
            # 로그인된 사용자 정보 표시
            st.markdown("### 👤 로그인된 사용자")
            google_auth.render_user_info()
            st.markdown("---")
    else:
        st.info("ℹ️ Google OAuth가 설정되지 않았습니다.")
        st.markdown("---")
    
    # 디버그 모드 토글
    st.markdown("### 🔧 디버그 모드")
    debug_mode = st.checkbox("디버그 모드 활성화", value=st.session_state.get('debug_mode', False))
    st.session_state.debug_mode = debug_mode
    
    if debug_mode:
        st.info("🔍 디버그 모드가 활성화되었습니다. OAuth 관련 정보가 표시됩니다.")
        
        # OAuth 상태 상세 정보
        oauth_status = {
            "client_id_set": bool(google_auth.client_id),
            "client_secret_set": bool(google_auth.client_secret),
            "redirect_uri": google_auth.redirect_uri,
            "user_authenticated": st.session_state.get('user_authenticated', False),
            "auth_checked": st.session_state.get('auth_checked', False),
            "login_success": st.session_state.get('login_success', False),
            "google_user_exists": bool(st.session_state.get('google_user', None)),
            "google_auth_initialized": st.session_state.get('google_auth_initialized', False)
        }
        
        st.json(oauth_status)
        
        # OAuth 설정 강제 업데이트 버튼
        if st.button("🔄 OAuth 상태 강제 업데이트"):
            st.session_state.google_auth_initialized = True
            st.session_state.auth_checked = True
            st.success("✅ OAuth 상태가 업데이트되었습니다!")
            st.rerun()
        
        # OAuth 설정 직접 테스트
        if st.button("🧪 OAuth 설정 직접 테스트"):
            try:
                client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
                client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
                st.success(f"✅ 직접 테스트 성공 - Client ID: {bool(client_id)}, Client Secret: {bool(client_secret)}")
                st.json({
                    "direct_client_id": client_id[:20] + "..." if client_id else "None",
                    "direct_client_secret": client_secret[:10] + "..." if client_secret else "None"
                })
            except Exception as e:
                st.error(f"❌ 직접 테스트 실패: {e}")
    
    # OAuth 디버그 페이지 링크
    st.markdown("### 🔍 OAuth 디버그")
    st.link_button("🔧 OAuth 설정 확인", "/OAuth_Debug", use_container_width=True)
    
    st.markdown("## 👤 담당자 정보")
    user_name = st.text_input("담당자명", placeholder="홍길동")
    user_role = st.selectbox("역할", ["영업", "엔지니어", "개발자"])
    st.markdown("---")
    

    
    st.markdown("## ⚙️ 시스템 설정")
    gpt_model = st.selectbox("AI 모델", ["Gemini 1.5 Pro"], index=0)

# 메인 헤더
st.markdown("""
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom:2rem;'>
    <h1>🔧 PrivKeeper P 장애 대응 자동화 시스템</h1>
    <p>Gemini AI 기반 고객 문의 자동 분석 및 응답 도구</p>
</div>
""", unsafe_allow_html=True)

# 로그인 상태에 따른 메시지 표시
if google_auth.is_authenticated():
    user_name = google_auth.get_user_name()
    st.success(f"✅ {user_name}님, AI 분석 서비스를 이용할 수 있습니다!")
else:
    st.warning("⚠️ AI 분석을 이용하려면 Google 계정으로 로그인해주세요.")
    st.info("사이드바에서 로그인 버튼을 클릭하세요.")

# 탭 생성
tab_names = ["📝 고객 문의 입력", "🤖 AI 분석 결과", "📊 이력 관리", "🔍 시스템 상태", "📚 사용 가이드"]

# 탭 생성
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_names)

# 분석 완료 알림 (전역적으로 표시)
if st.session_state.analysis_result and st.session_state.analysis_completed:
    st.success("✅ AI 분석이 완료되었습니다! AI 분석 결과 페이지로 이동해 상세한 결과를 확인하세요.")

# 탭 1: 고객 문의 입력
with tab1:
    st.markdown("## 📝 고객 문의 입력")
    
    # 고객 정보 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("고객사명", placeholder="ABC 주식회사")
        customer_contact = st.text_input("고객 연락처", placeholder="010-1234-7890")
        customer_manager = st.text_input("고객 담당자", placeholder="김담당")
    
    with col2:
        priority = st.selectbox("우선순위", ["긴급", "높음", "보통", "낮음"], index=2)
        contract_type = st.selectbox("계약 유형", ["무상 유지보수", "유상 유지보수", "기타"])
    
    # 문의 내용 입력
    st.markdown("### 문의 내용")
    inquiry_content = st.text_area(
        "고객이 전달한 문의 내용을 상세히 입력해주세요",
        placeholder="예시: 고객이 PrivKeeper P에서 비밀번호 변경을 시도했으나 '인증 실패' 오류가 발생하여 변경이 되지 않는다고 합니다. 고객은 정확한 현재 비밀번호를 입력했다고 확신하고 있습니다.",
        height=200
    )
    
    # 추가 정보
    with st.expander("📋 추가 정보 입력"):
        col3, col4 = st.columns(2)
        
        with col3:
            system_version = st.text_input("시스템 버전", placeholder="v2.0")
            browser_info = st.text_input("브라우저 정보", placeholder="Chrome 120")
        
        with col4:
            os_info = st.text_input("운영체제", placeholder="Windows 11")
            error_code = st.text_input("오류 코드", placeholder="ERR_001")
    
    # 제출 버튼
    if google_auth.is_authenticated():
        if st.button("🚀 AI 분석 요청", type="primary", use_container_width=True):
            if inquiry_content.strip():
                # 진행 상황을 표시할 컨테이너 생성
                progress_container = st.container()
                
                with progress_container:
                    st.info("🚀 AI 분석을 시작합니다...")
                    
                    try:
                        # 1. 문제 유형 자동 분류
                        with st.spinner("1단계: 문제 유형 분류 중..."):
                            classification_result = classifier.classify_issue(inquiry_content)
                            issue_type = classification_result['issue_type']
                            st.success(f"✅ 문제 유형 분류 완료: {issue_type}")
                        
                        # 2. 시나리오 조회
                        with st.spinner("2단계: 시나리오 조회 중..."):
                            scenarios = scenario_db.get_scenarios_by_issue_type(issue_type)
                            best_scenario = scenario_db.find_best_scenario(issue_type, inquiry_content)
                            st.success(f"✅ 시나리오 조회 완료: {len(scenarios)}개 시나리오 발견")
                        
                        # 3. 유사 사례 검색
                        with st.spinner("3단계: 유사 사례 검색 중..."):
                            similar_cases = vector_search.search_similar_cases(inquiry_content, top_k=3)
                            st.success(f"✅ 유사 사례 검색 완료: {len(similar_cases)}개 사례 발견")
                        
                        # 4. 매뉴얼 참조 조회
                        with st.spinner("4단계: 매뉴얼 참조 조회 중..."):
                            manual_ref = scenario_db.get_manual_reference(issue_type)
                            st.success("✅ 매뉴얼 참조 조회 완료")
                        
                        # 5. Gemini 응답 생성 (타임아웃 설정)
                        with st.spinner("5단계: AI 응답 생성 중... (최대 30초)"):
                            import time
                            start_time = time.time()
                            
                            # API 키 확인
                            api_key_available = st.session_state.get('google_api_key') or os.getenv("GOOGLE_API_KEY")
                            
                            if not api_key_available:
                                st.error("❌ API 키가 설정되지 않아 AI 분석을 진행할 수 없습니다.")
                                st.stop()
                            
                            # 타임아웃 설정 (30초)
                            gemini_result = None
                            try:
                                gemini_result = gpt_handler.generate_complete_response(
                                    customer_input=inquiry_content,
                                    issue_type=issue_type,
                                    condition_1=best_scenario.get('condition_1', '') if best_scenario else '',
                                    condition_2=best_scenario.get('condition_2', '') if best_scenario else ''
                                )
                                
                                elapsed_time = time.time() - start_time
                                if gemini_result["success"]:
                                    st.success(f"✅ AI 응답 생성 완료 ({elapsed_time:.1f}초)")
                                else:
                                    st.warning(f"⚠️ AI 응답 생성 실패, 기본 응답 사용 ({elapsed_time:.1f}초)")
                                    
                            except Exception as e:
                                elapsed_time = time.time() - start_time
                                st.error(f"❌ AI 응답 생성 중 오류 발생 ({elapsed_time:.1f}초): {e}")
                                # 기본 응답 생성
                                gemini_result = {
                                    "success": False,
                                    "error": str(e),
                                    "parsed_response": gpt_handler._generate_default_response(
                                        inquiry_content, issue_type, 
                                        best_scenario.get('condition_1', '') if best_scenario else '',
                                        best_scenario.get('condition_2', '') if best_scenario else ''
                                    )
                                }
                        
                        # 결과 저장
                        analysis_result = {
                            'classification': classification_result,
                            'issue_type': issue_type,
                            'scenarios': scenarios,
                            'best_scenario': best_scenario,
                            'similar_cases': similar_cases,
                            'gemini_result': gemini_result,
                            'timestamp': datetime.datetime.now().isoformat()
                        }
                        
                        st.session_state.analysis_result = analysis_result
                        
                        st.session_state.inquiry_data = {
                            "customer_name": customer_name,
                            "customer_contact": customer_contact,
                            "customer_manager": customer_manager,
                            "inquiry_content": inquiry_content,
                            "system_version": system_version,
                            "browser_info": browser_info,
                            "os_info": os_info,
                            "error_code": error_code,
                            "priority": priority,
                            "contract_type": contract_type,
                            "user_name": user_name,
                            "user_role": user_role
                        }
                        
                        # 다중 사용자 데이터베이스에 저장
                        if google_auth.is_authenticated():
                            try:
                                user_email = google_auth.get_user_email()
                                # inquiry_data에 사용자 이메일 추가
                                inquiry_data_with_email = st.session_state.inquiry_data.copy()
                                inquiry_data_with_email['user_email'] = user_email
                                save_result = multi_user_db.save_analysis(analysis_result, inquiry_data_with_email)
                                if save_result.get('success'):
                                    st.success(f"✅ 분석 결과가 저장되었습니다. (사용자: {save_result.get('user_name', 'Unknown')})")
                                else:
                                    st.warning(f"⚠️ 분석 결과 저장 중 경고: {save_result.get('error', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"❌ 다중 사용자 저장 중 오류: {e}")
                                st.info("기존 데이터베이스에만 저장됩니다.")
                        
                        # 기존 데이터베이스에도 저장 (호환성 유지)
                        try:
                            history_db.save_analysis(analysis_result, st.session_state.inquiry_data)
                        except Exception as e:
                            st.error(f"❌ 기존 데이터베이스 저장 중 오류: {e}")
                        
                        st.session_state.analysis_completed = True
                        st.success("🎉 AI 분석이 완료되었습니다!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 분석 중 오류가 발생했습니다: {e}")
                        st.info("다시 시도해주세요.")
            else:
                st.warning("⚠️ 문의 내용을 입력해주세요.")
    else:
        st.warning("⚠️ AI 분석을 이용하려면 Google 계정으로 로그인해주세요.")
        st.info("사이드바에서 로그인 버튼을 클릭하세요.")

# 탭 2: AI 분석 결과
with tab2:
    st.markdown("## 🤖 AI 분석 결과")
    
    # API 키 확인
    if not st.session_state.get('google_api_key') and not os.getenv("GOOGLE_API_KEY"):
        st.error("❌ Google API 키가 설정되지 않았습니다.")
        st.info("""
        **API 키 설정 방법:**
        1. 사이드바의 "🔑 API 설정" 섹션에서 Google API 키를 입력하세요
        2. 또는 환경변수 `GOOGLE_API_KEY`를 설정하세요
        
        **Google API 키 발급 방법:**
        1. [Google Cloud Console](https://console.cloud.google.com/) 접속
        2. 프로젝트 생성 또는 선택
        3. API 및 서비스 → 사용자 인증 정보
        4. "사용자 인증 정보 만들기" → "API 키"
        5. 생성된 API 키를 복사하여 앱에 입력
        """)
        st.stop()
    
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # 분석 완료 알림
        st.success("✅ AI 분석이 완료되었습니다! 아래에서 상세한 결과를 확인하세요.")
        
        # 입력 정보 요약
        with st.expander("📋 입력된 문의 정보", expanded=True):
            if st.session_state.inquiry_data:
                data = st.session_state.inquiry_data
                col5, col6 = st.columns(2)
                
                with col5:
                    st.write(f"**고객사명:** {data['customer_name']}")
                    st.write(f"**고객 담당자:** {data['customer_manager']}")
                    st.write(f"**문의 내용:** {data['inquiry_content'][:100]}")
                    st.write(f"**우선순위:** {data['priority']}")
                    st.write(f"**계약 유형:** {data['contract_type']}")
                
                with col6:
                    st.write(f"**담당자:** {data['user_name']} ({data['user_role']})")
                    st.write(f"**시스템 버전:** {data['system_version']}")
                    st.write(f"**브라우저:** {data['browser_info']}")
                    st.write(f"**운영체제:** {data['os_info']}")
        
        # AI 분석 결과
        st.markdown("### 🔍 AI 분석 결과")
        
        # 문제 유형 분류 결과
        col7, col8 = st.columns(2)
        
        with col7:
            st.markdown("#### 📊 문제 유형 분류")
            classification = result['classification']
            st.write(f"**분류된 문제 유형:** {classification['issue_type']}")
            st.write(f"**분류 방법:** {classification['method']}")
            st.write(f"**신뢰도:** {classification['confidence']}")
        
        with col8:
            st.markdown("#### 🎯 시나리오 매칭")
            if result['best_scenario']:
                scenario = result['best_scenario']
                st.write(f"**조건 1:** {scenario.get('condition_1', 'N/A')}")
                st.write(f"**조건 2:** {scenario.get('condition_2', 'N/A')}")
                st.write(f"**해결책:** {scenario.get('solution', 'N/A')}")
                st.write(f"**현장 출동 필요:** {scenario.get('onsite_needed', 'N')}")
        
        # Gemini 응답 결과
        st.markdown("### 🤖 AI 응답")
        
        if result['gemini_result']['success']:
            parsed = result['gemini_result']['parsed_response']
            
            # 대응 유형 표시
            response_type = parsed['response_type']
            if response_type == "해결안":
                st.success(f"✅ {response_type}")
            elif response_type == "질문":
                st.warning(f"❓ {response_type}")
            elif response_type == "출동":
                st.error(f"🚨 {response_type}")
            else:
                st.info(f"ℹ️ {response_type}")
            
            # 응답 내용
            col9, col10 = st.columns(2)
            
            with col9:
                st.markdown("#### 📝 요약")
                st.write(parsed['summary'])
                
                st.markdown("#### 🔧 조치 흐름")
                st.write(parsed['action_flow'])
            
            with col10:
                st.markdown("#### 📧 이메일 초안")
                # 이메일 내용을 줄바꿈이 포함된 형태로 표시
                email_content = parsed['email_draft'].replace('\n', '\n\n')
                st.text_area("이메일 내용", email_content, height=300)
                
                # 복사 버튼
                if st.button("📋 이메일 복사", use_container_width=True):
                    st.success("이메일 내용이 클립보드에 복사되었습니다!")
            
            # 전체 응답
            with st.expander("📄 전체 AI 응답"):
                st.text(parsed['full_response'])
        
        else:
            st.error("❌ AI 응답 생성 실패")
            st.write(f"오류: {result['gemini_result']['error']}")
            
            # 기본 응답 표시
            if 'parsed_response' in result['gemini_result']:
                parsed = result['gemini_result']['parsed_response']
                st.warning("⚠️ 기본 응답을 제공합니다:")
                
                col9, col10 = st.columns(2)
                
                with col9:
                    st.markdown("#### 📝 요약")
                    st.write(parsed['summary'])
                    
                    st.markdown("#### 🔧 조치 흐름")
                    st.write(parsed['action_flow'])
                
                with col10:
                    st.markdown("#### 📧 이메일 초안")
                    # 이메일 내용을 줄바꿈이 포함된 형태로 표시
                    email_content = parsed['email_draft'].replace('\n', '\n\n')
                    st.text_area("이메일 내용", email_content, height=300)
                    
                    if st.button("📋 이메일 복사", use_container_width=True):
                        st.success("이메일 내용이 클립보드에 복사되었습니다!")
        
        # 유사 사례
        if result['similar_cases']:
            st.markdown("### 🔍 유사 사례")
            for i, case in enumerate(result['similar_cases'], 1):
                with st.expander(f"사례 {i}: {case.get('issue_type', 'N/A')}"):
                    st.write(f"**고객 문의:** {case.get('customer_input', 'N/A')}")
                    st.write(f"**요약:** {case.get('summary', 'N/A')}")
                    st.write(f"**조치 흐름:** {case.get('action_flow', 'N/A')}")
                    if case.get('similarity_score'):
                        st.write(f"**유사도:** {case['similarity_score']:.3f}")
        
        # 액션 버튼
        col11, col12, col13 = st.columns(3)
        
        with col11:
            if st.button("💾 결과 저장", use_container_width=True):
                # 결과를 JSON 파일로 저장
                filename = f"analysis_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.analysis_result, f, ensure_ascii=False, indent=2)
                st.success(f"분석 결과가 {filename}에 저장되었습니다!")
        
        with col12:
            if st.button("🔄 새로운 분석", use_container_width=True):
                st.session_state.analysis_result = None
                st.session_state.inquiry_data = None
                st.rerun()
        
        with col13:
            if st.button("📊 통계 보기", use_container_width=True):
                # 통계 보기 버튼 클릭시 분석 완료 알림 제거
                st.session_state.analysis_completed = False
                st.info("📊 이력 관리 탭으로 이동하세요.")
    
    else:
        st.info("📝 먼저 고객 문의 입력 탭에서 문의를 입력해주세요.")
        st.markdown("---")
        st.markdown("### 📋 사용 방법")
        st.markdown("1. **📝 고객 문의 입력** 탭에서 문의 내용을 입력하세요")
        st.markdown("2. **🚀 AI 분석 요청** 버튼을 클릭하세요")
        st.markdown("3. 분석이 완료되면 이 탭에서 결과를 확인할 수 있습니다")

# 탭 3: 이력 관리
with tab3:
    st.markdown("## 📊 분석 이력 관리")
    
    # 이력 보기 모드 선택
    history_mode = st.radio(
        "이력 보기 모드",
        ["👤 내 이력", "🌐 전체 이력"],
        horizontal=True
    )
    
    # 필터링 옵션
    col15, col16, col17, col18 = st.columns(4)
    
    with col15:
        filter_date_from = st.date_input("시작 날짜", value=datetime.date.today() - datetime.timedelta(days=30))
    
    with col16:
        filter_date_to = st.date_input("종료 날짜", value=datetime.date.today())
    
    with col17:
        filter_type = st.selectbox("문제 유형 필터", 
            ["전체"] + ["현재 비밀번호가 맞지 않습니다", "VMS와의 통신에 실패했습니다", "Ping 테스트에 실패했습니다", 
                       "Onvif 응답이 없습니다", "로그인 차단 상태입니다(CCTV)", "비밀번호 변경에 실패했습니다",
                       "PK P 계정 로그인 안됨", "PK P 웹 접속 안됨", "기타"])
    
    with col18:
        if history_mode == "👤 내 이력":
            filter_user = st.text_input("담당자명", value=user_name, disabled=True)
        else:
            filter_user = st.text_input("담당자 필터", placeholder="담당자명 입력")
    
    # 검색 버튼
    search_clicked = st.button("🔍 이력 검색", type="primary")
    
    # 검색 버튼 클릭시
    if search_clicked:
        # 검색 진행 상태 표시
        with st.spinner("🔍 이력을 검색하고 있습니다..."):
            try:
                # 종료 날짜를 포함하도록 23:59:59 추가
                date_to_with_time = None
                if filter_date_to:
                    date_to_with_time = f"{filter_date_to.isoformat()}T23:59:59"
                
                # 다중 사용자 데이터베이스에서 이력 조회
                if history_mode == "👤 내 이력":
                    # 사용자별 이력 조회
                    history_result = multi_user_db.get_user_history(
                        user_name=user_name,
                        user_role=user_role,
                        limit=50,
                        issue_type=filter_type if filter_type != "전체" else None,
                        date_from=filter_date_from.isoformat() if filter_date_from else None,
                        date_to=date_to_with_time,
                        keyword=filter_user if filter_user else None
                    )
                else:
                    # 전체 이력 조회
                    history_result = multi_user_db.get_global_history(
                        limit=50,
                        issue_type=filter_type if filter_type != "전체" else None,
                        date_from=filter_date_from.isoformat() if filter_date_from else None,
                        date_to=date_to_with_time,
                        user_name=filter_user if filter_user else None
                    )
                
                if history_result.get('success') and history_result.get('data'):
                    history_data = history_result['data']
                    
                    # 데이터프레임 생성
                    df_data = []
                    for i, entry in enumerate(history_data, 1):
                        df_data.append({
                            "번호": i,
                            "날짜": entry.get('timestamp', '')[:10] if entry.get('timestamp') else "",
                            "고객사명": entry.get('customer_name', ''),
                            "문의유형": entry.get('issue_type', ''),
                            "우선순위": entry.get('priority', ''),
                            "담당자": entry.get('user_name', ''),
                            "역할": entry.get('user_role', ''),
                            "분류방법": entry.get('classification_method', ''),
                            "신뢰도": entry.get('confidence', ''),
                            "응답유형": entry.get('response_type', '')
                        })
                    
                    df = pd.DataFrame(df_data)
                    # 세션 상태에 결과 저장
                    st.session_state.history_search_results = df
                    st.session_state.history_search_performed = True
                    
                    st.success(f"✅ {len(history_data)}건의 이력이 조회되었습니다.")
                    # 인덱스 숨기기로 중복 번호 제거
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # 통계 정보
                    if history_mode == "👤 내 이력":
                        stats = multi_user_db.get_statistics(user_name=user_name, user_role=user_role)
                    else:
                        stats = multi_user_db.get_statistics()
                    
                    col19, col20, col21, col22 = st.columns(4)
                    
                    with col19:
                        st.metric("총 문의 건수", stats.get('total_analyses', 0))
                    
                    with col20:
                        if history_mode == "🌐 전체 이력":
                            st.metric("총 사용자 수", stats.get('total_users', 0))
                        else:
                            st.metric("내 분석 건수", stats.get('total_analyses', 0))
                    
                    with col21:
                        st.metric("문제 유형 수", len(stats.get('issue_types', [])))
                    
                    with col22:
                        if history_mode == "🌐 전체 이력":
                            st.metric("응답 유형 수", len(stats.get('response_types', [])))
                        else:
                            st.metric("응답 유형 수", len(stats.get('response_types', [])))
                    
                    # 문제 유형별 분포
                    if stats.get('issue_types'):
                        st.markdown("### 📊 문제 유형별 분포")
                        issue_data = []
                        for issue_type in stats['issue_types']:
                            if issue_type:  # 빈 문자열 제외
                                count = len([entry for entry in history_data if entry.get('issue_type') == issue_type])
                                issue_data.append({"문제 유형": issue_type, "건수": count})
                        
                        if issue_data:
                            issue_df = pd.DataFrame(issue_data)
                            st.bar_chart(issue_df.set_index("문제 유형"))
                
                else:
                    st.info("검색 조건에 맞는 이력이 없습니다.")
                    st.session_state.history_search_results = None
                    st.session_state.history_search_performed = True
                    
            except Exception as e:
                st.error(f"이력 조회 중 오류가 발생했습니다: {e}")
    
    # 이전 검색 결과가 있으면 표시 (검색 버튼을 클릭하지 않았을 때)
    if not search_clicked and st.session_state.history_search_performed and st.session_state.history_search_results is not None:
        st.markdown("### 📊 이전 검색 결과")
        # 인덱스 숨기기로 중복 번호 제거
        st.dataframe(st.session_state.history_search_results, use_container_width=True, hide_index=True)
    
    # 벡터 DB 통계
    st.markdown("### 🔍 벡터 검색 통계")
    try:
        vector_stats = vector_search.get_statistics()
        
        col23, col24, col25 = st.columns(3)
        
        with col23:
            st.metric("총 문서 수", vector_stats.get('total_documents', 0))
        
        with col24:
            st.metric("벡터 차원", vector_stats.get('vector_dimensions', 0))
        
        with col25:
            st.metric("문제 유형 수", len(vector_stats.get('issue_types', [])))
        
        if vector_stats.get('issue_types'):
            st.write("**등록된 문제 유형:**")
            for issue_type in vector_stats['issue_types']:
                st.write(f"- {issue_type}")
                
    except Exception as e:
        st.error(f"벡터 DB 통계 조회 실패: {e}")

# 탭 4: 시스템 상태
with tab4:
    st.markdown("## 🔍 시스템 상태")
    
    if classifier and scenario_db and vector_search and gpt_handler:
        st.success("✅ 모든 모듈이 정상적으로 초기화되었습니다.")
        
        # 각 모듈 상태 확인
        col22, col23 = st.columns(2)
        
        with col22:
            st.markdown("#### 📊 시나리오 DB 상태")
            issue_types = scenario_db.get_all_issue_types()
            st.write(f"**등록된 문제 유형:** {len(issue_types)}개")
            for issue_type in issue_types[:5]:  # 처음 5개만 표시
                st.write(f"- {issue_type}")
            if len(issue_types) > 5:
                st.write(f"... 외 {len(issue_types) - 5}개")
        
        with col23:
            st.markdown("#### 🔍 벡터 검색 상태")
            stats = vector_search.get_statistics()
            st.write(f"**총 문서 수:** {stats.get('total_documents', 0)}건")
            st.write(f"**벡터 차원:** {stats.get('vector_dimensions', 0)}")
            
            if stats.get('issue_types'):
                st.write("**문제 유형별 분포:**")
                for issue_type in stats['issue_types'][:3]:
                    st.write(f"- {issue_type}")
        
        # 시스템 정보
        st.markdown("#### ⚙️ 시스템 정보")
        col24, col25, col26 = st.columns(3)
        
        with col24:
            st.write("**AI 모델:** Gemini 1.5 Pro")
            st.write("**벡터 DB:** ChromaDB")
        
        with col25:
            st.write("**시나리오 소스:** JSON + Excel")
            st.write("**프롬프트 템플릿:** 로드됨")
        
        with col26:
            st.write("**API 상태:** 정상")
            st.write("**데이터베이스:** 연결됨")
        
        # 벡터 DB 관리
        st.markdown("#### 🔧 벡터 DB 관리")
        col27, col28 = st.columns(2)
        
        with col27:
            if st.button("📝 샘플 데이터 추가", use_container_width=True):
                try:
                    if vector_search.add_initial_sample_data():
                        st.success("✅ 샘플 데이터가 추가되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 샘플 데이터 추가에 실패했습니다.")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
        
        with col28:
            if st.button("🗑️ 벡터 DB 초기화", use_container_width=True):
                try:
                    vector_search.vector_search.vector_db.clear()
                    st.success("✅ 벡터 DB가 초기화되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 초기화 실패: {e}")
    
    else:
        st.error("❌ 일부 모듈 초기화에 실패했습니다.")

# 탭 5: 사용 가이드
with tab5:
    st.markdown("## 📚 사용 가이드")
    
    st.markdown("### 🎯 시스템 개요")
    st.markdown("PrivKeeper P 장애 대응 자동화 시스템은 Gemini AI 기반 고객 문의 자동 분석 및 응답 도구입니다.")

    st.markdown("### 📋 사용 방법")

    st.markdown("**1단계: 고객 문의 입력**")
    st.markdown("- 고객사 정보와 문의 내용을 상세히 입력")
    st.markdown("- 시스템이 자동으로 문제 유형을 분류합니다")

    st.markdown("**2단계: AI 분석**")
    st.markdown("- Gemini AI가 자동으로 증상 분석, 원인 추정, 조치 방향 제시")
    st.markdown("- 유사 사례 검색을 통한 참고 정보 제공")
    st.markdown("- 고객 응답 이메일 초안 자동 생성")

    st.markdown("**3단계: 검토 및 발송**")
    st.markdown("- 엔지니어가 AI 분석 결과 검토")
    st.markdown("- 필요시 수정 후 고객에게 응답")

    st.markdown("### 🔧 기술 스택")

    st.markdown("- **AI 모델:** Google Gemini 1.5 Pro")
    st.markdown("- **벡터 검색:** ChromaDB")
    st.markdown("- **웹 프레임워크:** Streamlit")
    st.markdown("- **데이터 소스:** JSON + Excel")

    st.markdown("### ⚠️ 주의사항")

    st.markdown("- AI 분석 결과는 참고용이며, 최종 검토 후 발송")
    st.markdown("- 민감한 정보는 입력하지 않도록 주의")
    st.markdown("- 긴급한 경우 즉시 담당 엔지니어에게 연락")

    st.markdown("### 📞 지원 연락처")

    st.markdown("- 기술지원: 02-678-1234 이메일: support@privkeeper.com")
    st.markdown("- 긴급상황: 010-3456-7890")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
©2024 PrivKeeper P 장애 대응 자동화 시스템
</div>
""", unsafe_allow_html=True)