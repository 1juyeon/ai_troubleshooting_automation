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

[조치 흐름의 내용을 이메일 본문에 자연스럽게 포함하여 작성하십시오. 구체적인 조치 사항과 단계를 명확하게 제시하십시오. 고객이 이해하기 쉽도록 기술적 용어는 설명과 함께 사용하십시오.]

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
        """Gemini 응답을 파싱하여 구조화된 데이터로 변환 - 간단하고 안정적인 방식"""
        try:
            import re
            
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
            
            # 간단한 섹션별 파싱
            lines = response_text.split('\n')
            current_section = ""
            section_content = {"summary": [], "action": [], "email": []}
            
            for i, line in enumerate(lines):
                line_original = line  # 원본 줄 보존
                line_clean = line.strip()
                
                # 섹션 시작점 감지
                if "요약" in line_clean.lower() and ":" in line_clean:
                    current_section = "summary"
                    # 같은 줄에 내용이 있는 경우
                    if ":" in line_clean:
                        content = line_clean.split(":", 1)[1].strip()
                        if content:
                            section_content["summary"].append(content)
                elif "조치" in line_clean.lower() and "흐름" in line_clean.lower() and ":" in line_clean:
                    current_section = "action"
                    # 같은 줄에 내용이 있는 경우
                    if ":" in line_clean:
                        content = line_clean.split(":", 1)[1].strip()
                        if content:
                            section_content["action"].append(content)
                elif "이메일" in line_clean.lower() and "초안" in line_clean.lower() and ":" in line_clean:
                    current_section = "email"
                    # 같은 줄에 내용이 있는 경우
                    if ":" in line_clean:
                        content = line_clean.split(":", 1)[1].strip()
                        if content:
                            section_content["email"].append(content)
                elif line_clean == "```" and current_section == "email":
                    # 이메일 초안의 ``` 구분자 시작/끝
                    continue
                elif line_clean == "---" and current_section == "email":
                    # 이메일 초안의 --- 구분자 시작/끝
                    continue
                elif "[예외 처리 기준]" in line_clean:
                    # 예외 처리 기준 섹션 시작 - 이메일 섹션 종료
                    if current_section == "email":
                        current_section = ""
                elif current_section == "email" and not line_clean:
                    # 이메일 섹션에서 빈 줄 처리
                    # "감사합니다." 다음의 빈 줄인지 확인
                    if section_content["email"] and "감사합니다" in section_content["email"][-1]:
                        # 감사합니다 다음의 빈 줄이면 이메일 섹션 종료
                        current_section = ""
                    else:
                        # 그 외의 빈 줄은 보존
                        section_content["email"].append("")
                elif current_section and line_clean:
                    # 현재 섹션에 내용 추가 (불필요한 지시사항 제외)
                    if not any(unwanted in line_clean.lower() for unwanted in [
                        "[응답내용]", "[대응유형]", "아래 형식을", "실무자가 이해하기", 
                        "자연스럽고 정확하게", "※ 각 단계는", "짧고 명확하게"
                    ]):
                        if current_section == "email":
                            # 이메일은 원본 줄바꿈 보존
                            section_content["email"].append(line_original.rstrip())
                        else:
                            # 요약과 조치는 정리된 형태로
                            section_content[current_section].append(line_clean)
            
            # 결과 조립
            parsed['summary'] = "\n".join(section_content["summary"]).strip()
            parsed['action_flow'] = "\n".join(section_content["action"]).strip()
            parsed['email_draft'] = "\n".join(section_content["email"]).strip()
            
            # [예외 처리 기준] 이후 내용 제거 (이메일 초안만)
            if '[예외 처리 기준]' in parsed['email_draft']:
                parsed['email_draft'] = parsed['email_draft'].split('[예외 처리 기준]')[0].strip()
            
            # GEMINI 파싱에서는 이미 파싱된 email_draft를 그대로 사용 (재파싱 불필요)
            print(f"Gemini: 파싱된 email_draft 사용 - 길이: {len(parsed['email_draft'])}")
            
            # 빈 값 체크 및 기본값 설정
            if not parsed['summary'] or len(parsed['summary']) < 5:
                parsed['summary'] = "AI 분석 결과를 파싱할 수 없습니다. 고객 문의 내용을 확인해주세요."
            if not parsed['action_flow'] or len(parsed['action_flow']) < 10:
                parsed['action_flow'] = "AI 분석 결과를 파싱할 수 없습니다. 단계별 조치 사항을 확인해주세요."
            if not parsed['email_draft'] or len(parsed['email_draft']) < 20:
                parsed['email_draft'] = "AI 분석 결과를 파싱할 수 없습니다. 이메일 초안을 확인해주세요."
            
            # 디버깅을 위한 로그 추가
            print(f"Gemini 파싱 결과 - 이메일 초안 길이: {len(parsed['email_draft'])}")
            print(f"Gemini 파싱 결과 - 이메일 초안 (처음 200자): {parsed['email_draft'][:200]}")
            print(f"Gemini 파싱 결과 - 이메일 초안 줄바꿈 개수: {parsed['email_draft'].count(chr(10))}")
            print(f"Gemini 파싱 결과 - 이메일 초안 전체 내용:")
            print(repr(parsed['email_draft']))
            
            return parsed
            
        except Exception as e:
            print(f"Gemini 응답 파싱 오류: {e}")
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
    
    def generate_response(self, prompt: str) -> Dict[str, Any]:
        """Gemini API를 호출하여 응답 생성"""
        try:
            if not self.model:
                return {
                    "success": False,
                    "error": "Gemini 모델이 초기화되지 않았습니다.",
                    "response": ""
                }
            
            # API 호출
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return {
                    "success": True,
                    "response": response.text,
                    "model": self.model_name
                }
            else:
                return {
                    "success": False,
                    "error": "Gemini API에서 빈 응답을 받았습니다.",
                    "response": ""
                }
                
        except Exception as e:
            print(f"Gemini API 호출 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": ""
            }
    
    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """응답 파싱 (외부에서 호출 가능한 메서드)"""
        return self._parse_response(response_text)
