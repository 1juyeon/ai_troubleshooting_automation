#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
문제유형 분류기 테스트 스크립트
"""

from chroma_vector_classifier import ChromaVectorClassifier

def test_classifier():
    """분류기 테스트"""
    print("=== 문제유형 분류기 테스트 시작 ===\n")
    
    # 분류기 초기화
    print("🔄 분류기 초기화 중...")
    classifier = ChromaVectorClassifier()
    print("✅ 분류기 초기화 완료\n")
    
    # 테스트 케이스들
    test_cases = [
        "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다. 비밀번호는 정확히 입력했는데도 인증 실패가 발생합니다.",
        "VMS와의 통신에 실패했습니다. VMS 패스워드가 맞지 않는 것 같습니다.",
        "Ping 테스트에 실패했습니다. 네트워크 연결이 안되는 것 같습니다.",
        "Onvif 프로토콜로 카메라와 통신이 안됩니다.",
        "PK P 계정이 30일 미접속으로 잠겼습니다.",
        "웹 접속이 안됩니다",
        "톰캣 서비스가 중단되었습니다",
        "비밀번호 변경이 안됩니다",
        "CCTV 로그인이 차단되었습니다",
        "알 수 없는 오류가 발생했습니다"
    ]
    
    print("=== 분류 테스트 실행 ===\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"--- 테스트 케이스 {i} ---")
        print(f"입력: {test_input}")
        
        try:
            result = classifier.classify_issue(test_input)
            print(f"분류 결과: {result['issue_type']}")
            print(f"분류 방법: {result['method']}")
            print(f"신뢰도: {result['confidence']}")
            
            if 'score' in result:
                print(f"점수: {result['score']}")
            if 'matched_keywords' in result and result['matched_keywords']:
                print(f"매칭된 키워드: {result['matched_keywords']}")
            if 'error' in result:
                print(f"오류: {result['error']}")
                
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
        
        print()  # 빈 줄
    
    # 통계 출력
    print("=== 분류기 통계 ===")
    try:
        stats = classifier.get_statistics()
        print(f"총 문서 수: {stats.get('total_documents', 'N/A')}")
        print(f"문제 유형: {stats.get('issue_types', [])}")
        if 'issue_type_counts' in stats:
            print("문제 유형별 문서 수:")
            for issue_type, count in stats['issue_type_counts'].items():
                print(f"  - {issue_type}: {count}개")
    except Exception as e:
        print(f"❌ 통계 조회 실패: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_classifier()
