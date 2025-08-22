#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 응답 파싱 수정사항 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpt_handler import GPTHandler
from gemini_handler import GeminiHandler

def test_gpt_parsing():
    """GPT 핸들러 파싱 테스트"""
    print("=" * 50)
    print("GPT 핸들러 파싱 테스트")
    print("=" * 50)
    
    # 테스트용 AI 응답 텍스트
    test_response = """[대응유형]
해결안

[응답내용]

요약: 고객이 PrivKeeper P에서 비밀번호 변경을 시도했으나 '인증 실패' 오류가 발생하여 변경이 되지 않는 문제입니다.

조치 흐름: 
1. PK P 설정에서 CCTV 비밀번호 확인
2. HTTPS/HTTP 프로토콜 설정 확인
3. 필요시 현장 확인

이메일 초안: 
안녕하세요,

고객이 PrivKeeper P에서 비밀번호 변경을 시도했으나 '인증 실패' 오류가 발생하여 변경이 되지 않는다고 합니다.

현재 발생한 문제는 PK P에 저장된 비밀번호로 CCTV 웹 접속이 안되는 것으로 파악됩니다.

권장 조치사항:
1. PK P 설정에서 CCTV 비밀번호를 확인해주세요
2. HTTPS/HTTP 프로토콜 설정이 올바른지 확인해주세요
3. 위 조치로 해결되지 않으면 현장 확인이 필요할 수 있습니다

추가 문의사항이 있으시면 언제든지 연락주시기 바랍니다.

감사합니다."""
    
    # GPT 핸들러 생성 (API 키 없이)
    handler = GPTHandler()
    
    # 파싱 테스트
    parsed_result = handler.parse_response(test_response)
    
    print("파싱 결과:")
    print(f"응답 유형: {parsed_result.get('response_type', 'N/A')}")
    print(f"요약: {parsed_result.get('summary', 'N/A')}")
    print(f"조치 흐름: {parsed_result.get('action_flow', 'N/A')}")
    print(f"이메일 초안: {parsed_result.get('email_draft', 'N/A')}")
    
    # 검증 및 보완 테스트
    validated_result = handler._validate_and_fix_parsed_response(parsed_result, test_response)
    
    print("\n검증 및 보완 후 결과:")
    print(f"응답 유형: {validated_result.get('response_type', 'N/A')}")
    print(f"요약: {validated_result.get('summary', 'N/A')}")
    print(f"조치 흐름: {validated_result.get('action_flow', 'N/A')}")
    print(f"이메일 초안: {validated_result.get('email_draft', 'N/A')}")
    
    return parsed_result, validated_result

def test_gemini_parsing():
    """Gemini 핸들러 파싱 테스트"""
    print("\n" + "=" * 50)
    print("Gemini 핸들러 파싱 테스트")
    print("=" * 50)
    
    # 테스트용 AI 응답 텍스트
    test_response = """[대응유형]
질문

[응답내용]

요약: 고객이 PrivKeeper P와 VMS 간 통신에 실패하는 문제입니다.

조치 흐름: 
1. PKP 웹 설정 > NVR/VMS 항목 확인
2. VMS 패스워드 일치 여부 확인
3. 네트워크 연결 상태 확인

이메일 초안: 
안녕하세요,

고객이 PrivKeeper P와 VMS 간 통신에 실패하는 문제입니다.

현재 발생한 문제는 VMS와의 통신 실패로 파악됩니다.

권장 조치사항:
1. PKP 웹 설정 > NVR/VMS 항목에서 등록된 VMS 패스워드 확인
2. VMS 패스워드와 PK P 설정이 일치하는지 확인
3. 네트워크 연결 상태 확인

추가 문의사항이 있으시면 언제든지 연락주시기 바랍니다.

감사합니다."""
    
    # Gemini 핸들러 생성 (API 키 없이)
    handler = GeminiHandler()
    
    # 파싱 테스트
    parsed_result = handler._parse_response(test_response)
    
    print("파싱 결과:")
    print(f"응답 유형: {parsed_result.get('response_type', 'N/A')}")
    print(f"요약: {parsed_result.get('summary', 'N/A')}")
    print(f"조치 흐름: {parsed_result.get('action_flow', 'N/A')}")
    print(f"이메일 초안: {parsed_result.get('email_draft', 'N/A')}")
    
    # 검증 및 보완 테스트
    validated_result = handler._validate_and_fix_parsed_response(parsed_result, test_response)
    
    print("\n검증 및 보완 후 결과:")
    print(f"응답 유형: {validated_result.get('response_type', 'N/A')}")
    print(f"요약: {validated_result.get('summary', 'N/A')}")
    print(f"조치 흐름: {validated_result.get('action_flow', 'N/A')}")
    print(f"이메일 초안: {validated_result.get('email_draft', 'N/A')}")
    
    return parsed_result, validated_result

def test_complete_response_generation():
    """완전한 응답 생성 테스트"""
    print("\n" + "=" * 50)
    print("완전한 응답 생성 테스트")
    print("=" * 50)
    
    # 테스트 데이터
    test_data = {
        "customer_input": "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다.",
        "issue_type": "현재 비밀번호가 맞지 않습니다",
        "condition_1": "고객이 PK P에 저장된 비밀번호로 CCTV 웹 접속 가능한가?",
        "condition_2": "접속 방식이 HTTPS 또는 HTTP인지 확인되었는가?"
    }
    
    # GPT 핸들러 테스트 (API 키 없이)
    print("GPT 핸들러 테스트:")
    gpt_handler = GPTHandler()
    gpt_result = gpt_handler.generate_complete_response(**test_data)
    
    if gpt_result["success"]:
        print("✅ GPT 응답 생성 성공")
        parsed = gpt_result["gpt_result"]["parsed_response"]
        print(f"응답 유형: {parsed.get('response_type', 'N/A')}")
        print(f"요약: {parsed.get('summary', 'N/A')[:100]}...")
    else:
        print(f"❌ GPT 응답 생성 실패: {gpt_result.get('error', '알 수 없는 오류')}")
    
    # Gemini 핸들러 테스트 (API 키 없이)
    print("\nGemini 핸들러 테스트:")
    gemini_handler = GeminiHandler()
    gemini_result = gemini_handler.generate_complete_response(**test_data)
    
    if gemini_result["success"]:
        print("✅ Gemini 응답 생성 성공")
        parsed = gemini_result["gemini_result"]["parsed_response"]
        print(f"응답 유형: {parsed.get('response_type', 'N/A')}")
        print(f"요약: {parsed.get('summary', 'N/A')[:100]}...")
    else:
        print(f"❌ Gemini 응답 생성 실패: {gemini_result.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    print("AI 응답 파싱 수정사항 테스트 시작")
    print("이 테스트는 API 키 없이 파싱 로직만 검증합니다.")
    
    try:
        # 개별 파싱 테스트
        gpt_parsed, gpt_validated = test_gpt_parsing()
        gemini_parsed, gemini_validated = test_gemini_parsing()
        
        # 완전한 응답 생성 테스트
        test_complete_response_generation()
        
        print("\n" + "=" * 50)
        print("테스트 완료!")
        print("=" * 50)
        
        # 결과 요약
        print("\n결과 요약:")
        print(f"GPT 파싱: {'성공' if gpt_parsed else '실패'}")
        print(f"GPT 검증: {'성공' if gpt_validated else '실패'}")
        print(f"Gemini 파싱: {'성공' if gemini_parsed else '실패'}")
        print(f"Gemini 검증: {'성공' if gemini_validated else '실패'}")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
