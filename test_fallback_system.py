#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== Fallback 시스템 테스트 ===")

try:
    from classify_issue import IssueClassifier
    print("✅ classify_issue 모듈 임포트 성공")
    
    # 분류기 초기화
    print("\n--- 분류기 초기화 ---")
    classifier = IssueClassifier()
    print("✅ 분류기 초기화 완료")
    
    # 벡터 분류기 상태 확인
    if classifier.vector_classifier is not None:
        print("✅ 벡터 분류기 사용 가능")
    else:
        print("⚠️ 벡터 분류기 사용 불가 - 키워드 + Gemini 분류만 사용")
    
    # 테스트 케이스들
    test_cases = [
        "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다.",
        "VMS와의 통신에 실패했습니다.",
        "Ping 테스트에 실패했습니다.",
        "Onvif 프로토콜로 카메라와 통신이 안됩니다."
    ]
    
    print("\n--- 분류 테스트 ---")
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: {test_input}")
        result = classifier.classify_issue(test_input)
        print(f"  결과: {result['issue_type']}")
        print(f"  방법: {result['method']}")
        print(f"  신뢰도: {result['confidence']}")
    
    print("\n✅ 모든 테스트 완료")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 테스트 완료 ===")
