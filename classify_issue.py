import google.generativeai as genai
import os
import json
import time
from typing import Dict, Any, List

class IssueClassifier:
    def __init__(self, api_key: str = None):
        """문제 유형 분류기 초기화"""
        self.issue_types = [
            "현재 비밀번호가 맞지 않습니다",
            "VMS와의 통신에 실패했습니다", 
            "Ping 테스트에 실패했습니다",
            "Onvif 응답이 없습니다",
            "로그인 차단 상태입니다(CCTV)",
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
            "로그인 차단 상태입니다(CCTV)": {
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
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("✅ Gemini API 초기화 성공 (gemini-1.5-pro)")
        except Exception as e:
            print(f"❌ Gemini API 초기화 실패: {e}")
            self.model = None
    
    def classify_issue(self, customer_input: str) -> Dict[str, Any]:
        """문제 유형 분류 (키워드 우선, Gemini 보조)"""
        
        # 1단계: 키워드 기반 분류 (우선)
        keyword_result = self._classify_by_keywords(customer_input)
        
        # 2단계: Gemini API 분류 (보조, 실패해도 키워드 결과 사용)
        gemini_result = None
        if self.model:
            try:
                gemini_result = self._classify_by_gemini(customer_input)
            except Exception as e:
                print(f"Gemini 분류 실패: {e}")
        
        # 3단계: 결과 결정
        if gemini_result and gemini_result['issue_type'] != keyword_result['issue_type']:
            # Gemini 결과가 키워드 결과와 다르면 Gemini 결과 사용
            final_result = gemini_result
            final_result['method'] = 'gemini_api'
            final_result['confidence'] = 'high'
        else:
            # 키워드 결과 사용
            final_result = keyword_result
            final_result['method'] = 'keyword_based'
            final_result['confidence'] = 'medium'
        
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

# 테스트 코드
if __name__ == "__main__":
    classifier = IssueClassifier()
    
    # 테스트 케이스들
    test_cases = [
        "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다. 비밀번호는 정확히 입력했는데도 인증 실패가 발생합니다.",
        "VMS와의 통신에 실패했습니다. VMS 패스워드가 맞지 않는 것 같습니다.",
        "Ping 테스트에 실패했습니다. 네트워크 연결이 안되는 것 같습니다."
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n=== 테스트 케이스 {i} ===")
        print(f"입력: {test_input}")
        
        result = classifier.classify_issue(test_input)
        print(f"분류 결과: {result['issue_type']}")
        print(f"분류 방법: {result['method']}")
        print(f"신뢰도: {result['confidence']}")
        
        if 'scores' in result:
            print(f"키워드 점수: {result['scores']}") 