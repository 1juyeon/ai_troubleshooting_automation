#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Secrets 테스트 스크립트
이 스크립트로 API 키가 제대로 로드되는지 확인할 수 있습니다.
"""

import os
import sys

def test_environment_variables():
    """환경변수 테스트"""
    print("🔍 환경변수 테스트:")
    
    # GOOGLE_API_KEY 확인
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        print(f"✅ GOOGLE_API_KEY: {google_api_key[:10]}... (길이: {len(google_api_key)})")
    else:
        print("❌ GOOGLE_API_KEY: 설정되지 않음")
    
    # GEMINI_API_KEY 확인
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        print(f"✅ GEMINI_API_KEY: {gemini_api_key[:10]}... (길이: {len(gemini_api_key)})")
    else:
        print("❌ GEMINI_API_KEY: 설정되지 않음")
    
    print()

def test_streamlit_secrets():
    """Streamlit Secrets 테스트"""
    print("🔍 Streamlit Secrets 테스트:")
    
    try:
        import streamlit as st
        
        # st.secrets 접근 테스트
        if hasattr(st, 'secrets'):
            print("✅ st.secrets 접근 가능")
            
            # GEMINI_API_KEY 확인
            try:
                gemini_key = st.secrets["GEMINI_API_KEY"]
                if gemini_key:
                    print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}... (길이: {len(gemini_key)})")
                else:
                    print("❌ GEMINI_API_KEY: 빈 값")
            except KeyError:
                print("❌ GEMINI_API_KEY: secrets에 없음")
            
            # GOOGLE_CLIENT_ID 확인
            try:
                client_id = st.secrets["GOOGLE_CLIENT_ID"]
                if client_id:
                    print(f"✅ GOOGLE_CLIENT_ID: {client_id[:10]}... (길이: {len(client_id)})")
                else:
                    print("❌ GOOGLE_CLIENT_ID: 빈 값")
            except KeyError:
                print("❌ GOOGLE_CLIENT_ID: secrets에 없음")
                
        else:
            print("❌ st.secrets 접근 불가")
            
    except ImportError:
        print("❌ streamlit 모듈을 import할 수 없음")
    
    print()

def test_gpt_handler():
    """GPTHandler 테스트"""
    print("🔍 GPTHandler 테스트:")
    
    try:
        from gpt_handler import GPTHandler
        
        # GPTHandler 초기화 테스트
        handler = GPTHandler()
        
        if handler.model:
            print("✅ GPTHandler 초기화 성공")
            print(f"✅ 모델: {handler.model}")
        else:
            print("❌ GPTHandler 초기화 실패 - API 키 문제")
            
    except ImportError as e:
        print(f"❌ gpt_handler 모듈 import 실패: {e}")
    except Exception as e:
        print(f"❌ GPTHandler 테스트 실패: {e}")
    
    print()

def main():
    """메인 테스트 함수"""
    print("🚀 Streamlit Secrets 및 API 키 테스트 시작")
    print("=" * 50)
    
    test_environment_variables()
    test_streamlit_secrets()
    test_gpt_handler()
    
    print("=" * 50)
    print("🏁 테스트 완료")
    
    print("\n📋 다음 단계:")
    print("1. .streamlit/secrets.toml 파일에 실제 API 키 입력")
    print("2. streamlit run app.py 실행")
    print("3. Streamlit Cloud 배포 시 Cloud Secrets 설정")

if __name__ == "__main__":
    main()
