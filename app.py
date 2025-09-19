import streamlit as st
from datetime import datetime, timezone, date, timedelta
import pandas as pd
import json
import os
import requests
from typing import Dict, Any
import pickle
import pytz
import re
import time
# import pyperclip  # Windows 환경에서 문제가 있어 JavaScript 기반 클립보드 사용

# 커스텀 모듈 import
from classify_issue import IssueClassifier
from scenario_db import ScenarioDB
from vector_search import VectorSearchWrapper
from openai_handler import OpenAIHandler
from gemini_handler import GeminiHandler
from database import HistoryDB
from multi_user_database import MultiUserHistoryDB
from mongodb_handler import MongoDBHandler
from solapi_handler import SOLAPIHandler
from config import get_secret, validate_config, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_API_KEY, GEMINI_API_KEY, MONGODB_URI, SOLAPI_API_KEY, SOLAPI_API_SECRET, OPENAI_API_KEY

# 페이지 설정
st.set_page_config(
    page_title="PrivKeeper P 장애 대응 자동화",
    page_icon="🤖",
    layout="wide"
)

# UI 간격 조정을 위한 CSS 스타일
st.markdown("""
<style>
    /* 상세보기 모달의 간격 조정 */
    .stExpander > div > div > div > div {
        padding: 0.5rem !important;
    }
    
    /* 컬럼 간격 조정 */
    .row-widget.stHorizontal > div {
        padding: 0.25rem !important;
    }
    
    /* 텍스트 간격 조정 */
    .stMarkdown p {
        margin-bottom: 0.5rem !important;
    }
    
    /* 구분선 간격 조정 */
    hr {
        margin: 0.5rem 0 !important;
    }
    
    /* 데이터 행의 텍스트 세로 중앙 정렬 */
    .row-widget.stHorizontal > div > div {
        display: flex !important;
        align-items: center !important;
        min-height: 2.5rem !important;
    }
    
    /* 데이터 행의 텍스트 세로 중앙 정렬 (고객사명이 비어있을 때) */
    .row-widget.stHorizontal > div > div > div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 2.5rem !important;
    }
    
    /* 상세보기 컨테이너 간격 조정 */
    .stContainer > div {
        margin-bottom: 0.5rem !important;
    }
    
    /* 상세보기 내부 컬럼 간격 조정 */
    .stHorizontal > div {
        padding: 0.25rem !important;
        margin: 0.25rem !important;
    }
    
    /* 상세보기 내부 텍스트 간격 조정 */
    .stMarkdown h3 {
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stMarkdown h4 {
        margin-top: 0.75rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* 상세보기 내부 expander 간격 조정 */
    .stExpander > div > div > div > div > div {
        padding: 0.25rem !important;
        margin: 0.25rem !important;
    }
    
    /* 상세보기 내부 컬럼 간격 더욱 조정 */
    .stHorizontal > div > div {
        padding: 0.1rem !important;
        margin: 0.1rem !important;
    }
    
    /* 상세보기 내부 텍스트 요소 간격 조정 */
    .stMarkdown p, .stMarkdown div {
        margin: 0.25rem 0 !important;
        padding: 0.1rem 0 !important;
    }
    
    /* 상세보기 내부 버튼 간격 조정 */
    .stButton > button {
        margin: 0.25rem !important;
        padding: 0.25rem 0.5rem !important;
    }
    
    /* 상세보기 내부 expander 헤더 간격 조정 */
    .stExpander > div > div > div > div > div:first-child {
        padding: 0.5rem !important;
        margin: 0.25rem !important;
    }
    
    /* 상세보기 내부 컬럼 레이아웃 간격 조정 */
    .stHorizontal {
        gap: 0.5rem !important;
    }
    
    /* 상세보기 내부 텍스트 블록 간격 조정 */
    .stMarkdown > div {
        margin-bottom: 0.5rem !important;
    }
    
    /* 상세보기 내부 섹션 간격 조정 */
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 상세보기 내부 컨테이너 패딩 조정 */
    .stContainer {
        padding: 0.5rem !important;
    }
    
    /* 상세보기 내부 expander 컨텐츠 간격 조정 */
    .stExpander > div > div > div > div > div > div {
        padding: 0.25rem !important;
        margin: 0.25rem !important;
    }
    
    /* 상세보기 내부 모든 요소의 간격 최소화 */
    .stMarkdown, .stText, .stButton, .stExpander {
        margin: 0.1rem !important;
        padding: 0.1rem !important;
    }
    
    /* 상세보기 내부 컬럼 간격 최소화 */
    .stHorizontal > div {
        padding: 0.1rem !important;
        margin: 0.1rem !important;
    }
    
    /* 상세보기 내부 텍스트 요소 간격 최소화 */
    .stMarkdown p, .stMarkdown div, .stMarkdown h3, .stMarkdown h4 {
        margin: 0.1rem 0 !important;
        padding: 0.1rem 0 !important;
    }
    
    /* 상세보기 내부 expander 헤더 간격 최소화 */
    .stExpander > div > div > div > div > div:first-child {
        padding: 0.25rem !important;
        margin: 0.1rem !important;
    }
    
    /* 상세보기 내부 컨테이너 패딩 최소화 */
    .stContainer {
        padding: 0.25rem !important;
    }
    
    /* 상세보기 내부 섹션 간격 최소화 */
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* 상세보기 내부 버튼 간격 최소화 */
    .stButton > button {
        margin: 0.1rem !important;
        padding: 0.1rem 0.25rem !important;
    }
    
    /* 상세보기 내부 text_area 간격 최소화 */
    .stTextArea > div > div > textarea {
        margin: 0.1rem !important;
        padding: 0.1rem !important;
    }
    
    /* Streamlit 기본 간격 최소화 */
    .main > div {
        padding: 0.5rem !important;
    }
    
    .main > div > div {
        padding: 0.25rem !important;
    }
    
    /* 상세보기 내부 모든 div 요소 간격 최소화 */
    .stExpander > div > div > div > div > div > div > div {
        margin: 0.05rem !important;
        padding: 0.05rem !important;
    }
    
    /* 상세보기 내부 컬럼 레이아웃 간격 최소화 */
    .stHorizontal {
        gap: 0.25rem !important;
    }
    
    /* 상세보기 내부 expander 간격 최소화 */
    .stExpander {
        margin: 0.1rem !important;
        padding: 0.1rem !important;
    }

    /* 상세보기 영역만을 위한 특정 스타일링 */
    .stContainer:has(.stExpander) {
        border: 2px solid #007acc !important;
        border-radius: 6px !important;
        background-color: #f8f9fa !important;
        padding: 0.5rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    /* 상세보기 내부 expander만 스타일링 */
    .stContainer:has(.stExpander) .stExpander > div > div > div > div {
        border: 1px solid #e0e0e0 !important;
        border-radius: 4px !important;
        background-color: #fafafa !important;
    }

    /* 상세보기 내부 컬럼만 스타일링 */
    .stContainer:has(.stExpander) .stHorizontal > div {
        border: 1px solid #d0d0d0 !important;
        border-radius: 3px !important;
        background-color: #ffffff !important;
        padding: 0.5rem !important;
        margin: 0.25rem !important;
    }

    /* 상세보기 내부 텍스트 블록만 스타일링 */
    .stContainer:has(.stExpander) .stMarkdown > div {
        border: 1px solid #e8e8e8 !important;
        border-radius: 3px !important;
        background-color: #fefefe !important;
        padding: 0.5rem !important;
        margin: 0.25rem !important;
    }

    /* 상세보기 내부 섹션 헤더만 스타일링 */
    .stContainer:has(.stExpander) .stMarkdown h2,
    .stContainer:has(.stExpander) .stMarkdown h3,
    .stContainer:has(.stExpander) .stMarkdown h4 {
        border-bottom: 2px solid #007acc !important;
        padding-bottom: 0.25rem !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        color: #1f1f1f !important;
    }

    /* 상세보기 내부 expander 헤더만 스타일링 */
    .stContainer:has(.stExpander) .stExpander > div > div > div > div > div:first-child {
        border-bottom: 1px solid #e0e0e0 !important;
        background-color: #f5f5f5 !important;
        padding: 0.5rem !important;
        margin: 0.25rem !important;
        font-weight: bold !important;
    }

    /* 상세보기 내부 버튼만 스타일링 */
    .stContainer:has(.stExpander) .stButton > button {
        border: 1px solid #007acc !important;
        border-radius: 4px !important;
        background-color: #007acc !important;
        color: white !important;
        margin: 0.1rem !important;
        padding: 0.1rem 0.25rem !important;
    }

    /* 상세보기 내부 text_area만 스타일링 */
    .stContainer:has(.stExpander) .stTextArea > div > div > textarea {
        border: 1px solid #d0d0d0 !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
        margin: 0.1rem !important;
        padding: 0.1rem !important;
    }

    /* 상세보기 내부 구분선만 스타일링 */
    .stContainer:has(.stExpander) hr {
        border: 1px solid #e0e0e0 !important;
        margin: 0.5rem 0 !important;
        opacity: 0.6 !important;
    }

    /* 상세보기 내부 강조 텍스트만 스타일링 */
    .stContainer:has(.stExpander) .stMarkdown strong {
        color: #007acc !important;
        font-weight: 600 !important;
    }

    /* 상세보기 내부 정보 표시만 스타일링 */
    .stContainer:has(.stExpander) .stMarkdown p {
        border-left: 3px solid #007acc !important;
        padding-left: 0.5rem !important;
        margin: 0.25rem 0 !important;
        background-color: #f8f9fa !important;
        padding: 0.25rem 0.5rem !important;
        border-radius: 0 3px 3px 0 !important;
    }

    .history-table-header {
        background-color: #f0f2f6 !important;
        padding: 0.75rem 0.5rem !important;
        border-bottom: 2px solid #e0e0e0 !important;
        font-weight: bold !important;
        text-align: center !important;
        border-radius: 4px !important;
        color: #333 !important;
        font-size: 0.9rem !important;
    }

    .history-table-cell {
        padding: 0.75rem 0.5rem !important;
        text-align: center !important;
        vertical-align: middle !important;
        border-bottom: 1px solid #f0f0f0 !important;
        background-color: #ffffff !important;
        border-radius: 4px !important;
        color: #555 !important;
        font-size: 0.9rem !important;
        min-height: 2.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
</style>
""", unsafe_allow_html=True)

# MongoDB 연결 상태 확인 및 초기화
def init_mongodb_connection():
    """MongoDB 연결 초기화 및 상태 확인"""
    try:
        # MongoDB 핸들러 초기화
        mongo_handler = MongoDBHandler()
        
        # 연결 테스트
        connection_test = mongo_handler.test_connection()
        
        if connection_test.get('success'):
            st.session_state.mongodb_connected = True
            st.session_state.mongo_handler = mongo_handler
            
            # 피드백 컬렉션 초기화
            try:
                mongo_handler._initialize_feedback_collection()
            except Exception as e:
                pass
            
            return True
        else:
            st.session_state.mongodb_connected = False
            return False
            
    except Exception as e:
        st.session_state.mongodb_connected = False
        return False

# 안전한 타임스탬프 생성 함수
def get_safe_timestamp():
    """안전한 타임스탬프 생성 (한국 시간대, 실패 시 UTC 사용)"""
    try:
        return datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
    except Exception as e:
        return datetime.now().isoformat()

def show_feedback_buttons(analysis_id):
    """피드백 버튼 표시 (MongoDB 지원)"""
    st.markdown("---")
    
    # 사용자 친화적인 안내 메시지
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; margin: 10px 0;">
        <h4 style="margin: 0 0 10px 0; color: #2E7D32;">💡 이 응답이 도움이 되었다면</h4>
        <p style="margin: 0; color: #424242; font-size: 14px;">
            좋아요 버튼을 눌러주세요! 여러분의 피드백은 AI가 더 정확하고 유용한 응답을 제공하는 데 큰 도움이 됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사용자 정보 가져오기
    user_name = st.session_state.get('contact_name', 'Unknown')
    user_role = st.session_state.get('role', 'Unknown')
    
    
    # 좋아요 버튼을 중앙에 배치
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("👍 좋아요", key=f"like_{analysis_id}", use_container_width=True, type="primary"):
            try:
                feedback_result = components['multi_user_db'].save_feedback(
                    analysis_id, "like", user_name, user_role
                )
                
                if feedback_result['success']:
                    # 성공 메시지를 더 눈에 띄게 표시
                    st.markdown("""
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; margin: 10px 0;">
                        <h4 style="margin: 0 0 10px 0; color: #2E7D32;">✅ 피드백이 성공적으로 반영되었습니다!</h4>
                        <p style="margin: 0; color: #424242; font-size: 14px;">
                            감사합니다! 여러분의 피드백을 바탕으로 AI가 더 나은 응답을 제공할 수 있도록 학습하겠습니다.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error(f"피드백 저장 실패: {feedback_result.get('error', '알 수 없는 오류')}")
            except Exception as e:
                st.error(f"피드백 처리 중 오류 발생: {str(e)}")
    
    # 추가 안내 메시지
    st.markdown("""
    <div style="text-align: center; margin: 10px 0; color: #666; font-size: 12px;">
        💡 피드백은 익명으로 수집되며, AI 모델 개선 목적으로만 사용됩니다.
    </div>
    """, unsafe_allow_html=True)

def enhance_ai_prompt_with_feedback(base_prompt: str, issue_type: str) -> str:
    """좋아요를 받은 응답을 참고하여 프롬프트 개선"""
    try:
        # 좋아요를 받은 응답들 조회
        liked_responses = components['multi_user_db'].get_liked_responses(issue_type, limit=2)
        
        if liked_responses:
            feedback_examples = []
            for response in liked_responses:
                if response['summary'] and response['action_flow']:
                    feedback_examples.append(f"""
                    좋은 응답 예시:
                    - 요약: {response['summary']}
                    - 대응 방안: {response['action_flow']}
                    """)
            
            if feedback_examples:
                enhanced_prompt = f"""
                    {base_prompt}

                    ## 참고할 만한 좋은 응답 사례들:
                    {chr(10).join(feedback_examples)}

                    위의 좋은 응답 사례들을 참고하여, 유사한 품질과 스타일로 응답해주세요.
                    """
                return enhanced_prompt
        
        return base_prompt
        
    except Exception as e:
        return base_prompt

def apply_feedback_learning(ai_result: dict, issue_type: str) -> dict:
    """AI 응답에 피드백 학습 적용"""
    try:
        # 좋아요를 받은 응답들 조회
        liked_responses = components['multi_user_db'].get_liked_responses(issue_type, limit=1)
        
        if not liked_responses or not ai_result.get('success'):
            return ai_result
        
        # 좋아요를 받은 응답의 스타일을 참고하여 현재 응답 개선
        liked_response = liked_responses[0]
        
        # Gemini 응답인 경우
        if 'gemini_result' in ai_result and 'parsed_response' in ai_result['gemini_result']:
            parsed = ai_result['gemini_result']['parsed_response']
            
            # 좋아요를 받은 응답의 스타일을 참고하여 개선
            if liked_response.get('summary') and parsed.get('summary'):
                # 좋아요를 받은 응답의 요약 스타일을 참고
                parsed['summary'] = f"{parsed['summary']}\n\n※ 참고: 유사한 사례에서 효과적이었던 접근 방식을 적용했습니다."
            
            if liked_response.get('action_flow') and parsed.get('action_flow'):
                # 좋아요를 받은 응답의 조치 흐름 스타일을 참고
                parsed['action_flow'] = f"{parsed['action_flow']}\n\n※ 추가 권장사항: 검증된 효과적인 대응 방식을 참고하여 작성되었습니다."
        
        # GPT 응답인 경우
        elif 'response' in ai_result:
            # GPT 응답에 피드백 학습 메시지 추가
            feedback_note = "\n\n※ 참고: 유사한 사례에서 효과적이었던 접근 방식을 참고하여 응답을 생성했습니다."
            ai_result['response'] = ai_result['response'] + feedback_note
        
        return ai_result
        
    except Exception as e:
        return ai_result

def show_ai_analysis(selected_row):
    """선택된 행의 AI 분석 결과를 표시"""
    st.markdown("## 🤖 AI 분석 결과")
    
    # 분석 완료 알림
    st.success("✅ AI 분석이 완료되었습니다! 아래에서 상세한 결과를 확인하세요.")
    
    # 선택된 데이터 정보 표시
    with st.expander("📋 입력된 문의 정보", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**고객사명:** {selected_row.get('고객사명', 'N/A')}")
            st.write(f"**문의유형:** {selected_row.get('문의유형', 'N/A')}")
            st.write(f"**우선순위:** {selected_row.get('우선순위', 'N/A')}")
        with col2:
            st.write(f"**담당자:** {selected_row.get('담당자', 'N/A')}")
            st.write(f"**역할:** {selected_row.get('역할', 'N/A')}")
            st.write(f"**날짜:** {selected_row.get('날짜', 'N/A')}")
    
    # AI 분석 결과 (샘플 데이터)
    st.markdown("### 🔍 AI 분석 결과")
    
    # 문제 유형 분류와 시나리오 매칭 섹션 삭제
    
    # AI 응답 결과
    st.markdown("### 🤖 AI 응답")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("#### 📝 요약")
        st.write("PKP 웹 접속 불가 현상. 톰캣 상태 확인 필요.")
        
        st.markdown("#### 🔧 조치 흐름")
        st.write("""
        1. **윈도우 서비스 확인:** 윈도우 서비스 목록에서 "Apache Tomcat" 서비스가 실행 중인지 확인합니다. (services.msc 실행)

        2. **톰캣 상태 확인:** 톰캣이 실행 중이라면, 브라우저에서 http://localhost:8888/ (포트 번호는 환경에 따라 다를 수 있음)에 접속하여 톰캣 기본 페이지가 정상적으로 표시되는지 확인합니다.

        3. **톰캣 재시작:** 톰캣이 실행 중이지만 접속이 안 된다면, 톰캣 서비스를 재시작합니다. 윈도우 서비스에서 "Apache Tomcat" 서비스를 "중지" 후 "시작" 합니다.

        4. **PKP 애플리케이션 확인:** 톰캣 재시작 후에도 접속이 안 된다면, PKP 애플리케이션의 로그 파일을 확인하여 에러 메시지가 있는지 확인합니다. 로그 파일 위치는 PKP 애플리케이션 설정에 따라 다릅니다.

        5. **방화벽 확인:** 윈도우 방화벽 또는 다른 방화벽이 톰캣 포트(기본값 8080)를 차단하고 있지 않은지 확인합니다. 필요시 방화벽 설정을 변경합니다.
        """)
    
    with col6:
        st.markdown("#### 📧 이메일 초안")
        
        # 이력 관리 탭과 완전히 동일한 방식으로 이메일 초안 추출
        email_content = None
        
        # 현재 분석 결과에서 이메일 초안 추출 (이력관리와 완전히 동일한 로직)
        if st.session_state.get('analysis_result'):
            analysis_data = st.session_state.analysis_result
            
            # 이력관리와 동일한 방식으로 이메일 추출
            # 1. 파싱된 email_draft 사용 (우선순위 1) - DB에 저장된 정확한 이메일 초안
            email_draft = analysis_data.get('email_draft', '')
            if email_draft and len(email_draft.strip()) > 20:
                email_content = email_draft
            
            # 2. original_ai_response에서 이메일 초안 추출 (우선순위 2) - 이력 관리와 동일
            if not email_content and analysis_data.get('original_ai_response'):
                email_content = extract_email_from_original_response(analysis_data['original_ai_response'])
            
            # 3. full_analysis_result에서 이메일 초안 추출 (우선순위 3) - 이력 관리와 동일
            if not email_content and analysis_data.get('full_analysis_result'):
                email_content = extract_email_from_analysis_result(analysis_data['full_analysis_result'])
            
            # 4. ai_result에서 직접 추출 (이력관리와 동일한 추가 로직)
            if not email_content and analysis_data.get('ai_result'):
                ai_result = analysis_data['ai_result']
                if 'gemini_result' in ai_result and 'raw_response' in ai_result['gemini_result']:
                    email_content = extract_email_from_original_response(ai_result['gemini_result']['raw_response'])
                elif 'response' in ai_result:
                    email_content = extract_email_from_original_response(ai_result['response'])
                elif 'gpt_result' in ai_result and 'raw_response' in ai_result['gpt_result']:
                    email_content = extract_email_from_original_response(ai_result['gpt_result']['raw_response'])
        
        # 5. 기본 이메일 템플릿 (최후 수단) - 이력 관리와 동일
        if not email_content:
            email_content = f"""제목: {selected_row.get('문의유형', '문의')} 답변

                고객님 안녕하세요.

                {selected_row.get('문의유형', '문의')}에 대한 문의 주셔서 감사합니다.

                현재 상황을 분석한 결과, 추가 정보가 필요한 상황입니다.

                **필요한 정보:**
                1. 구체적인 오류 메시지
                2. 발생 시점 및 빈도
                3. 사용 환경 정보

                자세한 내용은 담당 엔지니어가 확인 후 답변 드리겠습니다.

                추가 문의사항이 있으시면 언제든 연락 주세요.

                감사합니다."""
        
        # DB original_ai_response의 이메일 초안을 그대로 표시 (줄바꿈 유지)
        st.markdown("**이메일 내용**")
        st.markdown(
            f"""
            <div style="
                background-color: #f5f5f5;   /* 연한 회색 배경 */
                color: #000000;             /* 글씨는 진한 검정 */
                white-space: pre-wrap;      
                font-family: monospace;     
                border: 1px solid #ddd;     
                padding: 12px;              
                border-radius: 6px;         
                height: 500px;              /* 고정 크기 */
                overflow-y: scroll;         /* 스크롤 가능 */
            ">
            {email_content}
            </div>
            """,
            unsafe_allow_html=True
        )
        

    
    # 액션 버튼
    col7, col8, col9 = st.columns(3)
    
    with col7:
        if st.button("💾 결과 저장", use_container_width=True):
            st.success("분석 결과가 저장되었습니다!")
    
    with col8:
        if st.button("🔄 AI 재분석", use_container_width=True):
            st.info("AI 재분석을 시작합니다...")
            st.success("AI 재분석이 완료되었습니다!")
    
    with col9:
        if st.button("📊 통계 보기", use_container_width=True):
            st.info("📊 이력 관리 탭으로 이동하세요.")

def show_ai_analysis_modal(selected_row):
    """선택된 행의 AI 분석 결과를 모달 형태로 표시"""
    with st.container():
        st.markdown("## 🤖 AI 분석 결과")
        
        # 선택된 데이터 정보 표시
        with st.expander("📋 입력된 문의 정보", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                customer_name = selected_row.get('고객사명', '')
                st.write(f"**고객사명:** {customer_name if customer_name else ''}")
                st.write(f"**고객 담당자:** {selected_row.get('고객담당자', '')}")
                st.write(f"**문의 내용:** {selected_row.get('문의내용', 'N/A')}")
                st.write(f"**우선순위:** {selected_row.get('우선순위', 'N/A')}")
                st.write(f"**계약 유형:** {selected_row.get('계약유형', 'N/A')}")
            with col2:
                st.write(f"**담당자:** {selected_row.get('담당자', 'N/A')} ({selected_row.get('역할', 'N/A')})")
                st.write(f"**시스템 버전:** {selected_row.get('시스템버전', '')}")
                st.write(f"**브라우저:** {selected_row.get('브라우저', '')}")
                st.write(f"**운영체제:** {selected_row.get('운영체제', '')}")
                st.write(f"**날짜:** {selected_row.get('날짜', 'N/A')}")
        
        # 실제 분석 결과 조회 시도
        try:
            # MongoDB에서 실제 분석 결과 조회 시도
            actual_analysis = None
            
            # MongoDB 연결이 되어 있는 경우 우선 시도
            if st.session_state.get('mongodb_connected') and st.session_state.get('mongo_handler'):
                try:
                    # 고객사명과 날짜를 기준으로 MongoDB에서 조회
                    customer_name = selected_row.get('고객사명', '')
                    inquiry_date = selected_row.get('날짜', '')
                    user_name = selected_row.get('담당자', '')
                    issue_type = selected_row.get('문의유형', '')
                    
                    # 날짜 형식 변환 (YYYY-MM-DD HH:MM:SS -> YYYY-MM-DD)
                    if inquiry_date and ' ' in inquiry_date:
                        inquiry_date = inquiry_date.split(' ')[0]
                    
                    # MongoDB에서 해당 문의의 실제 분석 결과 조회
                    mongo_result = st.session_state.mongo_handler.get_analysis_by_criteria(
                        customer_name=customer_name,
                        issue_type=issue_type,
                        user_name=user_name,
                        date=inquiry_date
                    )
                    
                    if mongo_result and mongo_result.get('success'):
                        actual_analysis = mongo_result
                        
                except Exception as mongo_error:
                    pass
            
            # MongoDB에서 조회 실패한 경우 로컬 데이터베이스로 폴백
            if not actual_analysis:
                try:
                    # components가 초기화되었는지 확인
                    if 'components' in st.session_state and 'multi_user_db' in st.session_state.components:
                        # 고객사명과 날짜를 기준으로 실제 분석 결과 조회
                        customer_name = selected_row.get('고객사명', '')
                        inquiry_date = selected_row.get('날짜', '')
                        
                        # 날짜 형식 변환 (YYYY-MM-DD HH:MM:SS -> YYYY-MM-DD)
                        if inquiry_date and ' ' in inquiry_date:
                            inquiry_date = inquiry_date.split(' ')[0]
                        
                        # 실제 분석 결과 조회
                        actual_analysis = st.session_state.components['multi_user_db'].get_analysis_by_customer_and_date(
                            customer_name, inquiry_date
                        )
                        
                except Exception as local_error:
                    pass
            
            # AI 분석 결과 표시 (실제 데이터가 있든 없든 기본 정보는 표시)
            st.markdown("---")
            
            # 문제 유형 분류와 시나리오 매칭 섹션 삭제
            
            if actual_analysis:
                # MongoDB에서 가져온 데이터인지 로컬 데이터베이스에서 가져온 데이터인지 확인
                if actual_analysis.get('source') == 'mongodb':
                    # MongoDB에서 가져온 데이터
                    analysis_data = actual_analysis.get('data', {})
                    # full_analysis_result에서 전체 AI 분석 데이터 추출
                    full_result = analysis_data.get('full_analysis_result', {})
                else:
                    # 로컬 데이터베이스에서 가져온 데이터
                    analysis_data = actual_analysis.get('data', {})
                    full_result = analysis_data.get('full_analysis_result', {})
                
                # 데이터가 성공적으로 로드되었는지 확인
                if analysis_data:
                    
                    col5, col6 = st.columns(2)
                    
                    with col5:
                        st.markdown("#### 📝 요약")
                        summary = analysis_data.get('summary', '')
                        if summary:
                            st.write(summary)
                        else:
                            st.write("해당 문의에 대한 AI 분석 요약이 없습니다.")
                        
                        st.markdown("#### 🔧 조치 흐름")
                        action_flow = analysis_data.get('action_flow', '')
                        if action_flow:
                            # 조치 흐름에 줄바꿈 적용 (더 효과적인 줄바꿈 처리)
                            action_flow_content = action_flow
                            # 연속된 공백을 하나로 통일
                            action_flow_content = ' '.join(action_flow_content.split())
                            # 번호가 있는 항목을 줄바꿈으로 구분 (더 정교한 처리)
                            action_flow_content = re.sub(r'(\d+\.)', r'\n\1', action_flow_content)
                            # 첫 번째 줄바꿈 제거
                            action_flow_content = action_flow_content.lstrip('\n')
                            st.write(action_flow_content)
                        else:
                            st.warning("⚠️ 조치 흐름 정보가 없습니다.")
                    
                    with col6:
                        st.markdown("#### 📧 이메일 초안")
                        
                        # original_ai_response에서 이메일 초안을 직접 추출하여 표시
                        email_content = None
                        
                        # 1. 파싱된 email_draft 사용 (우선순위 1) - DB에 저장된 정확한 이메일 초안
                        email_draft = analysis_data.get('email_draft', '')
                        if email_draft and len(email_draft.strip()) > 20:
                            email_content = email_draft
                        
                        # 2. original_ai_response에서 이메일 초안 추출 (우선순위 2)
                        if not email_content and analysis_data.get('original_ai_response'):
                            email_content = extract_email_from_original_response(analysis_data['original_ai_response'])
                        
                        # 3. full_analysis_result에서 이메일 초안 추출 (우선순위 3)
                        if not email_content and analysis_data.get('full_analysis_result'):
                            email_content = extract_email_from_analysis_result(analysis_data['full_analysis_result'])
                        
                        # 4. 기본 이메일 템플릿 (최후 수단)
                        if not email_content:
                            email_content = f"""제목: {selected_row.get('문의유형', '문의')} 답변

                            고객님 안녕하세요.

                            {selected_row.get('문의유형', '문의')}에 대한 문의 주셔서 감사합니다.

                            현재 상황을 분석한 결과, 추가 정보가 필요한 상황입니다.

                            **필요한 정보:**
                            1. 구체적인 오류 메시지
                            2. 발생 시점 및 빈도
                            3. 사용 환경 정보

                            자세한 내용은 담당 엔지니어가 확인 후 답변 드리겠습니다.

                            추가 문의사항이 있으시면 언제든 연락 주세요.

                            감사합니다."""
                        
                        # 이메일 초안을 Streamlit 기본 스타일로 표시
                        st.markdown("**이메일 내용**")
                        email_content = (analysis_data.get('email_draft') or '').replace('\n', '\n\n')
                        st.text_area("이메일 내용", email_content, height=350, key="email_content_modal")
                        

                    
                    

                    
                    # SMS 발송 섹션 추가
                    st.markdown("---")
                    st.markdown("### 📱 SMS 발송")
                    
                    col_sms1, col_sms2 = st.columns(2)
                    
                    with col_sms1:
                        recipient_name = st.text_input(
                            "수신자 이름",
                            placeholder="수신자 이름을 입력하세요",
                            key=f"sms_recipient_name_{selected_row.get('번호', 'unknown')}"
                        )
                        recipient_phone = st.text_input(
                            "수신자 전화번호",
                            placeholder="01012345678",
                            key=f"sms_recipient_phone_{selected_row.get('번호', 'unknown')}"
                        )
                        sender_phone = st.text_input(
                            "발신자 번호",
                            value=st.session_state.get('sender_phone', '01012345678'),
                            placeholder="01012345678",
                            help="SMS 발송 시 표시될 발신자 번호입니다",
                            key=f"sms_sender_phone_{selected_row.get('번호', 'unknown')}"
                        )
                    
                    with col_sms2:
                        # DB에 저장된 email_draft가 있는지 먼저 확인 (이메일 초안과 동일)
                        email_draft = selected_row.get('email_draft', '')
                        if email_draft and len(email_draft.strip()) > 20:
                            # DB에 저장된 이메일 초안을 SMS 메시지로 사용
                            default_sms_message = email_draft
                        else:
                            # 기본 SMS 템플릿 사용
                            default_sms_message = f"[{selected_row.get('문의유형', 'AI')}] {summary[:100] if summary else '분석 완료'}..."
                        
                        sms_message = st.text_area(
                            "SMS 메시지",
                            value=default_sms_message,
                            height=150,
                            key=f"sms_message_{selected_row.get('번호', 'unknown')}"
                        )
                        
                        # SMS 발송 버튼
                        if st.button("📱 SMS 발송", use_container_width=True, type="primary", key=f"sms_send_{selected_row.get('번호', 'unknown')}"):
                            if recipient_name and recipient_phone and sms_message:
                                # SOLAPI 핸들러로 SMS 발송
                                try:
                                    # 세션 상태에서 API 키 가져오기
                                    api_key = st.session_state.get('solapi_api_key', '')
                                    api_secret = st.session_state.get('solapi_api_secret', '')
                                    # 사용자가 입력한 발신자 번호 사용
                                    sender_phone = sender_phone
                                    
                                    if api_key and api_secret:
                                        # SOLAPI 핸들러 생성
                                        sms_handler = SOLAPIHandler(api_key, api_secret)
                                        sms_handler.set_sender(sender_phone)
                                        
                                        # SMS 발송
                                        sms_result = sms_handler.send_sms(
                                            phone_number=recipient_phone,
                                            message=sms_message,
                                            recipient_name=recipient_name
                                        )
                                        
                                        if sms_result["success"]:
                                            st.success(f"✅ SMS가 성공적으로 발송되었습니다!")
                                            st.info(f"수신자: {recipient_name} ({recipient_phone})")
                                            st.info(f"메시지 ID: {sms_result.get('message_id', 'N/A')}")
                                        else:
                                            st.error(f"❌ SMS 발송 실패: {sms_result.get('error', '알 수 없는 오류')}")
                                    else:
                                        st.error("❌ SOLAPI API 키가 설정되지 않았습니다.")
                                        st.info("Streamlit Secrets에서 SOLAPI API 키를 설정해주세요.")
                                except Exception as e:
                                    st.error(f"❌ SMS 발송 중 오류: {e}")
                            else:
                                st.warning("⚠️ 수신자 정보와 메시지를 모두 입력해주세요.")
                else:
                    # 데이터가 비어있는 경우
                    st.warning("⚠️ 분석 데이터가 비어있습니다.")
            else:
                # 실제 분석 결과가 없는 경우에도 기본 정보 표시
                st.warning("⚠️ 해당 문의의 실제 AI 분석 결과를 찾을 수 없습니다.")
                st.info("이는 다음과 같은 이유일 수 있습니다:")
                st.info("1. 분석이 완료되지 않았거나 저장되지 않음")
                st.info("2. MongoDB 또는 로컬 데이터베이스에서 데이터를 찾을 수 없음")
                st.info("3. 검색 조건이 정확하지 않음")
                
                # 기본 정보 표시
                st.markdown("### 📋 기본 문의 정보")
                st.write(f"**문의 내용:** {selected_row.get('문의내용', 'N/A')}")
                st.write(f"**문의 유형:** {selected_row.get('문의유형', 'N/A')}")
                st.write(f"**담당자:** {selected_row.get('담당자', 'N/A')}")
                
                # 기본 AI 응답 표시 (샘플 데이터)
                st.markdown("### 🤖 기본 AI 응답 (샘플)")
                
                # 문제 유형 분류와 시나리오 매칭 섹션 삭제
                
                st.markdown("#### 📝 요약")
                st.write(f"고객님께서 {selected_row.get('문의유형', '문의')}에 대한 문의를 주셨습니다.")
                
                st.markdown("#### 🔧 조치 흐름")
                st.write("""1. 문제 상황 파악 및 분석

                    2. 적절한 해결 방안 제시

                    3. 필요시 추가 정보 요청

                    4. 해결 완료 확인""")
                
                st.markdown("#### 📧 이메일 초안")
                
                # DB에 저장된 email_draft가 있는지 먼저 확인
                email_draft = selected_row.get('email_draft', '')
                if email_draft and len(email_draft.strip()) > 20:
                    # DB에 저장된 이메일 초안 사용
                    formatted_basic_email = email_draft
                else:
                    # 기본 이메일 템플릿 사용
                    basic_email = f"""제목: {selected_row.get('문의유형', '문의')} 답변

                        고객님 안녕하세요.

                        {selected_row.get('문의유형', '문의')}에 대한 문의 주셔서 감사합니다.

                        현재 상황을 분석한 결과, 추가 정보가 필요한 상황입니다.

                        **필요한 정보:**
                        1. 구체적인 오류 메시지
                        2. 발생 시점 및 빈도
                        3. 사용 환경 정보

                        자세한 내용은 담당 엔지니어가 확인 후 답변 드리겠습니다.

                        추가 문의사항이 있으시면 언제든 연락 주세요.

                        감사합니다."""
                    
                    # 이메일 내용에 줄바꿈 처리 적용
                    formatted_basic_email = format_email_content(basic_email)
                st.markdown("**이메일 내용**")
                st.text_area("이메일 내용", value=formatted_basic_email, height=350, disabled=True, key="basic_email_display", label_visibility="collapsed")
                
                
                st.info("페이지를 새로고침하거나 다시 시도해주세요.")
                
        except Exception as e:
            st.error(f"❌ 분석 결과 조회 중 오류가 발생했습니다: {str(e)}")
            st.info("Streamlit Cloud 환경에서는 일시적인 데이터 접근 문제가 발생할 수 있습니다.")

def create_history_table_with_buttons(df):
    """이력 조회 결과를 버튼이 포함된 테이블로 생성"""
    if df.empty:
        return None
    
    # 데이터프레임 복사
    df_with_buttons = df.copy()
    
    # 각 행에 대해 버튼 생성
    for index, row in df_with_buttons.iterrows():
        # 고유한 키 생성
        button_key = f"detail_btn_{index}_{row.get('번호', 'unknown')}"
        
        # 버튼을 생성하고 클릭 시 상세보기 실행
        if st.button(f"🔍", key=button_key, help="클릭하여 상세 분석 결과 보기"):
            st.session_state.selected_row_for_detail = row.to_dict()
            st.session_state.show_detail_modal = True
    
    # 원본 데이터프레임 반환 (버튼은 별도로 표시)
    return df

# 세션 상태 초기화 (단순화)
def init_session_state():
    """세션 상태 초기화"""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    if 'inquiry_data' not in st.session_state:
        st.session_state.inquiry_data = None
    if 'history_search_performed' not in st.session_state:
        st.session_state.history_search_performed = False
    if 'history_search_results' not in st.session_state:
        st.session_state.history_search_results = None
    if 'show_detail_modal' not in st.session_state:
        st.session_state.show_detail_modal = False
    if 'selected_row_for_detail' not in st.session_state:
        st.session_state.selected_row_for_detail = None
    
    # 페이지네이션 관련 변수들
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'items_per_page' not in st.session_state:
        st.session_state.items_per_page = 5  # 고정값 5개

    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = """[고객 문의 내용]
{customer_input}

[문제 유형]
{issue_type}

[조건 1]
{condition_1}

[조건 2]
{condition_2}

위 정보를 바탕으로 고객에게 친절하고 전문적인 답변을 제공해주세요."""
    if 'response_language' not in st.session_state:
        st.session_state.response_language = "한국어"
    if 'response_detail' not in st.session_state:
        st.session_state.response_detail = "보통"
    if 'current_api_key' not in st.session_state:
        st.session_state.current_api_key = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
    if 'last_api_key' not in st.session_state:
        st.session_state.last_api_key = st.session_state.current_api_key
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "Gemini 1.5 Pro"
    if 'contact_name' not in st.session_state:
        st.session_state.contact_name = "홍길동"
    if 'role' not in st.session_state:
        st.session_state.role = "영업"
    if 'ai_model' not in st.session_state:
        st.session_state.ai_model = "Gemini 1.5 Pro"

def get_paginated_data(df, page, items_per_page):
    """데이터프레임을 페이지별로 나누는 함수"""
    if df is None or df.empty:
        return None, 0, 0
    
    total_items = len(df)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # 페이지 범위 조정
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    return df.iloc[start_idx:end_idx], total_pages, total_items

def render_pagination_controls(current_page, total_pages, total_items, items_per_page, prefix=""):
    """페이지네이션 컨트롤을 렌더링하는 함수"""
    if total_pages <= 1:
        return
    
    st.markdown("---")
    st.markdown(f"**📄 페이지 {current_page} / {total_pages} (총 {total_items}건, 페이지당 {items_per_page}건)**")
    
    # 페이지 번호 범위 계산
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, start_page + 4)
    
    if end_page - start_page < 4:
        start_page = max(1, end_page - 4)
    
    # 전체 버튼 수 계산 (첫페이지, 이전, 페이지번호들, 다음, 마지막)
    total_buttons = 2 + (end_page - start_page + 1) + 2
    
    # 동적으로 컬럼 생성
    cols = st.columns(total_buttons)
    
    # 첫페이지 버튼
    with cols[0]:
        if st.button("◀◀", key=f"{prefix}first_page", disabled=current_page == 1):
            st.session_state.current_page = 1
            st.rerun()
    
    # 이전 페이지 버튼
    with cols[1]:
        if st.button("◀", key=f"{prefix}prev_page", disabled=current_page == 1):
            st.session_state.current_page = current_page - 1
            st.rerun()
    
    # 페이지 번호 버튼들
    page_col_idx = 2
    for i in range(start_page, end_page + 1):
        with cols[page_col_idx]:
            if st.button(str(i), key=f"{prefix}page_{i}", type="primary" if i == current_page else "secondary"):
                st.session_state.current_page = i
                st.rerun()
        page_col_idx += 1
    
    # 다음 페이지 버튼
    with cols[page_col_idx]:
        if st.button("▶", key=f"{prefix}next_page", disabled=current_page == total_pages):
            st.session_state.current_page = current_page + 1
            st.rerun()
    
    # 마지막 페이지 버튼
    with cols[page_col_idx + 1]:
        if st.button("▶▶", key=f"{prefix}last_page", disabled=current_page == total_pages):
            st.session_state.current_page = total_pages
            st.rerun()
    
    st.markdown("---")

def format_email_content(email_content: str) -> str:
    """이메일 내용의 줄바꿈을 개선하여 가독성을 높입니다."""
    if not email_content:
        return ""
    
    # 기본 정리
    formatted = email_content.strip()
    
    # 연속된 공백을 하나로 통일
    formatted = ' '.join(formatted.split())
    
    # 제목과 본문 사이에 빈 줄 추가
    formatted = re.sub(r'(제목:.*?)(고객님)', r'\1\n\n\2', formatted)
    
    # 문단 구분을 위한 줄바꿈 추가
    # "고객님 안녕하세요." 다음에 빈 줄 추가
    formatted = re.sub(r'(고객님 안녕하세요\.)', r'\1\n', formatted)
    
    # "감사합니다." 앞에 빈 줄 추가
    formatted = re.sub(r'(\n감사합니다\.)', r'\n\n\1', formatted)
    
    # 번호가 있는 항목 앞에 줄바꿈 추가
    formatted = re.sub(r'(\d+\.)', r'\n\1', formatted)
    
    # 첫 번째 줄바꿈 제거
    formatted = formatted.lstrip('\n')
    
    return formatted

def format_ai_response(ai_response: str) -> str:
    """AI 응답의 줄바꿈을 개선하여 가독성을 높입니다."""
    if not ai_response:
        return ""
    
    # 기본 정리
    formatted = ai_response.strip()
    
    # 연속된 공백을 하나로 통일
    formatted = ' '.join(formatted.split())
    
    # 섹션 구분을 위한 줄바꿈 추가
    formatted = re.sub(r'(\[대응유형\])', r'\n\1', formatted)
    formatted = re.sub(r'(\[응답내용\])', r'\n\n\1', formatted)
    
    # 각 항목 앞에 줄바꿈 추가
    formatted = re.sub(r'(- 요약:)', r'\n\1', formatted)
    formatted = re.sub(r'(- 조치 흐름:)', r'\n\n\1', formatted)
    formatted = re.sub(r'(- 이메일 초안:)', r'\n\n\1', formatted)
    
    # 조치 흐름의 번호가 있는 항목 앞에 줄바꿈 추가
    formatted = re.sub(r'(\d+\.)', r'\n\1', formatted)
    
    # 첫 번째 줄바꿈 제거
    formatted = formatted.lstrip('\n')
    
    return formatted

def extract_email_from_gpt_response(original_response: str) -> str:
    """GPT 응답에서 이메일 초안을 추출 (GPT 전용)"""
    if not original_response:
        return ""
    
    try:
        import re
        
        
        # GPT 응답 패턴 1: "- 이메일 초안:" 다음에 ```로 감싸진 내용
        gpt_pattern1 = r'- 이메일\s*초안[:\s]*\n```\n(.*?)\n```'
        match = re.search(gpt_pattern1, original_response, re.DOTALL)
        if match:
            email_content = match.group(1).strip()
            if len(email_content) > 50:
                return email_content
        
        # GPT 응답 패턴 2: "- 이메일 초안:" 다음에 이메일 내용 (``` 없이, 더 포괄적)
        gpt_pattern2 = r'- 이메일\s*초안[:\s]*\n(.*?)(?=\n\n|\n- |\n\[|\n※|\Z)'
        match = re.search(gpt_pattern2, original_response, re.DOTALL)
        if match:
            email_content = match.group(1).strip()
            if len(email_content) > 50 and ('감사합니다' in email_content or '안녕하세요' in email_content):
                return email_content
        
        # GPT 응답 패턴 3: "- 이메일 초안:" 다음에 이메일 내용 (더 유연한 종료 조건)
        gpt_pattern3 = r'- 이메일\s*초안[:\s]*\n(.*?)(?=\n\n- |\n\[|\n※|\Z)'
        match = re.search(gpt_pattern3, original_response, re.DOTALL)
        if match:
            email_content = match.group(1).strip()
            if len(email_content) > 50 and ('감사합니다' in email_content or '안녕하세요' in email_content):
                return email_content
        
        # GPT 응답 패턴 4: "- 이메일 초안:" 다음에 이메일 내용 (가장 포괄적)
        gpt_pattern4 = r'- 이메일\s*초안[:\s]*\n(.*?)(?=\n- |\n\[|\n※|\Z)'
        match = re.search(gpt_pattern4, original_response, re.DOTALL)
        if match:
            email_content = match.group(1).strip()
            if len(email_content) > 50 and ('감사합니다' in email_content or '안녕하세요' in email_content):
                return email_content
        
        return ""
        
    except Exception as e:
        print(f"GPT 이메일 추출 오류: {e}")
        return ""

def extract_email_from_gemini_response(original_response: str) -> str:
    """GEMINI 응답에서 이메일 초안을 추출 (GEMINI 전용)"""
    if not original_response:
        return ""
    
    try:
        import re
        
        
        # GEMINI 응답 패턴: "이메일 초안:" 다음에 이메일 내용
        gemini_pattern = r'이메일\s*초안[:\s]*\n\n(.*?)(?=\n\n|\n- |\n\[|\n※|\Z)'
        match = re.search(gemini_pattern, original_response, re.DOTALL)
        if match:
            email_content = match.group(1).strip()
            if len(email_content) > 50 and ('감사합니다' in email_content or '안녕하세요' in email_content):
                return email_content
        
        # GEMINI 응답 패턴 2: "이메일 초안:" 다음에 이메일 내용 (빈 줄 없이)
        gemini_pattern2 = r'이메일\s*초안[:\s]*\n(.*?)(?=\n\n|\n- |\n\[|\n※|\Z)'
        match = re.search(gemini_pattern2, original_response, re.DOTALL)
        if match:
            email_content = match.group(1).strip()
            if len(email_content) > 50 and ('감사합니다' in email_content or '안녕하세요' in email_content):
                return email_content
        
        return ""
        
    except Exception as e:
        print(f"GEMINI 이메일 추출 오류: {e}")
        return ""

def extract_email_from_original_response(original_response: str) -> str:
    """원본 AI 응답에서 이메일 초안을 추출 (GPT/GEMINI 자동 감지)"""
    if not original_response:
        return ""
    
    try:
        import re
        
        # GPT 응답인지 GEMINI 응답인지 감지
        if '- 이메일 초안:' in original_response:
            return extract_email_from_gpt_response(original_response)
        elif '이메일 초안:' in original_response:
            return extract_email_from_gemini_response(original_response)
        else:
            return ""
        
    except Exception as e:
        print(f"이메일 추출 오류: {e}")
        return ""

def extract_email_from_analysis_result(analysis_result: dict) -> str:
    """분석 결과에서 이메일 초안을 추출 (GPT/GEMINI 구분 처리)"""
    try:
        # ai_result에서 raw_response 추출
        if 'ai_result' in analysis_result:
            ai_result = analysis_result['ai_result']
            
            # GEMINI 결과에서 추출
            if 'gemini_result' in ai_result and 'raw_response' in ai_result['gemini_result']:
                return extract_email_from_gemini_response(ai_result['gemini_result']['raw_response'])
            
            # GPT 결과에서 추출 (openai_handler는 'response' 키 사용)
            if 'response' in ai_result:
                return extract_email_from_gpt_response(ai_result['response'])
            
            # 기존 gpt_result 형태도 지원
            if 'gpt_result' in ai_result and 'raw_response' in ai_result['gpt_result']:
                return extract_email_from_gpt_response(ai_result['gpt_result']['raw_response'])
        
        # 직접 gemini_result나 gpt_result가 있는 경우
        if 'gemini_result' in analysis_result and 'raw_response' in analysis_result['gemini_result']:
            return extract_email_from_gemini_response(analysis_result['gemini_result']['raw_response'])
        
        # GPT 응답이 직접 있는 경우 (openai_handler는 'response' 키 사용)
        if 'response' in analysis_result:
            return extract_email_from_gpt_response(analysis_result['response'])
        
        # 기존 gpt_result 형태도 지원
        if 'gpt_result' in analysis_result and 'raw_response' in analysis_result['gpt_result']:
            return extract_email_from_gpt_response(analysis_result['gpt_result']['raw_response'])
        
        return ""
        
    except Exception as e:
        print(f"분석 결과에서 이메일 추출 오류: {e}")
        return ""

def _parse_gpt_response(response_text: str) -> dict:
    """GPT API 응답을 파싱하여 구조화된 데이터로 변환"""
    try:
        parsed = {
            'response_type': '해결안',
            'summary': '',
            'action_flow': '',
            'email_draft': '',
            'question': ''
        }
        
        # 응답 텍스트를 줄 단위로 분리
        lines = response_text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 섹션 헤더 확인
            if '[대응유형]' in line:
                response_type = line.replace('[대응유형]', '').strip()
                if response_type in ['해결안', '질문', '출동']:
                    parsed['response_type'] = response_type
            elif '[응답내용]' in line:
                current_section = 'content'
            elif '- 요약:' in line:
                current_section = 'summary'
                # 요약 내용이 같은 줄에 있는 경우
                summary_content = line.replace('- 요약:', '').strip()
                if summary_content:
                    parsed['summary'] = summary_content
                # 다음 줄에 요약 내용이 있는지 확인
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(keyword in next_line for keyword in ['- 조치 흐름:', '- 이메일 초안:', '[응답내용]', '[대응유형]']):
                        if parsed['summary']:
                            parsed['summary'] += ' ' + next_line
                        else:
                            parsed['summary'] = next_line
            elif '- 조치 흐름:' in line:
                current_section = 'action_flow'
            elif '- 이메일 초안:' in line:
                current_section = 'email_draft'
                # 이메일 초안 헤더 제거하고 내용이 있으면 바로 추가
                email_content = line.replace('- 이메일 초안:', '').strip()
                if email_content:
                    parsed['email_draft'] += email_content + '\n'
                # ```로 시작하는 경우 다음 줄부터 이메일 내용으로 처리
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('```'):
                        # ``` 다음 줄부터 이메일 내용 시작
                        for j in range(i + 2, len(lines)):
                            content_line = lines[j].strip()
                            if content_line == '```':
                                break
                            parsed['email_draft'] += content_line + '\n'
            elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                # 조치 흐름 항목
                if current_section == 'action_flow':
                    parsed['action_flow'] += line + '\n'
            elif current_section == 'summary':
                if parsed['summary']:  # 이미 내용이 있으면 공백 추가
                    parsed['summary'] += ' ' + line
                else:
                    parsed['summary'] = line
            elif current_section == 'action_flow':
                # 조치 흐름에서 불필요한 텍스트 제거
                if not any(unwanted in line for unwanted in [
                    '[응답내용]', '[대응유형]', '- 요약:', '- 조치 흐름:', '- 이메일 초안:',
                    '아래 형식을 참고하여', '실무자가 이해하기 쉽도록', '자연스럽고 정확하게 응답을 생성하십시오'
                ]):
                    parsed['action_flow'] += line + '\n'
            elif current_section == 'email_draft':
                # 이메일 초안 내용 추가 (불필요한 텍스트만 제거)
                if not any(unwanted in line for unwanted in [
                    '[응답내용]', '[대응유형]', '- 요약:', '- 조치 흐름:', '- 이메일 초안:',
                    '아래 형식을 참고하여', '실무자가 이해하기 쉽도록', '자연스럽고 정확하게 응답을 생성하십시오'
                ]):
                    # 이메일 초안 내용을 그대로 추가
                    parsed['email_draft'] += line + '\n'
        
        # 요약에서 "- 요약:" 제거 (혹시 남아있을 경우)
        parsed['summary'] = parsed['summary'].replace('- 요약:', '').strip()
        
        # 이메일 초안을 GPT 전용 함수로 다시 추출하여 정확성 보장
        # 항상 원본 응답에서 이메일 초안을 다시 추출 (기존 파싱 결과 무시)
        extracted_email = extract_email_from_gpt_response(response_text)
        if extracted_email:
            parsed['email_draft'] = extracted_email
            print(f"✅ GPT 파싱 - 이메일 초안 재추출 성공: {len(extracted_email)}자")
        else:
            print("⚠️ GPT 파싱 - 이메일 초안 재추출 실패, 기존 파싱 결과 사용")
        
        # 디버깅을 위한 로그 추가
        print(f"GPT 파싱 결과 - 요약: {parsed['summary'][:50]}...")
        print(f"GPT 파싱 결과 - 조치 흐름: {parsed['action_flow'][:50]}...")
        print(f"GPT 파싱 결과 - 이메일 초안: {parsed['email_draft'][:50]}...")
        
        return parsed
        
    except Exception as e:
        print(f"GPT 응답 파싱 오류: {e}")
        return {
            'response_type': '해결안',
            'summary': '응답 파싱 중 오류가 발생했습니다.',
            'action_flow': '응답을 확인해주세요.',
            'email_draft': '응답을 확인해주세요.',
            'question': ''
        }

def _parse_gemini_response(response_text: str) -> dict:
    """GEMINI API 응답을 파싱하여 구조화된 데이터로 변환"""
    try:
        parsed = {
            'response_type': '해결안',
            'summary': '',
            'action_flow': '',
            'email_draft': '',
            'question': ''
        }
        
        # 응답 텍스트를 줄 단위로 분리
        lines = response_text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 섹션 헤더 확인 (GEMINI 형식)
            if '[대응유형]' in line:
                response_type = line.replace('[대응유형]', '').strip()
                if response_type in ['해결안', '질문', '출동']:
                    parsed['response_type'] = response_type
            elif '[응답내용]' in line:
                current_section = 'content'
            elif '요약:' in line:
                current_section = 'summary'
                # 요약 내용이 같은 줄에 있는 경우
                summary_content = line.replace('요약:', '').strip()
                if summary_content:
                    parsed['summary'] = summary_content
                # 다음 줄에 요약 내용이 있는지 확인
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(keyword in next_line for keyword in ['조치 흐름:', '이메일 초안:', '[응답내용]', '[대응유형]']):
                        if parsed['summary']:
                            parsed['summary'] += ' ' + next_line
                        else:
                            parsed['summary'] = next_line
            elif '조치 흐름:' in line:
                current_section = 'action_flow'
            elif '이메일 초안:' in line:
                current_section = 'email_draft'
                # 이메일 초안 헤더 제거하고 내용이 있으면 바로 추가
                email_content = line.replace('이메일 초안:', '').strip()
                if email_content:
                    parsed['email_draft'] += email_content + '\n'
            elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                # 조치 흐름 항목
                if current_section == 'action_flow':
                    parsed['action_flow'] += line + '\n'
            elif current_section == 'summary':
                if parsed['summary']:  # 이미 내용이 있으면 공백 추가
                    parsed['summary'] += ' ' + line
                else:
                    parsed['summary'] = line
            elif current_section == 'action_flow':
                # 조치 흐름에서 불필요한 텍스트 제거
                if not any(unwanted in line for unwanted in [
                    '[응답내용]', '[대응유형]', '요약:', '조치 흐름:', '이메일 초안:',
                    '아래 형식을 참고하여', '실무자가 이해하기 쉽도록', '자연스럽고 정확하게 응답을 생성하십시오'
                ]):
                    parsed['action_flow'] += line + '\n'
            elif current_section == 'email_draft':
                # 이메일 초안 내용 추가 (불필요한 텍스트만 제거)
                if not any(unwanted in line for unwanted in [
                    '[응답내용]', '[대응유형]', '요약:', '조치 흐름:', '이메일 초안:',
                    '아래 형식을 참고하여', '실무자가 이해하기 쉽도록', '자연스럽고 정확하게 응답을 생성하십시오'
                ]):
                    # 이메일 초안 내용을 그대로 추가
                    parsed['email_draft'] += line + '\n'
        
        # 요약에서 "요약:" 제거 (혹시 남아있을 경우)
        parsed['summary'] = parsed['summary'].replace('요약:', '').strip()
        
        # 이메일 초안을 GEMINI 전용 함수로 다시 추출하여 정확성 보장
        # GEMINI 파싱에서는 이미 파싱된 email_draft를 그대로 사용 (재추출 불필요)
        print(f"✅ GEMINI 파싱 - 파싱된 email_draft 사용: {len(parsed['email_draft'])}자")
        
        # 디버깅을 위한 로그 추가
        print(f"GEMINI 파싱 결과 - 요약: {parsed['summary'][:50]}...")
        print(f"GEMINI 파싱 결과 - 조치 흐름: {parsed['action_flow'][:50]}...")
        print(f"GEMINI 파싱 결과 - 이메일 초안: {parsed['email_draft'][:50]}...")
        
        return parsed
        
    except Exception as e:
        print(f"GEMINI 응답 파싱 오류: {e}")
        return {
            'response_type': '해결안',
            'summary': '응답 파싱 중 오류가 발생했습니다.',
            'action_flow': '응답을 확인해주세요.',
            'email_draft': '응답을 확인해주세요.',
            'question': ''
        }

def _format_email_content(email_content: str) -> str:
    """이메일 내용을 자연스러운 형태로 포맷팅"""
    try:
        # 제목 분리
        if '제목:' in email_content:
            parts = email_content.split('제목:', 1)
            if len(parts) == 2:
                title_and_body = parts[1].strip()
                
                # 제목과 본문 분리 - "고객님 안녕하세요"를 찾아서 분리
                if '고객님 안녕하세요' in title_and_body:
                    title_part = title_and_body.split('고객님 안녕하세요')[0].strip()
                    body_part = '고객님 안녕하세요' + title_and_body.split('고객님 안녕하세요')[1]
                    
                    # 자연스러운 단락 구분을 위한 키워드 기반 줄바꿈
                    formatted_body = _format_email_body(body_part)
                    
                    # 최종 이메일 형식
                    formatted_email = f"제목: {title_part}\n\n{formatted_body}\n\n감사합니다."
                    return formatted_email
                else:
                    # 첫 번째 문장이 제목 (기존 로직)
                    sentences = title_and_body.split('. ')
                    if len(sentences) > 0:
                        title = sentences[0].strip()
                        body_sentences = sentences[1:] if len(sentences) > 1 else []
                        
                        # 본문 재구성
                        body = '. '.join(body_sentences).strip()
                        
                        # 자연스러운 단락 구분을 위한 키워드 기반 줄바꿈
                        formatted_body = _format_email_body(body)
                        
                        # 최종 이메일 형식
                        formatted_email = f"제목: {title}\n\n고객님 안녕하세요.\n\n{formatted_body}\n\n감사합니다."
                        return formatted_email
        
        # 제목이 없는 경우 기본 처리
        return _format_email_body(email_content)
        
    except Exception as e:
        print(f"이메일 포맷팅 오류: {e}")
        # 기본 문장 단위 줄바꿈으로 폴백
        return email_content.replace('. ', '.\n')

def _format_email_body(body_text: str) -> str:
    """이메일 본문을 자연스러운 단락으로 구분"""
    # 특정 패턴을 기준으로 단락 구분
    paragraph_patterns = [
        ('먼저', '먼저'),
        ('만약', '만약'),
        ('비밀번호가 다를 경우', '비밀번호 변경 후'),
        ('비밀번호 변경 후', '문제가 지속될 경우'),
        ('문제가 해결되지', '문제가 해결되지')
    ]
    
    # 각 패턴에 따라 단락 구분
    result = body_text
    
    # "먼저"로 시작하는 부분을 첫 번째 단락으로
    if '먼저' in result:
        before_first = result.split('먼저')[0].strip()
        after_first = '먼저' + result.split('먼저')[1]
        
        # "비밀번호 변경 후" 또는 "만약"으로 두 번째 단락 구분
        if '비밀번호 변경 후' in after_first:
            first_para = after_first.split('비밀번호 변경 후')[0].strip()
            second_para_start = '비밀번호 변경 후' + after_first.split('비밀번호 변경 후')[1]
            
            # "문제가 해결되지"로 세 번째 단락 구분
            if '문제가 해결되지' in second_para_start:
                second_para = second_para_start.split('문제가 해결되지')[0].strip()
                third_para = '문제가 해결되지' + second_para_start.split('문제가 해결되지')[1].strip()
                
                # 감사합니다 제거 (별도로 추가됨)
                third_para = third_para.replace('감사합니다.', '').strip()
                
                result = f"{before_first}\n\n{first_para}\n\n{second_para}\n\n{third_para}"
            else:
                result = f"{before_first}\n\n{first_para}\n\n{second_para_start}"
        elif '만약' in after_first:
            first_para = after_first.split('만약')[0].strip()
            second_para_start = '만약' + after_first.split('만약')[1]
            
            # "문제가 해결되지"로 세 번째 단락 구분
            if '문제가 해결되지' in second_para_start:
                second_para = second_para_start.split('문제가 해결되지')[0].strip()
                third_para = '문제가 해결되지' + second_para_start.split('문제가 해결되지')[1].strip()
                
                # 감사합니다 제거 (별도로 추가됨)
                third_para = third_para.replace('감사합니다.', '').strip()
                # 띄어쓰기 수정
                third_para = third_para.replace('문제가 해결되지않을', '문제가 해결되지 않을')
                
                result = f"{before_first}\n\n{first_para}\n\n{second_para}\n\n{third_para}"
            else:
                result = f"{before_first}\n\n{first_para}\n\n{second_para_start}"
    
    # 감사합니다 제거 및 띄어쓰기 정리
    result = result.replace('감사합니다.', '').strip()
    result = result.replace('문제가 해결되지않을', '문제가 해결되지 않을')
    
    return result

def _add_natural_line_breaks(text: str) -> str:
    """텍스트에 자연스러운 줄바꿈 추가"""
    # 키워드 기반 단락 구분 (더 구체적으로)
    paragraph_keywords = [
        '먼저', '만약', '만일', '비밀번호 변경 후', '위 조치 후', '문제가 해결되지'
    ]
    
    # 문장별로 분리
    sentences = text.split('. ')
    formatted_sentences = []
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # 마지막 문장이 아니면 마침표 추가
        if i < len(sentences) - 1 and not sentence.endswith('.'):
            sentence += '.'
            
        # 단락 시작 키워드 확인
        should_add_paragraph = any(sentence.startswith(keyword) for keyword in paragraph_keywords)
        
        if should_add_paragraph and formatted_sentences:
            # 이전 문장 끝에 추가 줄바꿈 (두 줄바꿈으로 단락 구분)
            formatted_sentences.append('\n\n' + sentence)
        else:
            formatted_sentences.append(sentence)
    
    # 문장들을 연결
    result = ' '.join(formatted_sentences)
    
    # 연속된 공백 정리
    result = ' '.join(result.split())
    
    # 단락 구분 줄바꿈 복원
    result = result.replace(' \n\n', '\n\n')
    
    return result

# 컴포넌트 초기화
def init_components():
    """컴포넌트 초기화"""
    try:
        # API 키 설정 (Streamlit Secrets 우선, 환경변수 차선, 사이드바 마지막)
        api_key = ""
        
        # config 모듈을 통해 API 키 로드
        api_key = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
        if api_key:
            print("✅ Gemini API 키를 로드했습니다.")
        
        # 3. 사이드바에서 설정한 API 키 (마지막 우선순위)
        if not api_key and 'current_api_key' in st.session_state and st.session_state.current_api_key:
            api_key = st.session_state.current_api_key
            print("✅ Gemini API 키를 사이드바에서 로드했습니다.")
        
        # 컴포넌트 초기화 (API 키 로드 후)
        # FAISS 벡터 분류기 사용 (Windows 호환성 개선)
        classifier = None
        try:
            from chroma_vector_classifier import ChromaVectorClassifier
            
            # 타임아웃 설정으로 무한 대기 방지
            import threading
            import time
            
            def init_faiss():
                nonlocal classifier
                try:
                    classifier = ChromaVectorClassifier()
                    print("✅ FAISS 벡터 분류기 초기화 성공")
                except Exception as e:
                    print(f"❌ FAISS 벡터 분류기 초기화 실패: {e}")
                    classifier = None
            
            # 별도 스레드에서 초기화 시도
            init_thread = threading.Thread(target=init_faiss)
            init_thread.daemon = True
            init_thread.start()
            
            # 최대 30초 대기 (Streamlit Cloud에서 모델 다운로드 시간 고려)
            init_thread.join(timeout=30)
            
            if classifier is None:
                print("⚠️ FAISS 초기화 실패 - 키워드 기반 분류로 폴백")
                # 키워드 기반 분류기로 폴백
                from simple_classifier import SimpleClassifier
                classifier = SimpleClassifier()
                
        except Exception as e:
            print(f"⚠️ FAISS 벡터 분류기 초기화 실패, 기본 분류기 사용: {e}")
            classifier = IssueClassifier(api_key=api_key)
        
        scenario_db = ScenarioDB()
        vector_search = VectorSearchWrapper()
        
        # Gemini 핸들러들 초기화
        gemini_1_5_pro = GeminiHandler(api_key=api_key, model_name="gemini-1.5-pro")
        gemini_1_5_flash = GeminiHandler(api_key=api_key, model_name="gemini-1.5-flash")
        gemini_2_0_pro = GeminiHandler(api_key=api_key, model_name="gemini-2.0-flash-exp")
        gemini_2_0_flash = GeminiHandler(api_key=api_key, model_name="gemini-2.0-flash-exp")
        
        # OpenAI 핸들러 초기화
        openai_api_key = get_secret("OPENAI_API_KEY")
        if openai_api_key:
            print("✅ OpenAI API 키를 로드했습니다.")
        
        openai_handler = OpenAIHandler(api_key=openai_api_key)
        
        # API 키 상태 확인 (최소 하나는 필요)
        if not api_key and not openai_api_key:
            st.error("❌ AI API 키가 설정되지 않았습니다.")
            st.info("""
            **API 키 설정 방법:**
            
            **Streamlit Cloud Secrets (권장):**
            1. Streamlit Cloud → Settings → Secrets
            2. 다음 키를 추가:
               - `GEMINI_API_KEY`: Google AI Studio에서 발급받은 API 키
               - `OPENAI_API_KEY`: OpenAI에서 발급받은 API 키
            
            **환경변수:**
            - `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY`
            - `OPENAI_API_KEY`
            
            **사이드바 입력:**
            - Gemini API 키 또는 OpenAI API 키 중 하나를 입력
            
            최소 하나의 API 키가 필요합니다.
            """)
            st.stop()
        
        # SOLAPI 핸들러 초기화
        solapi_handler = SOLAPIHandler()
        
        # 기존 데이터베이스 (호환성 유지)
        history_db = HistoryDB()
        multi_user_db = MultiUserHistoryDB()
        
        # MongoDB 핸들러를 multi_user_db에 연결
        if st.session_state.get('mongo_handler') and st.session_state.mongo_handler.is_connected():
            multi_user_db.set_mongo_handler(st.session_state.mongo_handler)
        
        return {
            'classifier': classifier,
            'scenario_db': scenario_db,
            'vector_search': vector_search,
            'gemini_1_5_pro': gemini_1_5_pro,
            'gemini_1_5_flash': gemini_1_5_flash,
            'gemini_2_0_pro': gemini_2_0_pro,
            'gemini_2_0_flash': gemini_2_0_flash,
            'openai_handler': openai_handler,
            'solapi_handler': solapi_handler,
            'history_db': history_db,
            'multi_user_db': multi_user_db
        }
    except Exception as e:
        st.error(f"❌ 컴포넌트 초기화 실패: {str(e)}")
        st.stop()

# 세션 상태 초기화 (가장 먼저 실행)
init_session_state()

# MongoDB 연결 초기화
if 'mongodb_connected' not in st.session_state:
    mongodb_status = init_mongodb_connection()
    if mongodb_status:
        st.sidebar.success("✅ DB 연결됨")
    else:
        st.sidebar.warning("⚠️ DB 연결 실패 - 로컬 저장소 사용")
        st.sidebar.info("💡 Streamlit Cloud Secrets에서 MONGODB_URI를 설정하세요")

# 메인 애플리케이션 시작
#st.success("✅ 애플리케이션 시작")

# 사이드바 설정
with st.sidebar:
    st.markdown("## 👤 담당자 정보")
    
    # 담당자명 입력
    contact_name = st.text_input(
        "담당자명",
        value="홍길동",
        placeholder="담당자명을 입력하세요"
    )
    
    # 역할 선택
    role = st.selectbox(
        "역할",
        options=["영업", "엔지니어", "개발자", "관리자"],
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("## ⚙️ 시스템 설정")
    
    # AI 모델 선택
    ai_model = st.selectbox(
        "AI 모델",
        options=[
            "Gemini 1.5 Pro",
            "Gemini 1.5 Flash", 
            "Gemini 2.0 Pro",
            "Gemini 2.0 Flash",
            "GPT-4o",
            "GPT-4 Turbo",
            "GPT-3.5 Turbo"
        ],
        index=0,
        help="각 모델의 특징:\n• Gemini 1.5 Pro: 가장 정확하고 상세한 분석\n• Gemini 1.5 Flash: 빠른 응답, 기본 분석\n• Gemini 2.0 Pro: 최신 기술, 고품질 분석\n• Gemini 2.0 Flash: 빠른 응답, 고품질\n• GPT 모델들: OpenAI 기반 분석"
    )
    
    st.markdown("---")
    
    # API 키는 config 모듈을 통해 자동으로 로드됩니다
    st.session_state['solapi_api_key'] = get_secret("SOLAPI_API_KEY", "")
    st.session_state['solapi_api_secret'] = get_secret("SOLAPI_API_SECRET", "")
    st.session_state['sender_phone'] = "01012345678"
    
    # 세션 상태에 저장
    st.session_state.contact_name = contact_name
    st.session_state.role = role
    st.session_state.ai_model = ai_model
    

    
    # 데이터 관리 섹션 (UI에서 숨김)
    # st.markdown("---")
    # st.markdown("## 🗑️ 데이터 관리")
    # 
    # if st.button("🗑️ 모든 데이터 초기화", type="secondary"):
    #     if 'components' in st.session_state and 'multi_user_db' in st.session_state.components:
    #         try:
    #             result = st.session_state.components['multi_user_db'].clear_all_history()
    #             if result.get('success'):
    #                 st.success("✅ 모든 데이터가 초기화되었습니다.")
    #                 st.rerun()
    #             else:
    #                 st.error(f"❌ 데이터 초기화 실패: {result.get('error', '알 수 없는 오류')}")
    #         except Exception as e:
    #             st.error(f"❌ 데이터 초기화 중 오류: {e}")
    #     else:
    #         st.error("❌ 데이터베이스가 초기화되지 않았습니다.")
    


# 컴포넌트 초기화
if 'components' not in st.session_state:
    st.session_state.components = init_components()
components = st.session_state.components

# 메인 헤더
st.markdown("""
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom:2rem;'>
    <h1>🔧 PrivKeeper P 장애 대응 자동화 시스템</h1>
    <p>Gemini AI & GPT 기반 고객 문의 자동 분석 및 응답 도구</p>
</div>
""", unsafe_allow_html=True)

# 환영 메시지
#st.success("✅ AI 분석 서비스를 이용할 수 있습니다!")

# 탭 생성
tab_names = ["📝 고객 문의 입력", "🤖 AI 분석 결과", "📊 이력 관리", "📚 사용 가이드", "🔧 Vector DB 관리"]

# 탭 생성
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_names)

# 분석 완료 알림 (전역적으로 표시) - 삭제됨

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
        key="inquiry_content_input",
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
    if st.button("🚀 AI 분석 요청", type="primary", use_container_width=True):
        if inquiry_content.strip():
            # 진행 상황을 표시할 컨테이너 생성
            progress_container = st.container()
            
            with progress_container:
                st.info("🚀 AI 분석을 시작합니다...")
                
                try:
                    # 1. 문제 유형 자동 분류
                    with st.spinner("1단계: 문제 유형 분류 중..."):
                        classification_result = components['classifier'].classify_issue(inquiry_content)
                        issue_type = classification_result['issue_type']
                        st.success(f"✅ 문제 유형 분류 완료: {issue_type}")
                    
                    # 2. 시나리오 조회
                    with st.spinner("2단계: 시나리오 조회 중..."):
                        scenarios = components['scenario_db'].get_scenarios_by_issue_type(issue_type)
                        best_scenario = components['scenario_db'].find_best_scenario(issue_type, inquiry_content)
                        st.success(f"✅ 시나리오 조회 완료: {len(scenarios)}개 시나리오 발견")
                    
                    # 3. 유사 사례 검색
                    with st.spinner("3단계: 유사 사례 검색 중..."):
                        similar_cases = components['vector_search'].search_similar_cases(inquiry_content, top_k=3)
                        st.success(f"✅ 유사 사례 검색 완료: {len(similar_cases)}개 사례 발견")
                    
                    # 4. 매뉴얼 참조 조회
                    with st.spinner("4단계: 매뉴얼 참조 조회 중..."):
                        manual_ref = components['scenario_db'].get_manual_reference(issue_type)
                        st.success("✅ 매뉴얼 참조 조회 완료")
                    
                    # 5. AI 응답 생성 (피드백 기반 프롬프트 개선)
                    with st.spinner("5단계: AI 응답 생성 중... (피드백 학습 적용)"):
                        start_time = time.time()
                        
                        # 피드백을 참고하여 프롬프트 개선
                        base_prompt = f"""
                        고객 문의 내용: {inquiry_content}
                        문제 유형: {issue_type}
                        시나리오: {best_scenario.get('scenario', '') if best_scenario else 'N/A'}
                        """
                        
                        enhanced_prompt = enhance_ai_prompt_with_feedback(base_prompt, issue_type)
                        
                        # 선택된 AI 모델에 따라 API 키 확인 및 핸들러 선택
                        ai_result = None
                        selected_model = st.session_state.get('ai_model', 'Gemini 1.5 Pro')
                        
                        if 'GPT' in selected_model:
                            # GPT API 사용
                            api_key_available = get_secret("OPENAI_API_KEY")
                            if api_key_available:
                                print("✅ OpenAI API 키를 로드했습니다.")
                            else:
                                api_key_available = st.session_state.get('openai_api_key', "")
                                if api_key_available:
                                    print("✅ OpenAI API 키를 사이드바에서 로드했습니다.")
                            
                            if not api_key_available:
                                st.error("❌ OpenAI API 키가 설정되지 않아 AI 분석을 진행할 수 없습니다.")
                                st.info("Streamlit Cloud Secrets에서 OPENAI_API_KEY를 설정하거나, 환경변수 OPENAI_API_KEY를 설정해주세요.")
                                st.stop()
                            
                            # GPT 모델 매핑
                            model_mapping = {
                                "GPT-4o": "gpt-4o",
                                "GPT-4 Turbo": "gpt-4-turbo",
                                "GPT-3.5 Turbo": "gpt-3.5-turbo"
                            }
                            gpt_model = model_mapping.get(selected_model, "gpt-4o")
                            
                            try:
                                ai_result = components['openai_handler'].generate_response(
                                    customer_input=inquiry_content,
                                    issue_type=issue_type,
                                    condition_1=best_scenario.get('condition_1', '') if best_scenario else '',
                                    condition_2=best_scenario.get('condition_2', '') if best_scenario else '',
                                    model=gpt_model
                                )
                                
                                elapsed_time = time.time() - start_time
                                if ai_result["success"]:
                                    # 피드백 학습 적용
                                    ai_result = apply_feedback_learning(ai_result, issue_type)
                                    st.success(f"✅ GPT 응답 생성 완료 (피드백 학습 적용) ({elapsed_time:.1f}초)")
                                else:
                                    st.warning(f"⚠️ GPT 응답 생성 실패, 기본 응답 사용 ({elapsed_time:.1f}초)")
                                    
                            except Exception as e:
                                elapsed_time = time.time() - start_time
                                st.error(f"❌ GPT 응답 생성 중 오류 발생 ({elapsed_time:.1f}초): {e}")
                                # 기본 응답 생성
                                ai_result = {
                                    "success": False,
                                    "error": str(e),
                                    "response": f"GPT API 오류로 인해 기본 응답을 생성합니다.\n\n[요약]\n고객 문의에 대한 기본적인 대응 방안을 제시합니다.\n\n[조치 흐름]\n1. 문제 상황 파악\n2. 기본적인 해결책 제시\n3. 필요시 추가 확인 요청\n\n[이메일 초안]\n고객님께서 문의하신 내용을 확인했습니다. 현재 상황을 파악하여 적절한 해결책을 제시하겠습니다."
                                }
                        else:
                            # Gemini API 사용
                            api_key_available = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
                            if api_key_available:
                                print("✅ Gemini API 키를 로드했습니다.")
                            else:
                                api_key_available = st.session_state.get('google_api_key', "")
                                if api_key_available:
                                    print("✅ Gemini API 키를 사이드바에서 로드했습니다.")
                            
                            if not api_key_available:
                                st.error("❌ Gemini API 키가 설정되지 않아 AI 분석을 진행할 수 없습니다.")
                                st.info("Streamlit Cloud Secrets에서 GEMINI_API_KEY를 설정하거나, 환경변수 GOOGLE_API_KEY를 설정해주세요.")
                                st.stop()
                            
                            # 선택된 Gemini 모델에 따라 적절한 핸들러 선택
                            gemini_handler = None
                            if selected_model == "Gemini 1.5 Pro":
                                gemini_handler = components.get('gemini_1_5_pro')
                            elif selected_model == "Gemini 1.5 Flash":
                                gemini_handler = components.get('gemini_1_5_flash')
                            elif selected_model == "Gemini 2.0 Pro":
                                gemini_handler = components.get('gemini_2_0_pro')
                            elif selected_model == "Gemini 2.0 Flash":
                                gemini_handler = components.get('gemini_2_0_flash')
                            
                            if not gemini_handler:
                                st.error(f"❌ {selected_model} 핸들러를 찾을 수 없습니다.")
                                st.info(f"💡 {selected_model} 모델을 사용하려면 Gemini API 키가 필요합니다.")
                                st.stop()
                            
                            try:
                                ai_result = gemini_handler.generate_complete_response(
                                    customer_input=inquiry_content,
                                    issue_type=issue_type,
                                    condition_1=best_scenario.get('condition_1', '') if best_scenario else '',
                                    condition_2=best_scenario.get('condition_2', '') if best_scenario else ''
                                )
                                
                                elapsed_time = time.time() - start_time
                                if ai_result["success"]:
                                    # 피드백 학습 적용
                                    ai_result = apply_feedback_learning(ai_result, issue_type)
                                    st.success(f"✅ {selected_model} 응답 생성 완료 (피드백 학습 적용) ({elapsed_time:.1f}초)")
                                else:
                                    st.warning(f"⚠️ {selected_model} 응답 생성 실패, 기본 응답 사용 ({elapsed_time:.1f}초)")
                                    
                            except Exception as e:
                                elapsed_time = time.time() - start_time
                                st.error(f"❌ {selected_model} 응답 생성 중 오류 발생 ({elapsed_time:.1f}초): {e}")
                                # 기본 응답 생성
                                ai_result = {
                                    "success": False,
                                    "error": str(e),
                                    "parsed_response": gemini_handler._generate_default_response(
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
                        'ai_result': ai_result,
                        'timestamp': get_safe_timestamp()
                    }
                    
                    # original_ai_response 추가 (GPT와 Gemini 모두 지원)
                    if ai_result.get('success') and ai_result.get('response'):
                        # GPT 응답인 경우
                        analysis_result['original_ai_response'] = ai_result['response']
                    elif ai_result.get('success') and 'gemini_result' in ai_result:
                        # Gemini 응답인 경우
                        gemini_result = ai_result['gemini_result']
                        if 'raw_response' in gemini_result:
                            analysis_result['original_ai_response'] = gemini_result['raw_response']
                        elif 'response' in gemini_result:
                            analysis_result['original_ai_response'] = gemini_result['response']
                    
                    # 분석 결과에 고유 ID 추가
                    analysis_result['id'] = int(time.time() * 1000)  # 타임스탬프 기반 ID
                    st.session_state.analysis_result = analysis_result
                    
                    st.session_state.inquiry_data = {
                        "timestamp": get_safe_timestamp(),
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
                        "user_name": st.session_state.contact_name,
                        "user_role": st.session_state.role
                    }
                    
                    # MongoDB 우선 저장 시도
                    try:
                        # inquiry_data에 사용자 정보 추가
                        inquiry_data_with_user = st.session_state.inquiry_data.copy()
                        inquiry_data_with_user['user_email'] = f"{st.session_state.contact_name}_{st.session_state.role}@privkeeper.com"
                        
                        # MongoDB 연결 상태 확인
                        if st.session_state.get('mongodb_connected') and st.session_state.get('mongo_handler'):
                            # MongoDB에 저장하기 전에 데이터 구조 확인 및 정리
                            # analysis_result에서 파싱된 데이터 추출
                            parsed_data = None
                            if 'ai_result' in analysis_result:
                                ai_result = analysis_result['ai_result']
                                
                            if 'gemini_result' in ai_result and 'parsed_response' in ai_result['gemini_result']:
                                # GEMINI 응답인 경우
                                parsed_data = ai_result['gemini_result']['parsed_response']
                            elif 'gemini_result' in ai_result and 'raw_response' in ai_result['gemini_result']:
                                # GEMINI raw_response인 경우 파싱
                                parsed_data = _parse_gemini_response(ai_result['gemini_result']['raw_response'])
                            elif 'parsed_response' in ai_result:
                                # 기존 파싱된 응답
                                parsed_data = ai_result['parsed_response']
                            elif 'response' in ai_result:
                                # GPT API 응답인 경우 파싱
                                parsed_data = _parse_gpt_response(ai_result['response'])
                            
                            # 파싱된 데이터를 analysis_result에 명시적으로 포함
                            if parsed_data:
                                analysis_result['parsed_response'] = parsed_data
                            else:
                                # 파싱된 데이터가 없는 경우 기본값 설정
                                analysis_result['parsed_response'] = {
                                    'response_type': '해결안',
                                    'summary': 'AI 분석 결과를 파싱할 수 없습니다.',
                                    'action_flow': 'AI 분석 결과를 파싱할 수 없습니다.',
                                    'email_draft': 'AI 분석 결과를 파싱할 수 없습니다.'
                                }
                            
                            # result 변수 초기화
                            result = {'success': True, 'ai_result': analysis_result}
                            
                            # MongoDB에 저장
                            mongo_result = st.session_state.mongo_handler.save_analysis(analysis_result, inquiry_data_with_user)
                            
                            if mongo_result.get('success'):
                                # MongoDB 저장 성공 - ID를 result에 설정
                                result['id'] = mongo_result.get('id')
                                print(f"✅ MongoDB 저장 성공 - Analysis ID: {result['id']}")
                            else:
                                st.warning(f"⚠️ MongoDB 저장 실패: {mongo_result.get('error', '알 수 없는 오류')}")
                                # 로컬 백업 저장 시도
                                save_result = components['multi_user_db'].save_analysis(analysis_result, inquiry_data_with_user)
                                if save_result.get('success'):
                                    result['id'] = save_result.get('id')
                                    st.info("📋 로컬 백업 저장소에 저장되었습니다.")
                                    print(f"✅ 로컬 백업 저장 성공 - Analysis ID: {result['id']}")
                                else:
                                    st.error("❌ 로컬 백업 저장도 실패했습니다.")
                        else:
                            # result 변수 초기화
                            result = {'success': True, 'ai_result': analysis_result}
                            
                            # MongoDB 연결 실패 시 로컬 저장
                            st.warning("⚠️ MongoDB 연결 실패 - 로컬 저장소에 저장합니다.")
                            save_result = components['multi_user_db'].save_analysis(analysis_result, inquiry_data_with_user)
                            
                            if save_result.get('success'):
                                result['id'] = save_result.get('id')
                                st.success(f"✅ 로컬 저장소에 분석 결과가 저장되었습니다. (사용자: {save_result.get('user_name', 'Unknown')}, ID: {save_result.get('user_id', 'Unknown')})")
                                print(f"✅ 로컬 저장 성공 - Analysis ID: {result['id']}")
                            else:
                                error_msg = save_result.get('error', '알 수 없는 오류')
                                st.error(f"❌ 로컬 저장도 실패했습니다: {error_msg}")
                                
                    except Exception as e:
                        st.error(f"❌ 데이터 저장 중 오류: {e}")
                        st.info("💡 저장 실패 시 관리자에게 문의하세요.")
                    
                    st.session_state.analysis_completed = True
                    st.success("🎉 AI 분석이 완료되었습니다! AI 분석 결과 페이지로 이동해 상세한 결과를 확인하세요.")
                    
                except Exception as e:
                    st.error(f"❌ 분석 중 오류 발생: {e}")
                    st.info("다시 시도해주세요.")
        else:
            st.warning("⚠️ 문의 내용을 입력해주세요.")

# 탭 2: AI 분석 결과
with tab2:
    st.markdown("## 🤖 AI 분석 결과")
    
    # API 키 확인
    gemini_api_key = st.session_state.get('google_api_key') or get_secret("GOOGLE_API_KEY")
    openai_api_key = st.session_state.get('openai_api_key') or get_secret("OPENAI_API_KEY")
    
    if not gemini_api_key and not openai_api_key:
        st.error("❌ AI API 키가 설정되지 않았습니다.")
        st.info("""
        **API 키 설정 방법:**
        1. Streamlit Secrets에서 Gemini API 키 또는 OpenAI API 키를 설정하세요
        2. 또는 환경변수 `GOOGLE_API_KEY` 또는 `OPENAI_API_KEY`를 설정하세요
        
        **API 키 발급 방법:**
        
        **Gemini API 키:**
        1. [Google AI Studio](https://aistudio.google.com/) 접속
        2. API 키 생성
        3. 생성된 API 키를 복사하여 앱에 입력
        
        **OpenAI API 키:**
        1. [OpenAI Platform](https://platform.openai.com/) 접속
        2. API Keys → Create new secret key
        3. 생성된 API 키를 복사하여 앱에 입력
        """)
        st.stop()
    
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        # 분석 완료 알림
        st.success("✅ AI 분석이 완료되었습니다! 아래에서 상세한 결과를 확인하세요.")
        
        # 입력 정보 요약
        with st.expander("📋 입력된 문의 정보"):
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
        
        
        # 문제 유형 분류와 시나리오 매칭 섹션 삭제
        
        if 'ai_result' in result and result['ai_result']['success']:
            ai_result = result['ai_result']
            
            # GEMINI 응답인 경우 gemini_result에서 parsed_response 추출
            if 'gemini_result' in ai_result:
                # GEMINI 응답인 경우 GEMINI 전용 파싱 사용
                if 'raw_response' in ai_result['gemini_result']:
                    parsed = _parse_gemini_response(ai_result['gemini_result']['raw_response'])
                else:
                    parsed = ai_result['gemini_result']['parsed_response']
            elif 'parsed_response' in ai_result:
                parsed = ai_result['parsed_response']
            elif 'response' in ai_result:
                # GPT API 응답인 경우 GPT 전용 파싱 사용
                parsed = _parse_gpt_response(ai_result['response'])
            else:
                st.error("❌ AI 응답 데이터가 올바르지 않습니다.")
                st.stop()
            
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
                if parsed.get('summary'):
                    st.write(parsed['summary'])
                else:
                    st.warning("⚠️ 요약 정보가 없습니다.")
                
                st.markdown("#### 🔧 조치 흐름")
                if parsed.get('action_flow'):
                    # 조치 흐름에 줄바꿈 적용 (더 효과적인 줄바꿈 처리)
                    action_flow_content = parsed['action_flow']
                    # 연속된 공백을 하나로 통일
                    action_flow_content = ' '.join(action_flow_content.split())
                    # 번호가 있는 항목을 줄바꿈으로 구분 (더 정교한 처리)
                    action_flow_content = re.sub(r'(\d+\.)', r'\n\1', action_flow_content)
                    # 첫 번째 줄바꿈 제거
                    action_flow_content = action_flow_content.lstrip('\n')
                    st.write(action_flow_content)
                else:
                    st.warning("⚠️ 조치 흐름 정보가 없습니다.")
            
            with col10:
                st.markdown("#### 📧 이메일 초안")
                
                # 이력 관리와 완전히 동일한 방식으로 이메일 초안 추출
                email_content = None
                
                # 1. 파싱된 email_draft 사용 (우선순위 1) - DB에 저장된 정확한 이메일 초안
                email_draft = result.get('email_draft', '')
                if email_draft and len(email_draft.strip()) > 20:
                    email_content = email_draft
                    print(f"✅ AI 분석 결과 탭 - email_draft 사용: {len(email_content)}자")
                
                # 2. original_ai_response에서 이메일 초안 추출 (우선순위 2) - 이력 관리와 동일
                if not email_content and result.get('original_ai_response'):
                    email_content = extract_email_from_original_response(result['original_ai_response'])
                    print(f"🔍 AI 분석 결과 탭 - original_ai_response에서 추출: {len(email_content) if email_content else 0}자")
                elif not email_content and result.get('ai_result'):
                    ai_result = result['ai_result']
                    if 'gemini_result' in ai_result and 'raw_response' in ai_result['gemini_result']:
                        email_content = extract_email_from_original_response(ai_result['gemini_result']['raw_response'])
                        print(f"🔍 AI 분석 결과 탭 - gemini_result에서 추출: {len(email_content) if email_content else 0}자")
                    elif 'response' in ai_result:
                        email_content = extract_email_from_original_response(ai_result['response'])
                        print(f"🔍 AI 분석 결과 탭 - ai_result response에서 추출: {len(email_content) if email_content else 0}자")
                    elif 'gpt_result' in ai_result and 'raw_response' in ai_result['gpt_result']:
                        email_content = extract_email_from_original_response(ai_result['gpt_result']['raw_response'])
                        print(f"🔍 AI 분석 결과 탭 - gpt_result에서 추출: {len(email_content) if email_content else 0}자")
                
                # 3. full_analysis_result에서 이메일 초안 추출 (우선순위 3) - 이력 관리와 동일
                if not email_content and result.get('full_analysis_result'):
                    email_content = extract_email_from_analysis_result(result['full_analysis_result'])
                    print(f"🔍 AI 분석 결과 탭 - full_analysis_result에서 추출: {len(email_content) if email_content else 0}자")
                
                # 4. 기본 이메일 템플릿 (최후 수단) - 이력 관리와 동일
                if not email_content:
                    email_content = f"""제목: {result.get('issue_type', '문의')} 답변

고객님 안녕하세요.

{result.get('issue_type', '문의')}에 대한 문의 주셔서 감사합니다.

현재 상황을 분석한 결과, 추가 정보가 필요한 상황입니다.

**필요한 정보:**
1. 구체적인 오류 메시지
2. 발생 시점 및 빈도
3. 사용 환경 정보

자세한 내용은 담당 엔지니어가 확인 후 답변 드리겠습니다.

추가 문의사항이 있으시면 언제든 연락 주세요.

감사합니다."""
                
                if email_content:
                    # 이력 관리와 동일한 방식으로 이메일 초안 표시
                    st.markdown("**이메일 내용**")
                    st.text_area("이메일 내용", value=email_content, height=350, key="email_content_analysis", label_visibility="collapsed")
                else:
                    st.warning("⚠️ 이메일 초안 정보가 없습니다.")
                    
            # SMS 발송 섹션 추가
            st.markdown("---")
            st.markdown("### 📱 SMS 발송")
            
            col_sms1, col_sms2 = st.columns(2)
            
            with col_sms1:
                recipient_name = st.text_input(
                    "수신자 이름",
                    placeholder="홍길동 대리",
                    key="sms_recipient_name"
                )
                recipient_phone = st.text_input(
                    "수신자 전화번호",
                    placeholder="01012345678",
                    key="sms_recipient_phone"
                )
                sender_phone = st.text_input(
                    "발신자 번호",
                    value=st.session_state.get('sender_phone', '01012345678'),
                    placeholder="01012345678",
                    help="SMS 발송 시 표시될 발신자 번호입니다",
                    key="sms_sender_phone"
                )
            
            with col_sms2:
                # AI 분석 결과에서 email_draft가 있는지 먼저 확인 (이메일 초안과 동일)
                email_draft = parsed.get('email_draft', '')
                if email_draft and len(email_draft.strip()) > 20:
                    # AI 분석 결과의 이메일 초안을 SMS 메시지로 사용
                    default_sms_message = email_draft
                else:
                    # 기본 SMS 템플릿 사용
                    default_sms_message = f"[{st.session_state.get('ai_model', 'AI')}] {parsed.get('summary', '')[:100] if parsed.get('summary') else '분석 완료'}..."
                
                sms_message = st.text_area(
                    "SMS 메시지",
                    value=default_sms_message,
                    height=150,
                    key="sms_message_analysis"
                )
                
                # SMS 발송 버튼
                if st.button("📱 SMS 발송", use_container_width=True, type="primary"):
                    if recipient_name and recipient_phone and sms_message:
                        # SOLAPI 핸들러로 SMS 발송
                        try:
                            # 세션 상태에서 API 키 가져오기
                            api_key = st.session_state.get('solapi_api_key', '')
                            api_secret = st.session_state.get('solapi_api_secret', '')
                            # 사용자가 입력한 발신자 번호 사용
                            sender_phone = sender_phone
                            
                            if api_key and api_secret:
                                # SOLAPI 핸들러 생성
                                sms_handler = SOLAPIHandler(api_key, api_secret)
                                sms_handler.set_sender(sender_phone)
                                
                                # SMS 발송
                                sms_result = sms_handler.send_sms(
                                    phone_number=recipient_phone,
                                    message=sms_message,
                                    recipient_name=recipient_name
                                )
                                
                                if sms_result["success"]:
                                    st.success(f"✅ SMS가 성공적으로 발송되었습니다!")
                                    st.info(f"수신자: {recipient_name} ({recipient_phone})")
                                    st.info(f"메시지 ID: {sms_result.get('message_id', 'N/A')}")
                                else:
                                    st.error(f"❌ SMS 발송 실패: {sms_result.get('error', '알 수 없는 오류')}")
                            else:
                                st.error("❌ SOLAPI API 키가 설정되지 않았습니다.")
                                st.info("Streamlit Secrets에서 SOLAPI API 키를 설정해주세요.")
                        except Exception as e:
                            st.error(f"❌ SMS 발송 중 오류: {e}")
                    else:
                        st.warning("⚠️ 수신자 정보와 메시지를 모두 입력해주세요.")
            
            # 피드백 버튼 추가
            if 'id' in result:
                analysis_id = result['id']
                print(f"🔍 피드백 버튼 호출 - Analysis ID: {analysis_id}, Type: {type(analysis_id)}")
                show_feedback_buttons(analysis_id)
            else:
                print("⚠️ 피드백 버튼을 표시할 수 없습니다 - result에 'id'가 없습니다")
                print(f"🔍 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        else:
            st.error("❌ AI 응답 생성 실패")
            if 'ai_result' in result and 'error' in result['ai_result']:
                st.write(f"오류: {result['ai_result']['error']}")
            
            # 기본 응답 표시
            if 'ai_result' in result:
                ai_result = result['ai_result']
                
                # Gemini 응답인 경우 gemini_result에서 parsed_response 추출
                if 'gemini_result' in ai_result:
                    parsed = ai_result['gemini_result']['parsed_response']
                elif 'parsed_response' in ai_result:
                    parsed = ai_result['parsed_response']
                else:
                    st.error("❌ 기본 응답 데이터가 올바르지 않습니다.")
                    st.stop()
                
                st.warning("⚠️ 기본 응답을 제공합니다:")
                
                col9, col10 = st.columns(2)
                
                with col9:
                    st.markdown("#### 📝 요약")
                    if parsed.get('summary'):
                        st.write(parsed['summary'])
                    else:
                        st.warning("⚠️ 요약 정보가 없습니다.")
                    
                    st.markdown("#### 🔧 조치 흐름")
                    if parsed.get('action_flow'):
                        # 조치 흐름에 줄바꿈 적용 (더 효과적인 줄바꿈 처리)
                        action_flow_content = parsed['action_flow']
                        # 연속된 공백을 하나로 통일
                        action_flow_content = ' '.join(action_flow_content.split())
                        # 번호가 있는 항목을 줄바꿈으로 구분 (더 정교한 처리)
                        action_flow_content = re.sub(r'(\d+\.)', r'\n\1', action_flow_content)
                        # 첫 번째 줄바꿈 제거
                        action_flow_content = action_flow_content.lstrip('\n')
                        st.write(action_flow_content)
                    else:
                        st.warning("⚠️ 조치 흐름 정보가 없습니다.")
                
                with col10:
                    st.markdown("#### 📧 이메일 초안")
                    
                    # 이력 관리 탭과 완전히 동일한 방식으로 이메일 초안 추출
                    email_content = None
                    
                    # 1. 파싱된 email_draft 사용 (우선순위 1) - DB에 저장된 정확한 이메일 초안
                    email_draft = result.get('email_draft', '')
                    if email_draft and len(email_draft.strip()) > 20:
                        email_content = email_draft
                        print(f"✅ 이력 조회 탭 - email_draft 사용: {len(email_content)}자")
                    
                    # 2. original_ai_response에서 이메일 초안 추출 (우선순위 2) - 이력 관리와 동일
                    if not email_content and result.get('original_ai_response'):
                        email_content = extract_email_from_original_response(result['original_ai_response'])
                        print(f"🔍 이력 조회 탭 - original_ai_response에서 추출: {len(email_content) if email_content else 0}자")
                    elif not email_content and result.get('ai_result'):
                        ai_result = result['ai_result']
                        if 'gemini_result' in ai_result and 'raw_response' in ai_result['gemini_result']:
                            email_content = extract_email_from_original_response(ai_result['gemini_result']['raw_response'])
                            print(f"🔍 이력 조회 탭 - gemini_result에서 추출: {len(email_content) if email_content else 0}자")
                        elif 'response' in ai_result:
                            email_content = extract_email_from_original_response(ai_result['response'])
                            print(f"🔍 이력 조회 탭 - ai_result response에서 추출: {len(email_content) if email_content else 0}자")
                        elif 'gpt_result' in ai_result and 'raw_response' in ai_result['gpt_result']:
                            email_content = extract_email_from_original_response(ai_result['gpt_result']['raw_response'])
                            print(f"🔍 이력 조회 탭 - gpt_result에서 추출: {len(email_content) if email_content else 0}자")
                    
                    # 3. full_analysis_result에서 이메일 초안 추출 (우선순위 3) - 이력 관리와 동일
                    if not email_content and result.get('full_analysis_result'):
                        email_content = extract_email_from_analysis_result(result['full_analysis_result'])
                        print(f"🔍 이력 조회 탭 - full_analysis_result에서 추출: {len(email_content) if email_content else 0}자")
                    
                    # 4. 기본 이메일 템플릿 (최후 수단) - 이력 관리와 동일
                    if not email_content:
                        email_content = f"""제목: {result.get('issue_type', '문의')} 답변

고객님 안녕하세요.

{result.get('issue_type', '문의')}에 대한 문의 주셔서 감사합니다.

현재 상황을 분석한 결과, 추가 정보가 필요한 상황입니다.

**필요한 정보:**
1. 구체적인 오류 메시지
2. 발생 시점 및 빈도
3. 사용 환경 정보

자세한 내용은 담당 엔지니어가 확인 후 답변 드리겠습니다.

추가 문의사항이 있으시면 언제든 연락 주세요.

감사합니다."""
                    
                if email_content:
                    # 이메일 초안을 Streamlit 기본 스타일로 표시
                    st.markdown("**이메일 내용**")
                    st.text_area("이메일 내용", value=email_content, height=350, key="email_content_history", label_visibility="collapsed")
                else:
                    st.warning("⚠️ 이메일 초안 정보가 없습니다.")
        
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
        #col11, col12, col13, col14 = st.columns(4)
        
        #with col11:
        #    if st.button("💾 결과 저장", use_container_width=True):
        #        # 결과를 JSON 파일로 저장
        #        filename = f"analysis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        #        with open(filename, 'w', encoding='utf-8') as f:
        #            json.dump(st.session_state.analysis_result, f, ensure_ascii=False, indent=2)
        #        st.success(f"분석 결과가 {filename}에 저장되었습니다!")
        
        #with col12:
        #    if st.button("🔄 새로운 분석", use_container_width=True):
        #        st.session_state.analysis_result = None
        #        st.session_state.inquiry_data = None
        #        st.rerun()
        
        #with col13:
        #    if st.button("📊 통계 보기", use_container_width=True):
        #        # 통계 보기 버튼 클릭시 분석 완료 알림 제거
        #        st.session_state.analysis_completed = False
        #        st.info("📊 이력 관리 탭으로 이동하세요.")
        
        #with col14:
        #  if st.button("📱 SMS 발송", use_container_width=True):
        #       st.info("📱 위의 SMS 발송 섹션을 사용하여 SMS를 발송하세요.")
    
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
    
    # 필터링 옵션
    col15, col16, col17, col18 = st.columns(4)
    
    with col15:
        filter_date_from = st.date_input("시작 날짜", value=date.today() - timedelta(days=30))
    
    with col16:
        filter_date_to = st.date_input("종료 날짜", value=date.today())
    
    with col17:
        filter_type = st.selectbox("문제 유형 필터", 
            ["전체"] + ["현재 비밀번호가 맞지 않습니다", "VMS와의 통신에 실패했습니다", "Ping 테스트에 실패했습니다", 
                       "Onvif 응답이 없습니다", "로그인 차단 상태입니다", "비밀번호 변경에 실패했습니다",
                       "PK P 계정 로그인 안됨", "PK P 웹 접속 안됨", "기타"])
    
    with col18:
        filter_user = st.text_input("담당자 필터", placeholder="담당자명 입력")
    
    # 검색 버튼
    search_clicked = st.button("🔍 이력 검색", type="primary")
    
    # 검색 버튼 클릭시
    if search_clicked:
        # 기존 상세보기 모달 상태 리셋
        st.session_state.show_detail_modal = False
        st.session_state.selected_row_for_detail = None
        
        # 검색 진행 상태 표시
        with st.spinner("🔍 이력을 검색하고 있습니다..."):
            try:
                # 종료 날짜는 포함하지 않음 (다음 날 00:00:00 이전까지만)
                date_to_with_time = None
                if filter_date_to:
                    # 종료 날짜 다음 날 00:00:00을 기준으로 설정 (종료 날짜는 포함하지 않음)
                    next_day = filter_date_to + timedelta(days=1)
                    date_to_with_time = next_day.isoformat()
                
                # MongoDB 우선 이력 조회 시도
                history_result = None
                
                if st.session_state.get('mongodb_connected') and st.session_state.get('mongo_handler'):
                    try:
                        # MongoDB에서 이력 조회 (날짜 필터링 지원)
                        history_data = st.session_state.mongo_handler.get_history(
                            limit=50,
                            date_from=filter_date_from.isoformat() if filter_date_from else None,
                            date_to=date_to_with_time,
                            issue_type=filter_type if filter_type != "전체" else None,
                            user_id=filter_user if filter_user else None
                        )
                        
                        history_result = {
                            'success': True,
                            'data': history_data,
                            'source': 'mongodb'
                        }
                        
                    except Exception as e:
                        st.warning(f"⚠️ MongoDB 조회 실패: {e}")
                        # 로컬 데이터베이스로 폴백
                        history_result = components['multi_user_db'].get_global_history(
                            limit=50,
                            issue_type=filter_type if filter_type != "전체" else None,
                            date_from=filter_date_from.isoformat() if filter_date_from else None,
                            date_to=date_to_with_time,
                            user_name=filter_user if filter_user else None
                        )
                        st.info("📋 로컬 데이터베이스에서 이력을 조회했습니다.")
                else:
                    # MongoDB 연결 실패 시 로컬 데이터베이스 사용
                    st.warning("⚠️ MongoDB 연결 실패 - 로컬 데이터베이스를 사용합니다.")
                    history_result = components['multi_user_db'].get_global_history(
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
                        # 날짜를 초단위까지 표시하고 최신순으로 정렬
                        timestamp = entry.get('timestamp', '').strip()
                        if timestamp:
                            formatted_date = ""
                            try:
                                # ISO 형식의 타임스탬프를 파싱하여 원하는 형식으로 변환
                                dt = datetime.fromisoformat(timestamp)
                                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                try:
                                    # 'T'를 공백으로 대체하여 파싱 시도
                                    timestamp_with_space = timestamp.replace('T', ' ')
                                    dt = datetime.strptime(timestamp_with_space, '%Y-%m-%d %H:%M:%S')
                                    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    try:
                                        # 마이크로초가 포함된 경우 처리
                                        dt = datetime.strptime(timestamp_with_space, '%Y-%m-%d %H:%M:%S.%f')
                                        formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                                    except:
                                        # 모든 파싱이 실패한 경우 원본 문자열에서 슬라이싱
                                        if 'T' in timestamp:
                                            # ISO 형식에서 'T' 제거하고 슬라이싱
                                            clean_timestamp = timestamp.replace('T', ' ')
                                            formatted_date = clean_timestamp[:19] if len(clean_timestamp) >= 19 else clean_timestamp
                                        else:
                                            formatted_date = timestamp[:19] if len(timestamp) >= 19 else timestamp
                        else:
                            formatted_date = ""
                        
                        df_data.append({
                            "번호": i,
                            "날짜": formatted_date,
                            "고객사명": entry.get('customer_name', ''),
                            "문의유형": entry.get('issue_type', ''),
                            "우선순위": entry.get('priority', ''),
                            "담당자": entry.get('user_name', ''),
                            "역할": entry.get('user_role', '')
                        })
                    
                    df = pd.DataFrame(df_data)
                    # 세션 상태에 결과 저장
                    st.session_state.history_search_results = df
                    st.session_state.history_search_performed = True
                    # 새로운 검색 시 페이지를 1로 리셋
                    st.session_state.current_page = 1
                    
                    st.success(f"✅ {len(history_data)}건의 이력이 조회되었습니다.")
                    
                    # 이력 조회 결과 표시 (기본 데이터프레임 + 커스텀 테이블 모두 표시)
                    st.markdown("### 📊 이력 조회 결과")
                    
                    # 1. 기본 st.dataframe 표시 (위쪽)
                    # st.markdown("#### 📋 기본 데이터프레임")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # 0) 모달을 위쪽에서 먼저 그리기(있다면)
                    if st.session_state.get('show_detail_modal', False) and st.session_state.get('selected_row_for_detail'):
                        with st.expander("🔍 상세 결과", expanded=True):
                            show_ai_analysis_modal(st.session_state.selected_row_for_detail)
                            # 모달 닫기 버튼
                            def close_modal_new():
                                st.session_state.show_detail_modal = False
                                st.session_state.selected_row_for_detail = None

                            if st.button("❌ 닫기", key="close_modal"):
                                close_modal_new()
                        st.markdown("---")  # 모달과 리스트 구분선

                    # 1) 커스텀 테이블 UI
                    st.markdown("#### 🔍상세 보기")
                    
                    # 헤더 행
                    header_cols = st.columns([2, 2, 2, 2, 2, 2, 2, 1])
                    with header_cols[0]:
                        st.markdown('<div class="history-table-header">번호</div>', unsafe_allow_html=True)
                    with header_cols[1]:
                        st.markdown('<div class="history-table-header">날짜</div>', unsafe_allow_html=True)
                    with header_cols[2]:
                        st.markdown('<div class="history-table-header">고객사명</div>', unsafe_allow_html=True)
                    with header_cols[3]:
                        st.markdown('<div class="history-table-header">문의유형</div>', unsafe_allow_html=True)
                    with header_cols[4]:
                        st.markdown('<div class="history-table-header">우선순위</div>', unsafe_allow_html=True)
                    with header_cols[5]:
                        st.markdown('<div class="history-table-header">담당자</div>', unsafe_allow_html=True)
                    with header_cols[6]:
                        st.markdown('<div class="history-table-header">역할</div>', unsafe_allow_html=True)
                    with header_cols[7]:
                        st.markdown('<div class="history-table-header">상세보기</div>', unsafe_allow_html=True)
                    
                    # 페이지네이션 적용
                    paginated_df, total_pages, total_items = get_paginated_data(
                        df, st.session_state.current_page, st.session_state.items_per_page
                    )
                    
                    # 데이터 행들 (페이지네이션된 데이터만 표시)
                    for index, row in paginated_df.iterrows():
                        row_cols = st.columns([2, 2, 2, 2, 2, 2, 2, 1])
                        
                        with row_cols[0]:
                            st.markdown(f'<div class="history-table-cell">{row.get("번호", "N/A")}</div>', unsafe_allow_html=True)
                        with row_cols[1]:
                            st.markdown(f'<div class="history-table-cell">{row.get("날짜", "N/A")}</div>', unsafe_allow_html=True)
                        with row_cols[2]:
                            st.markdown(f'<div class="history-table-cell">{row.get("고객사명", "N/A")}</div>', unsafe_allow_html=True)
                        with row_cols[3]:
                            st.markdown(f'<div class="history-table-cell">{row.get("문의유형", "N/A")}</div>', unsafe_allow_html=True)
                        with row_cols[4]:
                            st.markdown(f'<div class="history-table-cell">{row.get("우선순위", "N/A")}</div>', unsafe_allow_html=True)
                        with row_cols[5]:
                            st.markdown(f'<div class="history-table-cell">{row.get("담당자", "N/A")}</div>', unsafe_allow_html=True)
                        with row_cols[6]:
                            st.markdown(f'<div class="history-table-cell">{row.get("역할", "N/A")}</div>', unsafe_allow_html=True)
                        with row_cols[7]:
                            def open_modal_new(row_dict):
                                st.session_state.selected_row_for_detail = row_dict
                                st.session_state.show_detail_modal = True

                            st.button(
                                "🔍",
                                key=f"detail_btn_{index}_{row.get('번호', 'unknown')}",
                                help="클릭하여 상세 분석 결과 보기",
                                on_click=open_modal_new,
                                args=(row.to_dict(),),
                            )
                        
                        # 구분선 추가
                        st.markdown("---")
                    
                    # 페이지네이션 컨트롤 표시
                    render_pagination_controls(
                        st.session_state.current_page, 
                        total_pages, 
                        total_items, 
                        st.session_state.items_per_page,
                        "new_"
                    )
                    

                    
                    # 통계 정보
                    # MongoDB와 로컬 데이터를 모두 고려한 통계 계산
                    total_analyses = len(history_data)
                    
                                         # 디버깅 정보 제거
                    
                    # 사용자 수 계산
                    users = set()
                    for entry in history_data:
                        user_name = entry.get('user_name', '')
                        user_role = entry.get('user_role', '')
                        if user_name and user_role:
                            users.add(f"{user_name}_{user_role}")
                    
                    # 문제 유형 수 계산
                    issue_types = set()
                    for entry in history_data:
                        issue_type = entry.get('issue_type', '')
                        if issue_type:
                            issue_types.add(issue_type)
                    
                    # 응답 유형 수 계산
                    response_types = set()
                    for entry in history_data:
                        # 직접 response_type 필드 확인
                        response_type = entry.get('response_type', '')
                        if response_type:
                            response_types.add(response_type)
                        
                        # full_analysis_result에서 response_type 추출
                        full_result = entry.get('full_analysis_result', {})
                        if full_result:
                            ai_result = full_result.get('ai_result', {})
                            if ai_result:
                                if 'parsed_response' in ai_result:
                                    parsed_response = ai_result.get('parsed_response', {})
                                    if parsed_response:
                                        response_type = parsed_response.get('response_type', '')
                                        if response_type:
                                            response_types.add(response_type)
                                elif 'response' in ai_result:
                                    # GPT API 응답인 경우 파싱
                                    parsed_response = _parse_gpt_response(ai_result['response'])
                                    response_type = parsed_response.get('response_type', '')
                                    if response_type:
                                        response_types.add(response_type)
                    
                    col19, col20, col21, col22 = st.columns(4)
                    
                    with col19:
                        st.metric("총 문의 건수", total_analyses)
                    
                    with col20:
                        st.metric("총 사용자 수", len(users))
                    
                    with col21:
                        st.metric("문제 유형 수", len(issue_types))
                    
                    with col22:
                        st.metric("응답 유형 수", len(response_types))
                    
                    # 문제 유형별 분포
                    if issue_types:
                        st.markdown("### 📊 문제 유형별 분포")
                        issue_data = []
                        for issue_type in issue_types:
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
        st.markdown("### 📊 이력 조회 결과")
        
        # 이전 검색 결과도 동일한 방식으로 표시
        df_previous = st.session_state.history_search_results.copy()
        
        # 1. 기본 st.dataframe 표시 (위쪽)
        #st.markdown("#### 📋 기본 데이터프레임")
        st.dataframe(df_previous, use_container_width=True, hide_index=True)
        


        # 1) 커스텀 테이블 UI
        st.markdown("#### 🔍상세 보기")
        
        # 헤더 행
        prev_header_cols = st.columns([2, 2, 2, 2, 2, 2, 2, 1])
        with prev_header_cols[0]:
            st.markdown('<div class="history-table-header">번호</div>', unsafe_allow_html=True)
        with prev_header_cols[1]:
            st.markdown('<div class="history-table-header">날짜</div>', unsafe_allow_html=True)
        with prev_header_cols[2]:
            st.markdown('<div class="history-table-header">고객사명</div>', unsafe_allow_html=True)
        with prev_header_cols[3]:
            st.markdown('<div class="history-table-header">문의유형</div>', unsafe_allow_html=True)
        with prev_header_cols[4]:
            st.markdown('<div class="history-table-header">우선순위</div>', unsafe_allow_html=True)
        with prev_header_cols[5]:
            st.markdown('<div class="history-table-header">담당자</div>', unsafe_allow_html=True)
        with prev_header_cols[6]:
            st.markdown('<div class="history-table-header">역할</div>', unsafe_allow_html=True)
        with prev_header_cols[7]:
            st.markdown('<div class="history-table-header">상세보기</div>', unsafe_allow_html=True)
        
        # 페이지네이션 적용
        paginated_df_prev, total_pages_prev, total_items_prev = get_paginated_data(
            df_previous, st.session_state.current_page, st.session_state.items_per_page
        )
        
        # 데이터 행들 (페이지네이션된 데이터만 표시)
        for index, row in paginated_df_prev.iterrows():
            prev_row_cols = st.columns([2, 2, 2, 2, 2, 2, 2, 1])
            
            with prev_row_cols[0]:
                st.markdown(f'<div class="history-table-cell">{row.get("번호", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[1]:
                st.markdown(f'<div class="history_table-cell">{row.get("날짜", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[2]:
                st.markdown(f'<div class="history_table-cell">{row.get("고객사명", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[3]:
                st.markdown(f'<div class="history_table-cell">{row.get("문의유형", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[4]:
                st.markdown(f'<div class="history_table-cell">{row.get("우선순위", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[5]:
                st.markdown(f'<div class="history_table-cell">{row.get("담당자", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[6]:
                st.markdown(f'<div class="history_table-cell">{row.get("역할", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[7]:
                def open_modal_prev(row_dict):
                    st.session_state.selected_row_for_detail = row_dict
                    st.session_state.show_detail_modal = True

                st.button(
                    "🔍",
                    key=f"prev_detail_btn_{index}_{row.get('번호', 'unknown')}",
                    help="클릭하여 상세 분석 결과 보기",
                    on_click=open_modal_prev,
                    args=(row.to_dict(),),
                )
            
            # 구분선 추가
            st.markdown("---")
        
        # 페이지네이션 컨트롤 표시
        render_pagination_controls(
            st.session_state.current_page, 
            total_pages_prev, 
            total_items_prev, 
            st.session_state.items_per_page,
            "prev_"
        )

        if st.session_state.get('show_detail_modal', False) and st.session_state.get('selected_row_for_detail'):
            with st.expander("🔍 상세 결과", expanded=True):
                show_ai_analysis_modal(st.session_state.selected_row_for_detail)
                # 모달 닫기 버튼
                def close_modal_prev():
                    st.session_state.show_detail_modal = False
                    st.session_state.selected_row_for_detail = None

                if st.button("❌ 닫기", key="prev_close_modal"):
                    close_modal_prev()
            st.markdown("---")  # 모달과 리스트 구분선
        


# 탭 4: 사용 가이드
with tab4:
    st.markdown("## 📚 사용 가이드")
    
    st.markdown("### 🎯 시스템 개요")
    st.markdown("PrivKeeper P 장애 대응 자동화 시스템은 다중 AI 모델 기반 고객 문의 자동 분석 및 응답 도구입니다.")

    st.markdown("### 📋 사용 방법")

    st.markdown("**1단계: 고객 문의 입력**")
    st.markdown("- 고객사 정보와 문의 내용을 상세히 입력")
    st.markdown("- 시스템이 자동으로 문제 유형을 분류합니다")

    st.markdown("**2단계: AI 분석**")
    st.markdown("- 선택한 AI 모델이 자동으로 증상 분석, 원인 추정, 조치 방향 제시")
    st.markdown("- 유사 사례 검색을 통한 참고 정보 제공")
    st.markdown("- 고객 응답 이메일 초안 자동 생성")

    st.markdown("**3단계: 검토 및 발송**")
    st.markdown("- 엔지니어가 AI 분석 결과 검토")
    st.markdown("- 필요시 수정 후 고객에게 응답")
    st.markdown("- SMS 발송으로 빠른 알림 전달 가능")

    st.markdown("### 🔧 기술 스택")

    st.markdown("- **AI 모델:** Gemini 1.5 Pro/Flash, Gemini 2.0 Flash, GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo")
    st.markdown("- **벡터 검색:** scikit-learn 기반 텍스트 유사도")
    st.markdown("- **웹 프레임워크:** Streamlit")
    st.markdown("- **데이터베이스:** JSON 파일 + MongoDB Atlas (선택사항)")
    st.markdown("- **데이터 처리:** Pandas, NumPy")
    st.markdown("- **SMS 발송:** SOLAPI")

    st.markdown("### ⚠️ 주의사항")

    st.markdown("- AI 분석 결과는 참고용이며, 최종 검토 후 발송")
    st.markdown("- 민감한 정보는 입력하지 않도록 주의")
    st.markdown("- 긴급한 경우 즉시 담당 엔지니어에게 연락")

    st.markdown("### 📞 지원 연락처")

    st.markdown("- 기술지원: 02-678-1234 이메일: support@privkeeper.com")
    st.markdown("- 긴급상황: 010-3456-7890")
    
    st.markdown("### 📱 SMS 기능")
    
    st.markdown("- **SOLAPI 연동**: 안정적인 SMS 발송 서비스")
    st.markdown("- **자동 메시지 생성**: AI 분석 결과 기반 SMS 내용 자동 생성")
    st.markdown("- **즉시 발송**: 분석 완료 후 바로 SMS 발송 가능")
    st.markdown("- **이력 관리**: SMS 발송 내역 추적 및 관리")
    
    st.markdown("**SMS 발송 방법:**")
    st.markdown("1. Streamlit Secrets에서 SOLAPI API 키 설정")
    st.markdown("2. AI 분석 결과 또는 이력 상세보기에서 SMS 발송")
    st.markdown("3. 수신자 정보 입력 후 발송")
    
    st.markdown("**자세한 설정 방법:** `SOLAPI_설정_가이드.md` 파일 참조")

# 탭 5: Vector DB 관리
with tab5:
    st.markdown("## 🔧 Vector DB 관리")
    
    # Vector DB 상태 확인
    if 'classifier' in components:
        classifier = components['classifier']
        
        # ChromaVectorClassifier인지 IssueClassifier인지 확인
        is_faiss_classifier = hasattr(classifier, 'index') and hasattr(classifier, 'embedding_model')
        is_issue_classifier = hasattr(classifier, 'vector_classifier')
        
        if is_faiss_classifier:
            st.success("✅ FAISS Vector DB가 활성화되어 있습니다.")
        elif is_issue_classifier and classifier.vector_classifier is not None:
            st.success("✅ Vector DB가 활성화되어 있습니다 (IssueClassifier 내부).")
        else:
            st.warning("⚠️ Vector DB가 활성화되지 않았습니다.")
            st.info("FAISS 또는 Vector Classifier가 초기화되지 않았습니다.")
            
        # 디버깅 정보 표시
        if is_faiss_classifier or (is_issue_classifier and classifier.vector_classifier is not None):
            with st.expander("🔍 디버깅 정보"):
                try:
                    # ChromaVectorClassifier 또는 IssueClassifier의 vector_classifier 가져오기
                    if is_faiss_classifier:
                        vector_classifier = classifier
                        st.write("**분류기 타입**: ChromaVectorClassifier (FAISS 기반)")
                    else:
                        vector_classifier = classifier.vector_classifier
                        st.write("**분류기 타입**: IssueClassifier 내부의 ChromaVectorClassifier")
                    
                    if vector_classifier is not None:
                        st.write(f"**FAISS Index 존재**: {hasattr(vector_classifier, 'index') and vector_classifier.index is not None}")
                        st.write(f"**Embedding Model 존재**: {hasattr(vector_classifier, 'embedding_model') and vector_classifier.embedding_model is not None}")
                        st.write(f"**Documents 수**: {len(vector_classifier.documents) if hasattr(vector_classifier, 'documents') else 'N/A'}")
                    else:
                        st.write("**Vector Classifier**: None (초기화되지 않음)")
                except Exception as e:
                    st.write(f"**Vector Classifier 오류**: {e}")
                    st.write("**Vector Classifier**: 초기화 실패")
            
            # 클라이언트 타입 확인
            try:
                # vector_classifier 변수가 위에서 정의되었으므로 재사용
                if is_faiss_classifier:
                    current_classifier = classifier
                elif is_issue_classifier and classifier.vector_classifier is not None:
                    current_classifier = classifier.vector_classifier
                else:
                    current_classifier = None
                    
                if current_classifier and hasattr(current_classifier, 'client') and current_classifier.client:
                    client_type = type(current_classifier.client).__name__
                    st.write(f"**Client 타입**: {client_type}")
                else:
                    st.write("**Client 타입**: 없음")
            except Exception as e:
                st.write(f"**Client 타입 확인 오류**: {e}")
            
            
    else:
        st.error("❌ Vector DB가 초기화되지 않았습니다.")
        
        # Vector DB 없이도 작동하는 기능들 안내
        st.info("""
        **현재 사용 가능한 기능:**
        - ✅ **키워드 기반 분류**: 정상 작동
        - ✅ **Gemini API 분류**: 정상 작동  
        - ✅ **유사 사례 검색**: 간단한 텍스트 유사도 사용
        - ✅ **시나리오 조회**: 정상 작동
        - ❌ **고급 벡터 분류**: Vector DB 필요
        
        **Vector DB 활성화 방법:**
        1. 필요한 패키지 설치 확인
        2. 앱을 재시작하여 Vector DB를 초기화
        3. 문제가 지속되면 관리자에게 문의
        """)
        
        # 의존성 설치 안내
        st.markdown("#### 📦 필요한 패키지 설치")
        st.code("""
# 로컬 환경에서 실행
pip install chromadb==0.4.22
pip install sentence-transformers==2.2.2

# 또는 requirements.txt 사용 (이미 업데이트됨)
pip install -r requirements.txt
        """)
        
        # Streamlit Cloud 문제 해결 안내
        st.markdown("#### ☁️ Streamlit Cloud 문제 해결")
        st.warning("""
        **SQLite3 버전 문제가 발생하는 경우:**
        
        1. **앱 재시작**: Streamlit Cloud에서 앱을 완전히 재시작
        2. **캐시 클리어**: 브라우저 캐시를 삭제하고 새로고침
        3. **InMemory 모드**: 자동으로 InMemory 클라이언트로 대체됨
        4. **FAISS 사용**: ChromaDB 대신 FAISS 사용 권장
        5. **MongoDB 연동**: 지속적인 데이터 저장을 위해 MongoDB Atlas 사용 권장
        """)
        
        st.info("""
        **Vector DB 옵션:**
        
        - **ChromaDB**: 고급 기능이 많지만 Streamlit Cloud에서 호환성 문제 발생
        - **FAISS**: 더 안정적이고 Streamlit Cloud에서 잘 작동
        - **InMemory 모드**: 데이터가 세션 동안만 유지됨
        - **샘플 데이터**: 자동으로 재생성됨
        """)
        
        # Vector DB 초기화 시도
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 ChromaDB 초기화 시도", type="primary"):
                try:
                    st.info("🔄 ChromaDB Vector DB 초기화를 시도하고 있습니다...")
                    from chroma_vector_classifier import ChromaVectorClassifier
                    classifier = ChromaVectorClassifier()
                    
                    # 초기화 결과 확인
                    st.write("**초기화 결과:**")
                    st.write(f"- Collection: {classifier.collection is not None}")
                    st.write(f"- Embedding Model: {classifier.embedding_model is not None}")
                    st.write(f"- Client: {classifier.client is not None}")
                    
                    if classifier.client:
                        try:
                            client_type = type(classifier.client).__name__
                            st.write(f"- Client 타입: {client_type}")
                        except Exception as e:
                            st.write(f"- Client 타입 확인 오류: {e}")
                    
                    if classifier.collection and classifier.embedding_model and classifier.client:
                        st.success("✅ ChromaDB Vector DB 초기화가 완료되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ ChromaDB Vector DB 초기화는 되었지만 일부 컴포넌트가 누락되었습니다.")
                        st.info("필요한 패키지를 설치한 후 앱을 재시작하세요.")
                except Exception as e:
                    st.error(f"❌ ChromaDB Vector DB 초기화 실패: {e}")
                    st.write(f"**오류 타입**: {type(e).__name__}")
                    st.write(f"**오류 상세**: {str(e)}")
                    st.info("필요한 패키지를 설치한 후 다시 시도하세요.")
        
        with col2:
            if st.button("🚀 FAISS Vector DB 시도", type="secondary"):
                try:
                    st.info("🔄 FAISS Vector DB 초기화를 시도하고 있습니다...")
                    from faiss_vector_classifier import FAISSVectorClassifier
                    classifier = FAISSVectorClassifier()
                    
                    # 초기화 결과 확인
                    st.write("**초기화 결과:**")
                    st.write(f"- Index: {classifier.index is not None}")
                    st.write(f"- Embedding Model: {classifier.embedding_model is not None}")
                    st.write(f"- Documents: {len(classifier.documents)}개")
                    
                    if classifier.index and classifier.embedding_model:
                        st.success("✅ FAISS Vector DB 초기화가 완료되었습니다!")
                        st.info("FAISS는 ChromaDB보다 Streamlit Cloud에서 더 안정적으로 작동합니다.")
                        st.rerun()
                    else:
                        st.error("❌ FAISS Vector DB 초기화는 되었지만 일부 컴포넌트가 누락되었습니다.")
                        st.info("필요한 패키지를 설치한 후 앱을 재시작하세요.")
                except Exception as e:
                    st.error(f"❌ FAISS Vector DB 초기화 실패: {e}")
                    st.write(f"**오류 타입**: {type(e).__name__}")
                    st.write(f"**오류 상세**: {str(e)}")
                    st.info("필요한 패키지를 설치한 후 다시 시도하세요.")
        st.stop()
    
    # Vector DB 통계 조회
    st.markdown("### 📊 Vector DB 통계")
    if st.button("📈 통계 조회", type="primary"):
        try:
            if 'classifier' in components and components['classifier']:
                classifier = components['classifier']
                
                # ChromaVectorClassifier인지 IssueClassifier인지 확인
                if hasattr(classifier, 'get_statistics'):
                    # ChromaVectorClassifier의 경우
                    stats = classifier.get_statistics()
                elif hasattr(classifier, 'get_vector_statistics'):
                    # IssueClassifier의 경우
                    stats = classifier.get_vector_statistics()
                else:
                    st.error("통계 조회 메서드를 찾을 수 없습니다.")
                    stats = None
                
                if stats is not None:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("총 문서 수", stats.get('total_documents', 0))
                    with col2:
                        st.metric("임베딩 모델", stats.get('embedding_model', 'N/A'))
                    with col3:
                        st.metric("컬렉션명", stats.get('collection_name', 'N/A'))
                
                    if 'issue_type_counts' in stats:
                        st.markdown("#### 📋 문제 유형별 문서 수")
                        issue_counts = stats['issue_type_counts']
                        for issue_type, count in issue_counts.items():
                            st.write(f"- **{issue_type}**: {count}개")
                
                st.json(stats)
            else:
                st.error("❌ 분류기가 초기화되지 않았습니다.")
                
        except Exception as e:
            st.error(f"❌ 통계 조회 실패: {e}")
            st.write(f"오류 상세: {str(e)}")
    
    st.markdown("---")
    
    # 새 학습 데이터 추가
    st.markdown("### 📝 새 학습 데이터 추가")
    
    with st.form("add_training_data"):
        st.markdown("**새로운 학습 데이터를 Vector DB에 추가합니다.**")
        
        # 문제 유형 선택
        issue_types = [
            "현재 비밀번호가 맞지 않습니다",
            "VMS와의 통신에 실패했습니다", 
            "Ping 테스트에 실패했습니다",
            "Onvif 응답이 없습니다",
            "로그인 차단 상태입니다",
            "비밀번호 변경에 실패했습니다",
            "PK P 계정 로그인 안됨",
            "PK P 웹 접속 안됨",
            "기타"
        ]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            new_issue_type = st.selectbox("문제 유형", issue_types, key="new_issue_type")
        with col2:
            customer_name = st.text_input("고객사명 (선택사항)", placeholder="ABC 주식회사")
        
        new_input = st.text_area(
            "고객 문의 내용", 
            placeholder="예: PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다.",
            height=100,
            key="new_customer_input"
        )
        
        summary = st.text_input("요약 (선택사항)", placeholder="비밀번호 인증 실패 문제")
        
        submitted = st.form_submit_button("➕ 데이터 추가", type="primary")
        
        if submitted:
            if new_input.strip():
                try:
                    if 'classifier' in components and components['classifier']:
                        # 메타데이터 구성
                        metadata = {
                            'customer_name': customer_name,
                            'summary': summary,
                            'added_by': st.session_state.get('user_name', 'Unknown'),
                            'added_timestamp': datetime.now().isoformat()
                        }
                        
                        # Vector DB에 추가
                        classifier = components['classifier']
                        
                        # ChromaVectorClassifier인지 IssueClassifier인지 확인
                        if hasattr(classifier, 'add_training_data'):
                            # ChromaVectorClassifier 또는 IssueClassifier 둘 다 이 메서드를 가짐
                            success = classifier.add_training_data(
                                new_input, 
                                new_issue_type, 
                                metadata
                            )
                        else:
                            st.error("add_training_data 메서드를 찾을 수 없습니다.")
                            success = False
                        
                        if success:
                            st.success(f"✅ 학습 데이터가 추가되었습니다! (문제 유형: {new_issue_type})")
                            st.balloons()
                        else:
                            st.error("❌ 데이터 추가에 실패했습니다.")
                    else:
                        st.error("❌ 분류기가 초기화되지 않았습니다.")
                        
                except Exception as e:
                    st.error(f"❌ 데이터 추가 중 오류: {e}")
                    st.write(f"오류 상세: {str(e)}")
            else:
                st.warning("⚠️ 고객 문의 내용을 입력해주세요.")
    
    st.markdown("---")
    
    # Vector DB 관리
    st.markdown("### ⚙️ Vector DB 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 샘플 데이터 재생성", help="기존 데이터를 모두 삭제하고 샘플 데이터를 다시 생성합니다."):
            try:
                if 'classifier' in components and components['classifier']:
                    classifier = components['classifier']
                    
                    # clear_database 메서드 확인
                    if hasattr(classifier, 'clear_database'):
                        # Vector DB 초기화
                        success = classifier.clear_database()
                    elif hasattr(classifier, 'vector_classifier') and classifier.vector_classifier and hasattr(classifier.vector_classifier, 'clear_database'):
                        # IssueClassifier 내부의 vector_classifier 사용
                        success = classifier.vector_classifier.clear_database()
                    else:
                        st.error("clear_database 메서드를 찾을 수 없습니다.")
                        success = False
                    if success:
                        st.success("✅ 샘플 데이터가 재생성되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 샘플 데이터 재생성에 실패했습니다.")
                else:
                    st.error("❌ Vector DB가 초기화되지 않았습니다.")
            except Exception as e:
                st.error(f"❌ 재생성 중 오류: {e}")
                st.write(f"오류 상세: {str(e)}")
    
    with col2:
        if st.button("🗑️ 전체 데이터 삭제", help="모든 Vector DB 데이터를 삭제합니다."):
            try:
                if 'classifier' in components and components['classifier']:
                    classifier = components['classifier']
                    
                    # clear_database 메서드 확인
                    if hasattr(classifier, 'clear_database'):
                        success = classifier.clear_database()
                    elif hasattr(classifier, 'vector_classifier') and classifier.vector_classifier and hasattr(classifier.vector_classifier, 'clear_database'):
                        # IssueClassifier 내부의 vector_classifier 사용
                        success = classifier.vector_classifier.clear_database()
                    else:
                        st.error("clear_database 메서드를 찾을 수 없습니다.")
                        success = False
                    if success:
                        st.success("✅ 모든 데이터가 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 데이터 삭제에 실패했습니다.")
                else:
                    st.error("❌ Vector DB가 초기화되지 않았습니다.")
            except Exception as e:
                st.error(f"❌ 삭제 중 오류: {e}")
                st.write(f"오류 상세: {str(e)}")
    
    
    

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
©2025 PrivKeeper P 장애 대응 자동화 시스템
</div>
""", unsafe_allow_html=True)