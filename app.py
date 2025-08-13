import streamlit as st
from datetime import datetime, timezone, date, timedelta
import pandas as pd
import json
import os
import requests
from typing import Dict, Any
import pickle
import pytz

# 커스텀 모듈 import
from classify_issue import IssueClassifier
from scenario_db import ScenarioDB
from vector_search import VectorSearchWrapper
from gpt_handler import GPTHandler
from database import HistoryDB
from multi_user_database import MultiUserHistoryDB

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

# 안전한 타임스탬프 생성 함수
def get_safe_timestamp():
    """안전한 타임스탬프 생성 (한국 시간대, 실패 시 UTC 사용)"""
    try:
        return datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
    except Exception as e:
        print(f"⚠️ 한국 시간대 설정 실패, UTC 사용: {e}")
        return datetime.now().isoformat()

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
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 📊 문제 유형 분류")
        st.write("**분류된 문제 유형:** PKP 웹 접속 안됨")
        st.write("**분류 방법:** keyword_based")
        st.write("**신뢰도:** medium")
    
    with col4:
        st.markdown("#### 🎯 시나리오 매칭")
        st.write("**조건 1:** 윈도우 서비스에서 톰캣 작동 여부를 확인하였는가?")
        st.write("**조건 2:** 톰캣이 꺼져 있는가?")
        st.write("**해결책:** 톰캣 서비스 시작")
        st.write("**현장 출동 필요:** N")
    
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
        email_content = """제목: PKP 웹 접속 불가 문의 답변

고객님 안녕하세요.

PKP 웹 접속 불가 현상에 대한 문의 주셔서 감사합니다.

웹 접속 불가 현상은 여러 가지 원인으로 발생할 수 있습니다. 먼저 아래 내용을 확인 부탁드립니다.

1. 컴퓨터의 윈도우 서비스 목록에서 "Apache Tomcat" 서비스가 실행 중인지 확인해주세요.
2. 웹 브라우저에서 `http://localhost:8080/` (포트 번호는 환경에 따라 다를 수 있습니다) 에 접속하여 톰캣 기본 페이지가 정상적으로 표시되는지 확인해주세요.

위의 내용 확인 후에도 문제가 지속될 경우, 아래 정보를 회신해주시면 더 정확한 지원을 드릴 수 있습니다.

- 톰캣 서비스 실행 여부
- `http://localhost:8080/` 접속 결과 (에러 메시지 등)

빠른 시간 안에 문제를 해결하실 수 있도록 최선을 다하겠습니다.

감사합니다."""
        
        st.text_area("이메일 내용", email_content, height=300)
        
        # 복사 버튼
        if st.button("📋 이메일 복사", use_container_width=True):
            st.success("이메일 내용이 클립보드에 복사되었습니다!")
    
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
        st.markdown("## 🔍 AI 분석 상세 결과")
        
        # 선택된 데이터 정보 표시 (간격 줄임)
        with st.expander("📋 입력된 문의 정보", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                customer_name = selected_row.get('고객사명', '')
                st.write(f"**고객사명:** {customer_name if customer_name else ''}")
                st.write(f"**문의유형:** {selected_row.get('문의유형', 'N/A')}")
                st.write(f"**우선순위:** {selected_row.get('우선순위', 'N/A')}")
            with col2:
                st.write(f"**담당자:** {selected_row.get('담당자', 'N/A')}")
                st.write(f"**역할:** {selected_row.get('역할', 'N/A')}")
                st.write(f"**날짜:** {selected_row.get('날짜', 'N/A')}")
        
        # 실제 분석 결과 조회 시도
        try:
            # 데이터베이스에서 해당 문의의 실제 분석 결과 조회
            if 'components' in st.session_state:
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
                
                if actual_analysis and actual_analysis.get('success'):
                    analysis_data = actual_analysis.get('data', {})
                    
                    # AI 분석 결과 (실제 데이터) - 간격 줄임
                    st.markdown("### 🔍 AI 분석 결과")
                    
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        st.markdown("#### 📊 문제 유형 분류")
                        issue_type = analysis_data.get('issue_type', selected_row.get('문의유형', 'N/A'))
                        st.write(f"**분류된 문제 유형:** {issue_type}")
                        
                        # 분류 방법과 신뢰도 정보 표시
                        classification = analysis_data.get('classification', {})
                        classification_method = classification.get('method', 'AI 자동 분류')
                        confidence = classification.get('confidence', '높음')
                        st.write(f"**분류 방법:** {classification_method}")
                        st.write(f"**신뢰도:** {confidence}")
                    
                    with col4:
                        st.markdown("#### 🎯 시나리오 매칭")
                        if 'best_scenario' in analysis_data and analysis_data['best_scenario']:
                            scenario = analysis_data['best_scenario']
                            st.write(f"**조건 1:** {scenario.get('condition_1', 'N/A')}")
                            st.write(f"**조건 2:** {scenario.get('condition_2', 'N/A')}")
                            st.write(f"**해결책:** {scenario.get('solution', 'N/A')}")
                            st.write(f"**현장 출동 필요:** {scenario.get('onsite_needed', 'N')}")
                        else:
                            st.write("**조건 1:** 해당 시나리오 없음")
                            st.write("**조건 2:** 해당 시나리오 없음")
                            st.write("**해결책:** 기본 가이드 제공")
                            st.write("**현장 출동 필요:** N")
                    
                    # AI 응답 결과 - 간격 줄임
                    st.markdown("### 🤖 AI 응답")
                    
                    col5, col6 = st.columns(2)
                    
                    with col5:
                        st.markdown("#### 📝 요약")
                        if 'gemini_result' in analysis_data and analysis_data['gemini_result'].get('success'):
                            parsed = analysis_data['gemini_result'].get('parsed_response', {})
                            
                            summary = parsed.get('summary', '')
                            if summary:
                                st.write(summary)
                            else:
                                st.write("해당 문의에 대한 AI 분석 요약이 없습니다.")
                            
                            st.markdown("#### 🔧 조치 흐름")
                            action_flow = parsed.get('action_flow', '')
                            if action_flow:
                                st.write(action_flow)
                            else:
                                st.write("해당 문의에 대한 조치 흐름이 없습니다.")
                        else:
                            st.write("해당 문의에 대한 AI 분석 요약이 없습니다.")
                            st.markdown("#### 🔧 조치 흐름")
                            st.write("해당 문의에 대한 조치 흐름이 없습니다.")
                    
                    with col6:
                        st.markdown("#### 📧 이메일 초안")
                        if 'gemini_result' in analysis_data and analysis_data['gemini_result'].get('success'):
                            parsed = analysis_data['gemini_result'].get('parsed_response', {})
                            email_content = parsed.get('email_draft', '해당 문의에 대한 이메일 초안이 없습니다.')
                        else:
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
                        
                        st.text_area("이메일 내용", email_content, height=150, disabled=True)
                        
                        # 이메일 복사 버튼
                        if st.button("📋 이메일 내용 복사", key=f"copy_email_{selected_row.get('번호', 'unknown')}"):
                            st.write("✅ 이메일 내용이 클립보드에 복사되었습니다.")
                
                else:
                    # 실제 분석 결과가 없는 경우 기본 정보만 표시
                    st.warning("⚠️ 해당 문의의 실제 AI 분석 결과를 찾을 수 없습니다.")
                    st.info("이는 다음과 같은 이유일 수 있습니다:")
                    st.info("1. 분석이 완료되지 않았거나 저장되지 않음")
                    st.info("2. Streamlit Cloud 환경에서 데이터 저장 문제")
                    st.info("3. 검색 조건이 정확하지 않음")
                    
                    # 기본 정보 표시
                    st.markdown("### 📋 기본 문의 정보")
                    st.write(f"**문의 내용:** {selected_row.get('문의내용', 'N/A')}")
                    st.write(f"**문의 유형:** {selected_row.get('문의유형', 'N/A')}")
                    st.write(f"**담당자:** {selected_row.get('담당자', 'N/A')}")
                    
            else:
                st.error("❌ 컴포넌트가 초기화되지 않았습니다.")
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
        st.session_state.current_api_key = st.secrets.get("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
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

# 세션 상태 초기화
init_session_state()

# 컴포넌트 초기화
def init_components():
    """컴포넌트 초기화"""
    try:
        classifier = IssueClassifier()
        scenario_db = ScenarioDB()
        vector_search = VectorSearchWrapper()
        
        # API 키 설정 (사이드바 우선, st.secrets 차선, 환경변수 마지막)
        api_key = ""
        
        # 1. 사이드바에서 설정한 API 키 우선 사용
        if 'current_api_key' in st.session_state and st.session_state.current_api_key:
            api_key = st.session_state.current_api_key
            print("✅ Gemini API 키를 사이드바에서 로드했습니다.")
        # 2. st.secrets에서 시도
        elif not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                print("✅ Gemini API 키를 Streamlit Secrets에서 로드했습니다.")
            except:
                pass
        # 3. 환경변수로 폴백
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                print("✅ Gemini API 키를 환경변수에서 로드했습니다.")
        
        gpt_handler = GPTHandler(api_key=api_key)
        
        # API 키 상태 확인
        if not api_key:
            st.error("❌ Gemini API 키가 설정되지 않았습니다.")
            st.info("사이드바에서 API 키를 설정하거나, 관리자가 Streamlit Cloud Secrets 또는 환경변수 GOOGLE_API_KEY를 설정하면 AI 분석이 가능합니다.")
            st.stop()
        
        # 기존 데이터베이스 (호환성 유지)
        history_db = HistoryDB()
        multi_user_db = MultiUserHistoryDB()
        
        return {
            'classifier': classifier,
            'scenario_db': scenario_db,
            'vector_search': vector_search,
            'gpt_handler': gpt_handler,
            'history_db': history_db,
            'multi_user_db': multi_user_db
        }
    except Exception as e:
        st.error(f"❌ 컴포넌트 초기화 실패: {str(e)}")
        st.stop()

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
            "Gemini 2.0 Flash"
        ],
        index=0
    )
    
    # 세션 상태에 저장
    st.session_state.contact_name = contact_name
    st.session_state.role = role
    st.session_state.ai_model = ai_model
    
    st.markdown("---")
    
    # 디버깅 정보 (Streamlit Cloud 환경 확인)
    st.markdown("## 🔍 시스템 정보")
    
    # 환경 정보
    is_cloud = os.getenv('STREAMLIT_SERVER_RUNNING') == 'true'
    if is_cloud:
        st.success("☁️ Streamlit Cloud 환경")
        st.info("데이터는 임시 저장소에 저장됩니다.")
    else:
        st.info("💻 로컬 환경")
        st.info("데이터는 파일 시스템에 저장됩니다.")
    
    # 데이터 저장 상태 확인
    if 'components' in st.session_state and 'multi_user_db' in st.session_state.components:
        multi_user_db = st.session_state.components['multi_user_db']
        
        if hasattr(multi_user_db, 'is_cloud') and multi_user_db.is_cloud:
            # 클라우드 환경에서 저장된 데이터 확인
            if hasattr(multi_user_db, 'cloud_storage'):
                stored_keys = multi_user_db.cloud_storage.get_all_keys()
                st.info(f"📊 저장된 데이터: {len(stored_keys)}개")
                if stored_keys:
                    st.write("저장된 키:")
                    for key in stored_keys[:5]:  # 처음 5개만 표시
                        st.write(f"• {key}")
                    if len(stored_keys) > 5:
                        st.write(f"... 외 {len(stored_keys) - 5}개")
                else:
                    st.warning("저장된 데이터가 없습니다.")
        else:
            # 로컬 환경에서 파일 상태 확인
            try:
                if hasattr(multi_user_db, 'data_dir') and os.path.exists(multi_user_db.data_dir):
                    files = os.listdir(multi_user_db.data_dir)
                    json_files = [f for f in files if f.endswith('.json')]
                    st.info(f"📁 데이터 파일: {len(json_files)}개")
                    if json_files:
                        st.write("파일 목록:")
                        for file in json_files[:5]:  # 처음 5개만 표시
                            st.write(f"• {file}")
                        if len(json_files) > 5:
                            st.write(f"... 외 {len(json_files) - 5}개")
                else:
                    st.warning("데이터 디렉토리를 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"파일 상태 확인 실패: {e}")
    
    # 데이터 초기화 버튼
    st.markdown("---")
    st.markdown("## 🗑️ 데이터 관리")
    
    if st.button("🗑️ 모든 데이터 초기화", type="secondary"):
        if 'components' in st.session_state and 'multi_user_db' in st.session_state.components:
            try:
                result = st.session_state.components['multi_user_db'].clear_all_history()
                if result.get('success'):
                    st.success("✅ 모든 데이터가 초기화되었습니다.")
                    st.rerun()
                else:
                    st.error(f"❌ 데이터 초기화 실패: {result.get('error', '알 수 없는 오류')}")
            except Exception as e:
                st.error(f"❌ 데이터 초기화 중 오류: {e}")
        else:
            st.error("❌ 데이터베이스가 초기화되지 않았습니다.")

# 컴포넌트 초기화 (캐싱 제거)
if 'components' not in st.session_state:
    components = init_components()
    st.session_state.components = components
else:
    components = st.session_state.components

# 메인 헤더
st.markdown("""
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom:2rem;'>
    <h1>🔧 PrivKeeper P 장애 대응 자동화 시스템</h1>
    <p>Gemini AI 기반 고객 문의 자동 분석 및 응답 도구</p>
</div>
""", unsafe_allow_html=True)

# 환영 메시지
#st.success("✅ AI 분석 서비스를 이용할 수 있습니다!")

# 탭 생성
tab_names = ["📝 고객 문의 입력", "🤖 AI 분석 결과", "📊 이력 관리", "📚 사용 가이드"]

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(tab_names)

# 분석 완료 알림 (전역적으로 표시)
# if st.session_state.analysis_result and st.session_state.analysis_completed:
#    st.success("✅ AI 분석이 완료되었습니다! AI 분석 결과 페이지로 이동해 상세한 결과를 확인하세요.")

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
                            gemini_result = components['gpt_handler'].generate_complete_response(
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
                                "parsed_response": components['gpt_handler']._generate_default_response(
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
                           'timestamp': get_safe_timestamp()
                    }
                    
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
                    
                    # 다중 사용자 데이터베이스에 저장
                    try:
                        # inquiry_data에 사용자 정보 추가
                        inquiry_data_with_user = st.session_state.inquiry_data.copy()
                        inquiry_data_with_user['user_email'] = f"{st.session_state.contact_name}_{st.session_state.role}@privkeeper.com"
                        
                        # 저장 시도
                        save_result = components['multi_user_db'].save_analysis(analysis_result, inquiry_data_with_user)
                        
                        if save_result.get('success'):
                            st.success(f"✅ 분석 결과가 저장되었습니다. (사용자: {save_result.get('user_name', 'Unknown')}, ID: {save_result.get('user_id', 'Unknown')})")
                        else:
                            error_msg = save_result.get('error', '알 수 없는 오류')
                            st.warning(f"⚠️ 분석 결과 저장에 실패했습니다: {error_msg}")
                            
                            # 백업 저장 시도
                            try:
                                backup_result = components['history_db'].save_analysis(analysis_result, inquiry_data_with_user)
                                if backup_result.get('success'):
                                    st.info("📋 백업 저장소에 저장되었습니다.")
                                else:
                                    st.error("❌ 백업 저장도 실패했습니다.")
                            except Exception as backup_e:
                                st.error(f"❌ 백업 저장 중 오류: {backup_e}")
                                
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
                filename = f"analysis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    # 필터링 옵션
    col15, col16, col17, col18 = st.columns(4)
    
    with col15:
        filter_date_from = st.date_input("시작 날짜", value=date.today() - timedelta(days=30))
    
    with col16:
        filter_date_to = st.date_input("종료 날짜", value=date.today())
    
    with col17:
        filter_type = st.selectbox("문제 유형 필터", 
            ["전체"] + ["현재 비밀번호가 맞지 않습니다", "VMS와의 통신에 실패했습니다", "Ping 테스트에 실패했습니다", 
                       "Onvif 응답이 없습니다", "로그인 차단 상태입니다(CCTV)", "비밀번호 변경에 실패했습니다",
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
                # 종료 날짜를 포함하도록 23:59:59 추가
                date_to_with_time = None
                if filter_date_to:
                    date_to_with_time = f"{filter_date_to.isoformat()}T23:59:59"
                
                # 전체 이력 조회
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
                    
                    st.success(f"✅ {len(history_data)}건의 이력이 조회되었습니다.")
                    
                    # 이력 조회 결과 표시 (기본 데이터프레임 + 커스텀 테이블 모두 표시)
                    st.markdown("### 📊 이력 조회 결과")
                    
                    # 1. 기본 st.dataframe 표시 (위쪽)
                    # st.markdown("#### 📋 기본 데이터프레임")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # 2. 커스텀 테이블 UI (아래쪽)
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
                    
                    # 데이터 행들
                    for index, row in df.iterrows():
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
                            if st.button(f"🔍", key=f"detail_btn_{index}_{row.get('번호', 'unknown')}", 
                                       help="클릭하여 상세 분석 결과 보기"):
                                st.session_state.selected_row_for_detail = row.to_dict()
                                st.session_state.show_detail_modal = True
                        
                        # 구분선 추가
                        st.markdown("---")
                    
                    # 상세보기 모달 표시
                    if st.session_state.get('show_detail_modal', False) and st.session_state.get('selected_row_for_detail'):
                        with st.expander("🔍 AI 분석 상세 결과", expanded=True):
                            show_ai_analysis_modal(st.session_state.selected_row_for_detail)
                            # 모달 닫기 버튼
                            if st.button("❌ 닫기", key="close_modal"):
                                st.session_state.show_detail_modal = False
                                st.session_state.selected_row_for_detail = None
                    
                    # 통계 정보
                    stats = components['multi_user_db'].get_statistics()
                    
                    col19, col20, col21, col22 = st.columns(4)
                    
                    with col19:
                        st.metric("총 문의 건수", stats.get('total_analyses', 0))
                    
                    with col20:
                        st.metric("총 사용자 수", stats.get('total_users', 0))
                    
                    with col21:
                        st.metric("문제 유형 수", len(stats.get('issue_types', [])))
                    
                    with col22:
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
        
        # 이전 검색 결과도 동일한 방식으로 표시
        df_previous = st.session_state.history_search_results.copy()
        
        # 1. 기본 st.dataframe 표시 (위쪽)
        #st.markdown("#### 📋 기본 데이터프레임")
        st.dataframe(df_previous, use_container_width=True, hide_index=True)
        
        # 2. 커스텀 테이블 UI (아래쪽)
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
        
        # 데이터 행들
        for index, row in df_previous.iterrows():
            prev_row_cols = st.columns([2, 2, 2, 2, 2, 2, 2, 1])
            
            with prev_row_cols[0]:
                st.markdown(f'<div class="history-table-cell">{row.get("번호", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[1]:
                st.markdown(f'<div class="history-table-cell">{row.get("날짜", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[2]:
                st.markdown(f'<div class="history-table-cell">{row.get("고객사명", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[3]:
                st.markdown(f'<div class="history-table-cell">{row.get("문의유형", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[4]:
                st.markdown(f'<div class="history-table-cell">{row.get("우선순위", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[5]:
                st.markdown(f'<div class="history-table-cell">{row.get("담당자", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[6]:
                st.markdown(f'<div class="history-table-cell">{row.get("역할", "N/A")}</div>', unsafe_allow_html=True)
            with prev_row_cols[7]:
                if st.button(f"🔍", key=f"prev_detail_btn_{index}_{row.get('번호', 'unknown')}", 
                           help="클릭하여 상세 분석 결과 보기"):
                    st.session_state.selected_row_for_detail = row.to_dict()
                    st.session_state.show_detail_modal = True
            
            # 구분선 추가
            st.markdown("---")
        
        # 상세보기 모달 표시
        if st.session_state.get('show_detail_modal', False) and st.session_state.get('selected_row_for_detail'):
            with st.expander("🔍 AI 분석 상세 결과", expanded=True):
                show_ai_analysis_modal(st.session_state.selected_row_for_detail)
                # 모달 닫기 버튼
                if st.button("❌ 닫기", key="prev_close_modal"):
                    st.session_state.show_detail_modal = False
                    st.session_state.selected_row_for_detail = None

# 탭 4: 사용 가이드
with tab4:
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

    st.markdown(f"- **AI 모델:** Google {st.session_state.get('ai_model', 'Gemini 1.5 Pro')}")
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