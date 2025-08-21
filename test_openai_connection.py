import streamlit as st
import os
from openai_handler import OpenAIHandler

st.set_page_config(
    page_title="OpenAI API 연결 테스트",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 OpenAI API 연결 테스트")

# API 키 입력
api_key = st.text_input(
    "OpenAI API 키",
    type="password",
    placeholder="sk-...",
    help="OpenAI에서 발급받은 API 키를 입력하세요"
)

if api_key:
    # OpenAI 핸들러 초기화
    handler = OpenAIHandler(api_key=api_key)
    
    if handler.client:
        st.success("✅ OpenAI API 클라이언트가 초기화되었습니다.")
        
        # 연결 테스트
        if st.button("🔗 연결 테스트"):
            with st.spinner("연결을 테스트하고 있습니다..."):
                test_result = handler.test_connection()
                
                if test_result['success']:
                    st.success(f"✅ {test_result['message']}")
                    st.info(f"모델: {test_result['model']}")
                    st.info(f"테스트 응답: {test_result['test_response']}")
                else:
                    st.error(f"❌ {test_result['error']}")
        
        # 사용 가능한 모델 목록
        if st.button("📋 사용 가능한 모델 목록"):
            with st.spinner("모델 목록을 가져오고 있습니다..."):
                models = handler.get_available_models()
                
                if models:
                    st.success(f"✅ {len(models)}개의 모델을 찾았습니다.")
                    for model in models:
                        st.write(f"- {model}")
                else:
                    st.warning("⚠️ 모델 목록을 가져올 수 없습니다.")
        
        # 간단한 테스트 요청
        st.markdown("---")
        st.markdown("### 🧪 간단한 테스트 요청")
        
        test_input = st.text_area(
            "테스트 입력",
            value="안녕하세요. 간단한 테스트입니다.",
            height=100
        )
        
        if st.button("🚀 테스트 요청"):
            if test_input.strip():
                with st.spinner("AI 응답을 생성하고 있습니다..."):
                    response = handler.generate_response(
                        customer_input=test_input,
                        issue_type="테스트",
                        condition_1="테스트 조건 1",
                        condition_2="테스트 조건 2"
                    )
                    
                    if response['success']:
                        st.success("✅ 응답 생성 성공!")
                        st.info(f"모델: {response['model']}")
                        st.info(f"토큰 사용량: {response['usage']['total_tokens']}")
                        st.markdown("### 📝 응답 내용")
                        st.write(response['response'])
                    else:
                        st.error(f"❌ 응답 생성 실패: {response['error']}")
            else:
                st.warning("⚠️ 테스트 입력을 입력해주세요.")
    else:
        st.error("❌ OpenAI API 클라이언트 초기화에 실패했습니다.")
        st.info("API 키를 확인해주세요.")
else:
    st.info("👆 OpenAI API 키를 입력해주세요.")
    st.markdown("""
    **API 키 발급 방법:**
    1. [OpenAI Platform](https://platform.openai.com/) 접속
    2. API Keys → Create new secret key
    3. 생성된 API 키를 복사하여 위에 입력
    """)
