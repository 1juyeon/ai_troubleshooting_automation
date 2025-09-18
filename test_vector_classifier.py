#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== 벡터 분류기 직접 테스트 ===")

try:
    from chroma_vector_classifier import ChromaVectorClassifier
    print("✅ ChromaVectorClassifier 임포트 성공")
    
    # 벡터 분류기 초기화
    print("\n--- 벡터 분류기 초기화 ---")
    classifier = ChromaVectorClassifier()
    print("✅ 벡터 분류기 초기화 완료")
    
    # 테스트 케이스
    test_input = "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다."
    print(f"\n--- 테스트 입력: {test_input} ---")
    
    # 분류 실행
    result = classifier.classify_issue(test_input)
    print(f"✅ 분류 결과: {result['issue_type']}")
    print(f"✅ 분류 방법: {result['method']}")
    print(f"✅ 신뢰도: {result['confidence']}")
    print(f"✅ 유사도 점수: {result.get('similarity_score', 'N/A')}")
    
    # 통계 조회
    print("\n--- 벡터 DB 통계 ---")
    stats = classifier.get_statistics()
    print(f"총 문서 수: {stats['total_documents']}")
    print(f"문제 유형: {stats['issue_types']}")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 테스트 완료 ===")
