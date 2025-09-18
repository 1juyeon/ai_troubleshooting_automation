#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== 간단한 분류기 테스트 ===")

try:
    from classify_issue import IssueClassifier
    print("✅ classify_issue 모듈 임포트 성공")
    
    # 분류기 초기화
    print("\n--- 분류기 초기화 ---")
    classifier = IssueClassifier()
    print("✅ 분류기 초기화 완료")
    
    # 테스트 케이스
    test_input = "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다."
    print(f"\n--- 테스트 입력: {test_input} ---")
    
    # 분류 실행
    result = classifier.classify_issue(test_input)
    print(f"✅ 분류 결과: {result['issue_type']}")
    print(f"✅ 분류 방법: {result['method']}")
    print(f"✅ 신뢰도: {result['confidence']}")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 테스트 완료 ===")
