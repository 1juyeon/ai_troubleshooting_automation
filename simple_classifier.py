import re
import json
from typing import Dict, Any, List

class SimpleIssueClassifier:
    def __init__(self):
        """간단한 키워드 기반 문제 유형 분류기"""
        self.issue_types = [
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
        
        # 키워드 매핑 정의
        self.keyword_mapping = {
            "현재 비밀번호가 맞지 않습니다": [
                "비밀번호", "패스워드", "password", "인증", "로그인", "접속", "웹", "cctv",
                "맞지 않", "틀렸", "실패", "오류", "인증 실패", "접속 실패", "로그인 실패"
            ],
            "VMS와의 통신에 실패했습니다": [
                "vms", "VMS", "통신", "연결", "서버", "svms", "nvr", "영상", "카메라",
                "실패", "오류", "연결 안", "통신 실패", "서버 연결"
            ],
            "Ping 테스트에 실패했습니다": [
                "ping", "Ping", "네트워크", "연결", "통신", "테스트", "응답", "네트워크 연결",
                "실패", "안됨", "오류", "ping 실패", "네트워크 실패"
            ],
            "Onvif 응답이 없습니다": [
                "onvif", "Onvif", "ONVIF", "프로토콜", "카메라", "설정", "통신", "응답",
                "없", "실패", "오류", "onvif 응답", "프로토콜 응답"
            ],
            "로그인 차단 상태입니다": [
                "차단", "잠금", "로그인", "계정", "cctv", "접속", "차단 상태", "잠금 상태",
                "안됨", "실패", "오류", "로그인 차단", "계정 차단"
            ],
            "비밀번호 변경에 실패했습니다": [
                "비밀번호 변경", "패스워드 변경", "변경", "수정", "업데이트", "비밀번호 수정",
                "실패", "안됨", "오류", "변경 실패", "수정 실패"
            ],
            "PK P 계정 로그인 안됨": [
                "pk p", "PK P", "계정", "로그인", "30일", "미접속", "잠금", "잠겼",
                "안됨", "실패", "오류", "계정 로그인", "pk p 계정"
            ],
            "PK P 웹 접속 안됨": [
                "pk p", "PK P", "웹", "접속", "웹사이트", "톰캣", "tomcat", "서비스",
                "안됨", "실패", "오류", "웹 접속", "페이지", "로드"
            ]
        }
    
    def classify_issue(self, customer_input: str) -> Dict[str, Any]:
        """키워드 기반 문제 유형 분류"""
        try:
            print(f"🔍 분류 시도: {customer_input}")
            
            # 입력 텍스트 정규화
            normalized_input = customer_input.lower().strip()
            
            # 각 문제 유형별로 키워드 매칭 점수 계산
            issue_scores = {}
            
            for issue_type, keywords in self.keyword_mapping.items():
                score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    if keyword.lower() in normalized_input:
                        score += 1
                        matched_keywords.append(keyword)
                
                if score > 0:
                    issue_scores[issue_type] = {
                        'score': score,
                        'matched_keywords': matched_keywords,
                        'confidence': min(score / len(keywords), 1.0)
                    }
            
            # 가장 높은 점수를 받은 문제 유형 선택
            if issue_scores:
                best_issue = max(issue_scores.items(), key=lambda x: x[1]['score'])
                best_issue_type = best_issue[0]
                best_score = best_issue[1]['score']
                best_confidence = best_issue[1]['confidence']
                matched_keywords = best_issue[1]['matched_keywords']
                
                # 신뢰도 결정
                if best_confidence >= 0.3:  # 30% 이상 키워드 매칭
                    confidence_level = 'high' if best_confidence >= 0.5 else 'medium'
                else:
                    confidence_level = 'low'
                
                print(f"✅ 분류 결과: {best_issue_type} (점수: {best_score}, 신뢰도: {confidence_level})")
                print(f"🔑 매칭된 키워드: {matched_keywords}")
                
                return {
                    'issue_type': best_issue_type,
                    'method': 'keyword_based',
                    'confidence': confidence_level,
                    'score': best_score,
                    'matched_keywords': matched_keywords,
                    'all_scores': {k: v['score'] for k, v in issue_scores.items()}
                }
            else:
                print("❌ 매칭되는 키워드가 없음, 기타로 분류")
                return {
                    'issue_type': '기타',
                    'method': 'keyword_based',
                    'confidence': 'low',
                    'score': 0,
                    'matched_keywords': [],
                    'all_scores': {}
                }
                
        except Exception as e:
            print(f"❌ 분류 실패: {e}")
            return {
                'issue_type': '기타',
                'method': 'keyword_based',
                'confidence': 'low',
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """분류기 통계"""
        total_keywords = sum(len(keywords) for keywords in self.keyword_mapping.values())
        return {
            'total_issue_types': len(self.issue_types),
            'total_keywords': total_keywords,
            'issue_types': list(self.keyword_mapping.keys()),
            'method': 'keyword_based'
        }

# 테스트 코드
if __name__ == "__main__":
    # 분류기 초기화
    classifier = SimpleIssueClassifier()
    
    # 테스트 케이스들
    test_cases = [
        "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다. 비밀번호는 정확히 입력했는데도 인증 실패가 발생합니다.",
        "VMS와의 통신에 실패했습니다. VMS 패스워드가 맞지 않는 것 같습니다.",
        "Ping 테스트에 실패했습니다. 네트워크 연결이 안되는 것 같습니다.",
        "Onvif 프로토콜로 카메라와 통신이 안됩니다.",
        "PK P 계정이 30일 미접속으로 잠겼습니다.",
        "웹 접속이 안됩니다",
        "톰캣 서비스가 중단되었습니다"
    ]
    
    print("\n=== 간단한 키워드 기반 문제 유형 분류 테스트 ===")
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"입력: {test_input}")
        
        result = classifier.classify_issue(test_input)
        print(f"분류 결과: {result['issue_type']}")
        print(f"신뢰도: {result['confidence']}")
        print(f"점수: {result['score']}")
        if result['matched_keywords']:
            print(f"매칭된 키워드: {result['matched_keywords']}")
    
    # 통계 출력
    print("\n=== 분류기 통계 ===")
    stats = classifier.get_statistics()
    print(f"문제 유형 수: {stats['total_issue_types']}")
    print(f"총 키워드 수: {stats['total_keywords']}")
    print(f"문제 유형: {stats['issue_types']}")
