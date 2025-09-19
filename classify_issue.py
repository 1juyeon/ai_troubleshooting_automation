import google.generativeai as genai
import os
import json
import time
from typing import Dict, Any, List

# 벡터 분류기는 안전하게 임포트 (의존성 문제 시 fallback)
try:
    from chroma_vector_classifier import ChromaVectorClassifier
    VECTOR_CLASSIFIER_AVAILABLE = True
    pass
except ImportError as e:
    VECTOR_CLASSIFIER_AVAILABLE = False
    ChromaVectorClassifier = None
except Exception as e:
    VECTOR_CLASSIFIER_AVAILABLE = False
    ChromaVectorClassifier = None

class IssueClassifier:
    def __init__(self, api_key: str = None):
        """문제 유형 분류기 초기화"""
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
        
        # 키워드 기반 분류를 위한 가중치 키워드
        self.keyword_weights = {
            "현재 비밀번호가 맞지 않습니다": {
                "high": ["비밀번호", "패스워드", "인증 실패", "로그인 실패", "접속 실패", "인증 오류", "CCTV 웹 접속"],
                "medium": ["CCTV", "웹 접속", "웹 로그인", "인증", "로그인", "접속"],
                "low": ["실패", "오류", "문제", "안됨", "안되다"]
            },
            "VMS와의 통신에 실패했습니다": {
                "high": ["VMS", "SVMS", "통신 실패", "연결 실패", "NVR", "VMS 패스워드"],
                "medium": ["통신", "연결", "패스워드", "비밀번호", "설정"],
                "low": ["실패", "오류", "문제", "안됨", "안되다"]
            },
            "Ping 테스트에 실패했습니다": {
                "high": ["Ping", "ping", "네트워크", "연결", "통신"],
                "medium": ["테스트", "확인", "점검", "상태"],
                "low": ["실패", "오류", "문제", "안됨", "안되다"]
            },
            "Onvif 응답이 없습니다": {
                "high": ["Onvif", "onvif", "프로토콜", "응답 없음", "카메라 통신"],
                "medium": ["프로토콜", "HTTP", "HTTPS", "통신", "연결"],
                "low": ["실패", "오류", "문제", "안됨", "안되다"]
            },
            "로그인 차단 상태입니다": {
                "high": ["로그인 차단", "차단 상태", "CCTV 차단", "비밀번호 변경"],
                "medium": ["로그인", "차단", "CCTV", "비밀번호", "패스워드"],
                "low": ["상태", "문제", "안됨", "안되다"]
            },
            "비밀번호 변경에 실패했습니다": {
                "high": ["비밀번호 변경", "패스워드 변경", "변경 실패"],
                "medium": ["비밀번호", "패스워드", "변경", "수정"],
                "low": ["실패", "오류", "문제", "안됨", "안되다"]
            },
            "PK P 계정 로그인 안됨": {
                "high": ["PK P 계정", "계정 로그인", "계정 잠김", "30일 미접속"],
                "medium": ["PK P", "계정", "로그인", "접속", "비밀번호"],
                "low": ["안됨", "실패", "오류", "문제"]
            },
            "PK P 웹 접속 안됨": {
                "high": ["PK P 웹", "웹 접속", "톰캣", "서비스"],
                "medium": ["PK P", "웹", "접속", "톰캣", "서비스"],
                "low": ["안됨", "실패", "오류", "문제"]
            },
            "기타": {
                "high": ["기타", "기타 문제", "알 수 없음"],
                "medium": ["문제", "오류", "실패"],
                "low": ["기타", "기타"]
            }
        }
        
        # Gemini API 초기화 (실패해도 키워드 분류는 작동)
        try:
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            else:
                self.model = None
        except Exception as e:
            self.model = None
        
        # 벡터 분류기 초기화 (안전하게)
        self.vector_classifier = None
        if VECTOR_CLASSIFIER_AVAILABLE and ChromaVectorClassifier is not None:
            try:
                self.vector_classifier = ChromaVectorClassifier()
            except Exception as e:
                self.vector_classifier = None
        else:
            pass
    
    def classify_issue(self, customer_input: str) -> Dict[str, Any]:
        """문제 유형 분류 (하이브리드: 벡터 + 키워드 + Gemini)"""
        
        # 1단계: 벡터 기반 분류 (최우선)
        vector_result = None
        if self.vector_classifier:
            try:
                vector_result = self.vector_classifier.classify_issue(customer_input)
                print(f"벡터 분류 결과: {vector_result['issue_type']} (신뢰도: {vector_result['confidence']})")
            except Exception as e:
                print(f"벡터 분류 실패: {e}")
        
        # 2단계: 키워드 기반 분류
        keyword_result = self._classify_by_keywords(customer_input)
        print(f"키워드 분류 결과: {keyword_result['issue_type']}")
        
        # 3단계: Gemini API 분류 (보조)
        gemini_result = None
        if self.model:
            try:
                gemini_result = self._classify_by_gemini(customer_input)
                print(f"Gemini 분류 결과: {gemini_result['issue_type']}")
            except Exception as e:
                print(f"Gemini 분류 실패: {e}")
        
        # 4단계: 하이브리드 결과 결정
        final_result = self._decide_hybrid_result(vector_result, keyword_result, gemini_result)
        
        return final_result
    
    def _decide_hybrid_result(self, vector_result: Dict[str, Any], keyword_result: Dict[str, Any], gemini_result: Dict[str, Any]) -> Dict[str, Any]:
        """하이브리드 분류 결과 결정"""
        
        # 벡터 분류 결과가 있고 신뢰도가 높은 경우
        if vector_result and vector_result.get('confidence') == 'high' and vector_result.get('similarity_score', 0) >= 0.8:
            final_result = vector_result.copy()
            final_result['method'] = 'vector_based'
            final_result['confidence'] = 'high'
            final_result['hybrid_info'] = {
                'vector_score': vector_result.get('similarity_score', 0),
                'keyword_score': keyword_result.get('scores', {}).get(vector_result['issue_type'], 0),
                'gemini_match': gemini_result['issue_type'] == vector_result['issue_type'] if gemini_result else None
            }
            return final_result
        
        # 벡터 분류 결과가 있고 중간 신뢰도인 경우
        if vector_result and vector_result.get('confidence') == 'medium' and vector_result.get('similarity_score', 0) >= 0.6:
            # 키워드 결과와 일치하는지 확인
            if keyword_result['issue_type'] == vector_result['issue_type']:
                final_result = vector_result.copy()
                final_result['method'] = 'vector_keyword_hybrid'
                final_result['confidence'] = 'high'
                final_result['hybrid_info'] = {
                    'vector_score': vector_result.get('similarity_score', 0),
                    'keyword_score': keyword_result.get('scores', {}).get(vector_result['issue_type'], 0),
                    'gemini_match': gemini_result['issue_type'] == vector_result['issue_type'] if gemini_result else None
                }
                return final_result
        
        # Gemini 결과가 있고 키워드 결과와 일치하는 경우
        if gemini_result and keyword_result['issue_type'] == gemini_result['issue_type']:
            final_result = gemini_result.copy()
            final_result['method'] = 'gemini_keyword_hybrid'
            final_result['confidence'] = 'high'
            final_result['hybrid_info'] = {
                'vector_score': vector_result.get('similarity_score', 0) if vector_result else 0,
                'keyword_score': keyword_result.get('scores', {}).get(gemini_result['issue_type'], 0),
                'gemini_match': True
            }
            return final_result
        
        # 벡터 분류 결과가 있는 경우 (낮은 신뢰도라도)
        if vector_result and vector_result.get('similarity_score', 0) >= 0.4:
            final_result = vector_result.copy()
            final_result['method'] = 'vector_based'
            final_result['confidence'] = 'medium'
            final_result['hybrid_info'] = {
                'vector_score': vector_result.get('similarity_score', 0),
                'keyword_score': keyword_result.get('scores', {}).get(vector_result['issue_type'], 0),
                'gemini_match': gemini_result['issue_type'] == vector_result['issue_type'] if gemini_result else None
            }
            return final_result
        
        # Gemini 결과가 있는 경우
        if gemini_result:
            final_result = gemini_result.copy()
            final_result['method'] = 'gemini_api'
            final_result['confidence'] = 'medium'
            final_result['hybrid_info'] = {
                'vector_score': vector_result.get('similarity_score', 0) if vector_result else 0,
                'keyword_score': keyword_result.get('scores', {}).get(gemini_result['issue_type'], 0),
                'gemini_match': True
            }
            return final_result
        
        # 키워드 결과 사용 (최후)
        final_result = keyword_result.copy()
        final_result['method'] = 'keyword_based'
        final_result['confidence'] = 'medium'
        final_result['hybrid_info'] = {
            'vector_score': vector_result.get('similarity_score', 0) if vector_result else 0,
            'keyword_score': keyword_result.get('scores', {}).get(keyword_result['issue_type'], 0),
            'gemini_match': gemini_result['issue_type'] == keyword_result['issue_type'] if gemini_result else None
        }
        return final_result
    
    def _classify_by_keywords(self, customer_input: str) -> Dict[str, Any]:
        """키워드 기반 문제 유형 분류"""
        scores = {}
        
        for issue_type, keywords in self.keyword_weights.items():
            score = 0
            input_lower = customer_input.lower()
            
            # 고가중치 키워드 (3점)
            for keyword in keywords['high']:
                if keyword.lower() in input_lower:
                    score += 3
            
            # 중가중치 키워드 (2점)
            for keyword in keywords['medium']:
                if keyword.lower() in input_lower:
                    score += 2
            
            # 저가중치 키워드 (1점)
            for keyword in keywords['low']:
                if keyword.lower() in input_lower:
                    score += 1
            
            scores[issue_type] = score
        
        # 가장 높은 점수의 문제 유형 선택
        best_issue_type = max(scores, key=scores.get)
        
        return {
            'issue_type': best_issue_type,
            'scores': scores,
            'method': 'keyword_based',
            'confidence': 'medium'
        }
    
    def _classify_by_gemini(self, customer_input: str) -> Dict[str, Any]:
        """Gemini API를 사용한 문제 유형 분류"""
        if not self.model:
            raise Exception("Gemini 모델이 초기화되지 않았습니다.")
        
        # 간단한 프롬프트 사용
        prompt = f"다음 문의를 분석하여 문제 유형을 선택하세요: {customer_input}\n\n선택지: {', '.join(self.issue_types)}"
        
        start_time = time.time()
        
        try:
            # 타임아웃 설정 (5초)
            response = self.model.generate_content(prompt)
            
            elapsed_time = time.time() - start_time
            
            # 타임아웃 체크
            if elapsed_time > 5:
                print(f"Gemini 분류 타임아웃 ({elapsed_time:.2f}초)")
                raise Exception("API 응답 시간 초과")
            
            # 응답에서 문제 유형 추출
            response_text = response.text.strip()
            
            # 가장 유사한 문제 유형 찾기
            best_match = None
            best_score = 0
            
            for issue_type in self.issue_types:
                # 부분 문자열 매칭
                if issue_type.lower() in response_text.lower():
                    score = len(issue_type) / len(response_text)
                    if score > best_score:
                        best_score = score
                        best_match = issue_type
            
            if best_match:
                return {
                    'issue_type': best_match,
                    'method': 'gemini_api',
                    'confidence': 'high',
                    'response_time': elapsed_time
                }
            else:
                # 매칭되지 않으면 키워드 분류 결과 사용
                return self._classify_by_keywords(customer_input)
                
        except Exception as e:
            print(f"Gemini 분류 실패: {e}")
            # 키워드 분류 결과 사용
            return self._classify_by_keywords(customer_input)
    
    def add_training_data(self, customer_input: str, issue_type: str, metadata: Dict[str, Any] = None):
        """벡터 분류기에 학습 데이터 추가"""
        if self.vector_classifier:
            return self.vector_classifier.add_training_data(customer_input, issue_type, metadata)
        return False
    
    def get_vector_statistics(self) -> Dict[str, Any]:
        """벡터 DB 통계 조회"""
        if self.vector_classifier:
            return self.vector_classifier.get_statistics()
        return {
            'total_documents': 0,
            'issue_types': [],
            'collection_name': 'issue_classification',
            'error': '벡터 분류기가 초기화되지 않았습니다.'
        }

# 테스트 코드
if __name__ == "__main__":
    print("=== 문제 유형 분류기 초기화 ===")
    classifier = IssueClassifier()
    print("초기화 완료\n")
    
    # 테스트 케이스들
    test_cases = [
        "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다. 비밀번호는 정확히 입력했는데도 인증 실패가 발생합니다.",
        "VMS와의 통신에 실패했습니다. VMS 패스워드가 맞지 않는 것 같습니다.",
        "Ping 테스트에 실패했습니다. 네트워크 연결이 안되는 것 같습니다.",
        "Onvif 프로토콜로 카메라와 통신이 안됩니다.",
        "PK P 계정이 30일 미접속으로 잠겼습니다.",
        "비밀번호 변경이 제대로 되지 않습니다."
    ]
    
    print("\n=== 하이브리드 분류 시스템 테스트 ===")
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"입력: {test_input}")
        
        result = classifier.classify_issue(test_input)
        print(f"최종 분류 결과: {result['issue_type']}")
        print(f"분류 방법: {result['method']}")
        print(f"신뢰도: {result['confidence']}")
        
        if 'hybrid_info' in result:
            print(f"하이브리드 정보:")
            print(f"  - 벡터 점수: {result['hybrid_info']['vector_score']:.3f}")
            print(f"  - 키워드 점수: {result['hybrid_info']['keyword_score']}")
            print(f"  - Gemini 일치: {result['hybrid_info']['gemini_match']}")
        
        if 'scores' in result:
            print(f"키워드 점수: {result['scores']}")
    
    # 벡터 DB 통계 출력
    print("\n=== 벡터 DB 통계 ===")
    stats = classifier.get_vector_statistics()
    print(f"총 문서 수: {stats['total_documents']}")
    print(f"문제 유형: {stats['issue_types']}")
    if 'issue_type_counts' in stats:
        print("문제 유형별 문서 수:")
        for issue_type, count in stats['issue_type_counts'].items():
            print(f"  - {issue_type}: {count}개") 