import google.generativeai as genai
import os
import streamlit as st
from typing import Dict, Any, Optional
import json
import re
import time

class GeminiHandler:
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-pro"):
        """Gemini 핸들러 초기화"""
        self.model_name = model_name
        self.prompt_template = self._load_prompt_template()
        
        try:
            # API 키 설정 (st.secrets 우선, 파라미터 차선, 환경변수 마지막)
            if api_key:
                self.api_key = api_key
            else:
                try:
                    self.api_key = st.secrets["GEMINI_API_KEY"]
                    print(f"✅ Gemini API 키를 Streamlit Secrets에서 로드했습니다.")
                except:
                    self.api_key = os.getenv("GOOGLE_API_KEY")
                    if self.api_key:
                        print(f"✅ Gemini API 키를 환경변수에서 로드했습니다.")
            
            if not self.api_key:
                print(f"⚠️ Gemini API 키가 설정되지 않았습니다.")
                self.model = None
                return
            
            # API 키 설정
            genai.configure(api_key=self.api_key)
            
            # 모델별 설정
            if "flash" in model_name.lower():
                # Flash 모델은 빠른 응답을 위해 최적화
                self.model = genai.GenerativeModel(
                    model_name,
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
            elif "2.0" in model_name:
                # Gemini 2.0 모델은 더 정교한 설정
                self.model = genai.GenerativeModel(
                    model_name,
                    generation_config={
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "top_k": 50,
                        "max_output_tokens": 4096,
                    }
                )
            else:
                # Gemini 1.5 Pro 기본 설정
                self.model = genai.GenerativeModel(
                    model_name,
                    generation_config={
                        "temperature": 0.1,
                        "top_p": 0.95,
                        "top_k": 60,
                        "max_output_tokens": 8192,
                    }
                )
            
            print(f"✅ Gemini API 초기화 성공 ({model_name})")
            
        except Exception as e:
            print(f"❌ Gemini API 초기화 실패 ({model_name}): {e}")
            self.model = None
    
    def _load_prompt_template(self) -> str:
        """프롬프트 템플릿 로딩"""
        try:
            with open("프롬프트.txt", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            # 개선된 기본 프롬프트 템플릿
            return """[고객 문의 내용]
{customer_input}

[문제 유형]
{issue_type}

[조건 정보]
- 조건 1: {condition_1}
- 조건 2: {condition_2}

[대응안 작성 지침]
아래 형식을 정확히 따라 상세하고 실용적인 응답을 생성하십시오.

[대응유형]
해결안 / 질문 / 출동 중 하나를 선택하십시오.

[응답내용]

요약: {customer_input}에 대한 핵심 내용을 구체적이고 명확하게 정리하십시오. 문제의 원인과 영향 범위를 포함하여 작성하십시오.

조치 흐름: 
1. 첫 번째 조치 단계: 구체적인 조치 내용과 예상 소요 시간
2. 두 번째 조치 단계: 세부적인 실행 방법과 주의사항
3. 세 번째 조치 단계: 검증 방법과 다음 단계 제시
4. 추가 조치가 필요한 경우: 예방 조치나 모니터링 방안

이메일 초안: 
안녕하세요,

{customer_input}에 대한 답변드립니다.

[구체적인 내용을 상세하게 작성하십시오. 고객이 이해하기 쉽도록 기술적 용어는 설명과 함께 사용하십시오.]

추가 문의사항이 있으시면 언제든 연락주시기 바랍니다.

감사합니다.

[예외 처리 기준]
- 조건 정보가 불충분하거나 고객 상태가 불명확한 경우 → "추가 확인이 필요합니다. 다음 질문을 해주세요."라고 안내하십시오.
- 문제가 시나리오 DB에 존재하지 않거나, 적절한 해결책이 없는 경우 → "현장 출동이 필요할 수 있습니다."로 안내하십시오.
- 확실한 답변이 불가능한 경우에도 → "현장 확인 후 조치가 필요합니다" 또는 "엔지니어 출동을 권장합니다" 등으로 마무리하십시오.

**중요: 위 형식을 정확히 따라 응답하십시오. 각 섹션은 반드시 포함되어야 하며, 구체적이고 실용적인 내용으로 작성하십시오.**"""
    
    def build_prompt(self, 
                    customer_input: str,
                    issue_type: str,
                    condition_1: str = "",
                    condition_2: str = "") -> str:
        """프롬프트 조립"""
        if not hasattr(self, 'prompt_template') or not self.prompt_template:
            return self._load_prompt_template()
        
        return self.prompt_template.format(
            customer_input=customer_input,
            issue_type=issue_type,
            condition_1=condition_1,
            condition_2=condition_2
        )
    
    def generate_complete_response(self,
                                 customer_input: str,
                                 issue_type: str,
                                 condition_1: str = "",
                                 condition_2: str = "") -> Dict[str, Any]:
        """완전한 응답 생성 프로세스"""
        try:
            # 프롬프트 조립
            prompt = self.build_prompt(
                customer_input=customer_input,
                issue_type=issue_type,
                condition_1=condition_1,
                condition_2=condition_2
            )
            
            # Gemini API 호출
            api_response = self.generate_response(prompt)
            
            if api_response["success"]:
                # 응답 파싱
                parsed_response = self.parse_response(api_response["response"])
                
                # 파싱 결과 검증
                if not parsed_response or not isinstance(parsed_response, dict):
                    # 파싱 실패 시 기본 응답 사용
                    parsed_response = self._generate_default_response(
                        customer_input, issue_type, condition_1, condition_2
                    )
                
                return {
                    "success": True,
                    "gemini_result": {
                        "api_response": api_response,
                        "parsed_response": parsed_response,
                        "raw_response": api_response["response"],  # 원본 응답 텍스트 포함
                        "prompt_used": prompt
                    }
                }
            else:
                # API 실패 시 기본 응답 생성
                default_response = self._generate_default_response(
                    customer_input, issue_type, condition_1, condition_2
                )
                
                return {
                    "success": False,
                    "error": api_response.get("error", "Gemini API 호출 실패"),
                    "gemini_result": {
                        "api_response": api_response,
                        "parsed_response": default_response,
                        "raw_response": "",  # API 실패 시 빈 문자열
                        "prompt_used": prompt
                    }
                }
                
        except Exception as e:
            print(f"Gemini 응답 생성 중 오류: {e}")
            # 오류 발생 시 기본 응답 생성
            default_response = self._generate_default_response(
                customer_input, issue_type, condition_1, condition_2
            )
            
            return {
                "success": False,
                "error": str(e),
                "gemini_result": {
                    "api_response": {"success": False, "error": str(e)},
                    "parsed_response": default_response,
                    "raw_response": "",  # 오류 발생 시 빈 문자열
                    "prompt_used": ""
                }
            }
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Gemini 응답을 파싱하여 구조화된 데이터로 변환"""
        try:
            # 기본 구조
            parsed = {
                'response_type': '해결안',
                'summary': '',
                'action_flow': '',
                'email_draft': ''
            }
            
            # 응답 유형 추출
            if '질문' in response_text:
                parsed['response_type'] = '질문'
            elif '출동' in response_text:
                parsed['response_type'] = '출동'
            
            # 요약 추출
            summary_match = re.search(r'요약[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n조치|\n이메일|$)', response_text, re.DOTALL)
            if summary_match:
                parsed['summary'] = summary_match.group(1).strip()
            
            # 조치 흐름 추출
            action_match = re.search(r'조치 흐름[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n이메일|$)', response_text, re.DOTALL)
            if action_match:
                parsed['action_flow'] = action_match.group(1).strip()
            
            # 이메일 초안 추출
            email_match = re.search(r'이메일 초안[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|$)', response_text, re.DOTALL)
            if email_match:
                parsed['email_draft'] = email_match.group(1).strip()
            
            # 파싱 실패 시 원본 텍스트 사용
            if not parsed['summary'] and not parsed['action_flow'] and not parsed['email_draft']:
                parsed['summary'] = response_text[:500] + "..." if len(response_text) > 500 else response_text
                parsed['action_flow'] = "응답 파싱에 실패했습니다. 원본 응답을 확인해주세요."
                parsed['email_draft'] = "응답 파싱에 실패했습니다. 원본 응답을 확인해주세요."
            
            return parsed
            
        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            return {
                'response_type': '해결안',
                'summary': response_text[:500] + "..." if len(response_text) > 500 else response_text,
                'action_flow': "응답 파싱에 실패했습니다.",
                'email_draft': "응답 파싱에 실패했습니다."
            }
    
    def _generate_default_response(self,
                                 customer_input: str,
                                 issue_type: str,
                                 condition_1: str = "",
                                 condition_2: str = "") -> Dict[str, Any]:
        """기본 응답 생성 (API 실패 시)"""
        return {
            'response_type': '해결안',
            'summary': f"{customer_input}에 대한 기본적인 대응 방안을 제시합니다.",
            'action_flow': "1. 문제 상황 파악\n2. 기본적인 해결책 제시\n3. 필요시 추가 확인 요청",
            'email_draft': f"고객님께서 문의하신 {customer_input} 내용을 확인했습니다. 현재 상황을 파악하여 적절한 해결책을 제시하겠습니다."
        }
