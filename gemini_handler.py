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
            
            # 이메일 초안 추출 - GPT 핸들러와 동일한 로직 적용
            email_patterns = [
                # --- 구분자가 있는 경우
                r'이메일\s*초안[:\s]*\n---\n(.*?)\n---',
                # [예외 처리 기준] 전까지
                r'이메일\s*초안[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\[예외\s*처리\s*기준\])',
                # 기존 패턴들
                r'이메일\s*초안[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*$)',
                r'이메일\s*초안[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:$))',
                r'이메일\s*초안[:\s]*([^\n]+)'
            ]
            
            for pattern in email_patterns:
                email_match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if email_match:
                    email_text = email_match.group(1)
                    # 앞뒤 공백만 제거하고 줄바꿈은 보존
                    email_text = email_text.strip('\n\r\t ')
                    
                    # 불필요한 텍스트 제거 (줄바꿈 보존)
                    email_lines = []
                    for line in email_text.split('\n'):
                        line_stripped = line.strip()
                        if line_stripped and not any(unwanted in line_stripped.lower() for unwanted in [
                            "[응답내용]", "[대응유형]", "요약:", "조치 흐름:", "이메일 초안:",
                            "아래 형식을 참고하여", "실무자가 이해하기 쉽도록", "자연스럽고 정확하게 응답을 생성하십시오",
                            "---", "[예외 처리 기준]"
                        ]):
                            # 원본 줄의 공백 구조를 최대한 보존
                            email_lines.append(line.rstrip())
                        elif not line_stripped:
                            # 빈 줄도 보존 (이메일 형식 유지)
                            email_lines.append("")
                    
                    parsed['email_draft'] = '\n'.join(email_lines)
                    
                    # [예외 처리 기준] 이후의 모든 내용 제거 (줄바꿈 보존)
                    if '[예외 처리 기준]' in parsed['email_draft']:
                        parsed['email_draft'] = parsed['email_draft'].split('[예외 처리 기준]')[0].strip('\n\r\t ')
                    
                    if parsed['email_draft'] and len(parsed['email_draft']) > 20:  # 의미있는 길이인지 확인
                        break
            
            # 정규식 파싱이 실패한 경우 더 강력한 폴백 로직
            if not parsed['summary'] or not parsed['action_flow'] or not parsed['email_draft']:
                # 줄별 파싱으로 보완
                lines = response_text.split('\n')
                current_section = ""
                section_content = {"summary": [], "action": [], "email": []}
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 섹션 시작점 감지 (더 유연하게)
                    line_lower = line.lower()
                    if "요약" in line_lower and ":" in line:
                        current_section = "summary"
                        # 요약 내용이 같은 줄에 있는 경우
                        summary_content = line.split(":", 1)[1].strip() if ":" in line else ""
                        if summary_content and len(summary_content) > 5:
                            parsed['summary'] = summary_content
                    elif "조치" in line_lower and "흐름" in line_lower and ":" in line:
                        current_section = "action"
                        # 조치 흐름 내용이 같은 줄에 있는 경우
                        action_content = line.split(":", 1)[1].strip() if ":" in line else ""
                        if action_content and len(action_content) > 5:
                            parsed['action_flow'] = action_content + "\n"
                    elif "이메일" in line_lower and "초안" in line_lower and ":" in line:
                        current_section = "email"
                        # 이메일 초안 내용이 같은 줄에 있는 경우
                        email_content = line.split(":", 1)[1].strip() if ":" in line else ""
                        if email_content and len(email_content) > 10:
                            parsed['email_draft'] = email_content + "\n"
                    elif line.strip() == "---" and current_section == "email":
                        # 이메일 초안의 --- 구분자 시작
                        continue
                    else:
                        # 현재 섹션에 내용 추가
                        if current_section == "summary" and not parsed['summary']:
                            if len(line) > 5 and not any(keyword in line.lower() for keyword in ["조치", "이메일", "[응답내용]", "[대응유형]"]):
                                parsed['summary'] = line
                        elif current_section == "action" and not parsed['action_flow']:
                            if len(line) > 5 and not any(instruction in line.lower() for instruction in [
                                "아래 형식을 따라", "단계별로 줄바꿈하며", "번호를 붙여 설명하십시오",
                                "각 단계는 짧고 명확하게", "실무자가 바로 이해할 수 있도록",
                                "※ 각 단계는", "짧고 명확하게", "실무자가 바로 이해할 수 있도록 작성하십시오",
                                "[응답내용]", "[대응유형]", "요약:", "조치 흐름:", "이메일 초안:"
                            ]):
                                if re.match(r'^\d+\.', line) or (line and not line.startswith('-')):
                                    parsed['action_flow'] = line + "\n"
                        elif current_section == "email":
                            # 이메일 섹션 종료 조건 확인
                            if line.strip() == "---" or "[예외 처리 기준]" in line:
                                current_section = ""
                                continue
                            
                            if len(line) > 5 and not any(unwanted in line.lower() for unwanted in [
                                "[응답내용]", "[대응유형]", "요약:", "조치 흐름:", "이메일 초안:",
                                "아래 형식을 참고하여", "실무자가 이해하기 쉽도록", "자연스럽고 정확하게 응답을 생성하십시오",
                                "---", "[예외 처리 기준]"
                            ]):
                                if parsed['email_draft']:
                                    parsed['email_draft'] += line + "\n"
                                else:
                                    parsed['email_draft'] = line + "\n"
            
            # 줄바꿈 정리 (이메일 초안은 줄바꿈 보존)
            parsed['action_flow'] = parsed['action_flow'].strip()
            # 이메일 초안은 앞뒤 공백만 제거하고 줄바꿈은 보존
            parsed['email_draft'] = parsed['email_draft'].strip('\n\r\t ')
            
            # [예외 처리 기준] 이후의 모든 내용 제거 (폴백 로직에서도, 줄바꿈 보존)
            if '[예외 처리 기준]' in parsed['email_draft']:
                parsed['email_draft'] = parsed['email_draft'].split('[예외 처리 기준]')[0].strip('\n\r\t ')
            
            # 빈 값 체크 및 기본값 설정 (더 엄격하게)
            if not parsed['summary'] or len(parsed['summary'].strip()) < 5:
                parsed['summary'] = "AI 분석 결과를 파싱할 수 없습니다. 고객 문의 내용을 확인해주세요."
            if not parsed['action_flow'] or len(parsed['action_flow'].strip()) < 10:
                parsed['action_flow'] = "AI 분석 결과를 파싱할 수 없습니다. 단계별 조치 사항을 확인해주세요."
            if not parsed['email_draft'] or len(parsed['email_draft'].strip()) < 20:
                parsed['email_draft'] = "AI 분석 결과를 파싱할 수 없습니다. 이메일 초안을 확인해주세요."
            
            # 디버깅을 위한 로그 추가
            print(f"Gemini 파싱 결과 - 이메일 초안 길이: {len(parsed['email_draft'])}")
            print(f"Gemini 파싱 결과 - 이메일 초안 (처음 200자): {parsed['email_draft'][:200]}")
            print(f"Gemini 파싱 결과 - 이메일 초안 줄바꿈 개수: {parsed['email_draft'].count(chr(10))}")
            print(f"Gemini 원본 응답에서 이메일 초안 부분:")
            email_start = response_text.find("이메일 초안")
            if email_start != -1:
                email_part = response_text[email_start:email_start+500]
                print(email_part)
            
            # 정규식 패턴별 매칭 결과 확인
            print("=== 정규식 패턴 매칭 결과 ===")
            for i, pattern in enumerate(email_patterns):
                match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if match:
                    print(f"패턴 {i+1} 매칭됨: {pattern}")
                    print(f"매칭된 텍스트 길이: {len(match.group(1))}")
                    print(f"매칭된 텍스트 (처음 100자): {match.group(1)[:100]}")
                    print(f"매칭된 텍스트 전체:")
                    print(match.group(1))
                    break
            else:
                print("어떤 패턴도 매칭되지 않음")
            
            # 최종 파싱 결과 상세 출력
            print("=== 최종 파싱 결과 ===")
            print(f"이메일 초안 전체 내용:")
            print(repr(parsed['email_draft']))  # repr을 사용하여 줄바꿈 문자도 확인
            
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
