#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chroma_vector_classifier import ChromaVectorClassifier

def test_comprehensive():
    """포괄적인 분류기 테스트"""
    print("=== 포괄적인 문제유형 분류기 테스트 ===\n")
    
    # 분류기 초기화
    classifier = ChromaVectorClassifier()
    
    # 다양한 테스트 케이스들
    test_cases = [
        # 비밀번호 관련
        ("비밀번호가 맞지 않습니다", "현재 비밀번호가 맞지 않습니다"),
        ("패스워드 인증 실패", "현재 비밀번호가 맞지 않습니다"),
        ("CCTV 웹 로그인 실패", "현재 비밀번호가 맞지 않습니다"),
        ("비밀번호 변경이 안됩니다", "비밀번호 변경에 실패했습니다"),
        ("패스워드 수정 실패", "비밀번호 변경에 실패했습니다"),
        
        # VMS 관련
        ("VMS 통신 실패", "VMS와의 통신에 실패했습니다"),
        ("VMS 서버 연결 안됨", "VMS와의 통신에 실패했습니다"),
        ("NVR과 VMS 통신 오류", "VMS와의 통신에 실패했습니다"),
        
        # 네트워크 관련
        ("Ping 테스트 실패", "Ping 테스트에 실패했습니다"),
        ("네트워크 연결 안됨", "Ping 테스트에 실패했습니다"),
        ("통신 테스트 실패", "Ping 테스트에 실패했습니다"),
        
        # Onvif 관련
        ("Onvif 응답 없음", "Onvif 응답이 없습니다"),
        ("카메라 Onvif 통신 안됨", "Onvif 응답이 없습니다"),
        ("Onvif 프로토콜 오류", "Onvif 응답이 없습니다"),
        
        # 로그인 차단 관련
        ("로그인 차단됨", "로그인 차단 상태입니다"),
        ("계정 잠금 상태", "로그인 차단 상태입니다"),
        ("CCTV 차단 상태", "로그인 차단 상태입니다"),
        
        # PK P 계정 관련
        ("PK P 계정 로그인 안됨", "PK P 계정 로그인 안됨"),
        ("30일 미접속으로 잠김", "PK P 계정 로그인 안됨"),
        ("계정이 잠겼습니다", "PK P 계정 로그인 안됨"),
        
        # PK P 웹 관련
        ("PK P 웹 접속 안됨", "PK P 웹 접속 안됨"),
        ("웹사이트 접속 실패", "PK P 웹 접속 안됨"),
        ("톰캣 서비스 중단", "PK P 웹 접속 안됨"),
        ("웹 페이지 로드 안됨", "PK P 웹 접속 안됨"),
        
        # 기타
        ("알 수 없는 오류", "기타"),
        ("시스템 오류 발생", "기타"),
        ("예상치 못한 문제", "기타")
    ]
    
    print("=== 분류 정확도 테스트 ===\n")
    
    correct_count = 0
    total_count = len(test_cases)
    
    for i, (input_text, expected_type) in enumerate(test_cases, 1):
        print(f"--- 테스트 {i:2d} ---")
        print(f"입력: {input_text}")
        print(f"예상: {expected_type}")
        
        try:
            result = classifier.classify_issue(input_text)
            predicted_type = result['issue_type']
            confidence = result['confidence']
            method = result['method']
            
            is_correct = predicted_type == expected_type
            if is_correct:
                correct_count += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"결과: {predicted_type} ({confidence}) [{method}] {status}")
            
            if 'matched_keywords' in result and result['matched_keywords']:
                print(f"키워드: {result['matched_keywords']}")
            
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print()
    
    # 정확도 계산
    accuracy = (correct_count / total_count) * 100
    print(f"=== 테스트 결과 ===")
    print(f"총 테스트: {total_count}개")
    print(f"정확한 분류: {correct_count}개")
    print(f"정확도: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 우수한 분류 성능!")
    elif accuracy >= 60:
        print("👍 양호한 분류 성능")
    else:
        print("⚠️ 분류 성능 개선 필요")

if __name__ == "__main__":
    test_comprehensive()
