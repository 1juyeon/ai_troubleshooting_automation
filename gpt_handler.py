import google.generativeai as genai
import os
import streamlit as st
from typing import Dict, Any, Optional
import json
import re # Added for regex in parse_response

class GPTHandler:
    def __init__(self, api_key: str = None):
        """Gemini 핸들러 초기화"""
        # 프롬프트 템플릿 로딩 (API 키와 관계없이 항상 로드)
        self.prompt_template = self._load_prompt_template()
        
        try:
            # API 키 설정 (st.secrets 우선, 파라미터 차선, 환경변수 마지막)
            if api_key:
                self.api_key = api_key
            else:
                # st.secrets에서 먼저 시도
                try:
                    self.api_key = st.secrets["GEMINI_API_KEY"]
                    print("✅ Gemini API 키를 Streamlit Secrets에서 로드했습니다.")
                except:
                    # 환경변수로 폴백
                    self.api_key = os.getenv("GOOGLE_API_KEY")
                    if self.api_key:
                        print("✅ Gemini API 키를 환경변수에서 로드했습니다.")
            
            if not self.api_key:
                print("⚠️ Gemini API 키가 설정되지 않았습니다.")
                print("Streamlit Cloud Secrets 또는 환경변수 GOOGLE_API_KEY를 설정해주세요.")
                self.model = None
                return
            
            # API 키 방식으로 설정
            genai.configure(api_key=self.api_key)
            # gemini-1.5-pro 모델 사용
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
            print("✅ Gemini API 초기화 성공 (gemini-1.5-pro)")
            
        except Exception as e:
            print(f"❌ Gemini API 초기화 실패: {e}")
            self.model = None
        
    def _load_prompt_template(self) -> str:
        """프롬프트 템플릿 로딩"""
        try:
            with open("프롬프트.txt", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            # 기본 프롬프트 템플릿 (프롬프트.txt와 동일)
            return """[고객 문의 내용]
{customer_input}

[문제 유형]
{issue_type}

[조건 정보]
- 조건 1: {condition_1}
- 조건 2: {condition_2}

[대응안 작성 지침]
아래 형식을 정확히 따라 응답을 생성하십시오.

[대응유형]
해결안 / 질문 / 출동 중 하나를 선택하십시오.

[응답내용]

요약: {customer_input}에 대한 핵심 내용을 간결하게 정리하십시오.

조치 흐름: 
1. 첫 번째 조치 단계
2. 두 번째 조치 단계  
3. 세 번째 조치 단계

이메일 초안: 
안녕하세요, [고객님 성함]님.

{customer_input}에 대한 답변드립니다.

문제를 해결하기 위해 아래의 단계를 따라주시기를 부탁드립니다:

1. [조치 흐름의 첫 번째 단계를 여기에 작성]
2. [조치 흐름의 두 번째 단계를 여기에 작성]  
3. [조치 흐름의 세 번째 단계를 여기에 작성]

위의 방법으로 문제가 해결되지 않는다면, 추가적인 지원이 필요할 수 있습니다. 언제든지 문의해 주세요.

감사합니다.
[고객지원팀 이름]

[예외 처리 기준]
- 조건 정보가 불충분하거나 고객 상태가 불명확한 경우 → "추가 확인이 필요합니다. 다음 질문을 해주세요."라고 안내하십시오.
- 문제가 시나리오 DB에 존재하지 않거나, 적절한 해결책이 없는 경우 → "현장 출동이 필요할 수 있습니다."로 안내하십시오.
- 확실한 답변이 불가능한 경우에도 → "현장 확인 후 조치가 필요합니다" 또는 "엔지니어 출동을 권장합니다" 등으로 마무리하십시오.

**중요: 위 형식을 정확히 따라 응답하십시오. 각 섹션은 반드시 포함되어야 합니다.**"""
    
    def build_prompt(self, 
                    customer_input: str,
                    issue_type: str,
                    condition_1: str = "",
                    condition_2: str = "") -> str:
        """프롬프트 조립"""
        if not hasattr(self, 'prompt_template') or not self.prompt_template:
            # 기본 프롬프트 템플릿 사용
            prompt_template = """[고객 문의 내용]
{customer_input}

[문제 유형]
{issue_type}

[조건 정보]
- 조건 1: {condition_1}
- 조건 2: {condition_2}

[대응안 작성 지침]
아래 형식을 정확히 따라 응답을 생성하십시오.

[대응유형]
해결안 / 질문 / 출동 중 하나를 선택하십시오.

[응답내용]

요약: {customer_input}에 대한 핵심 내용을 간결하게 정리하십시오.

조치 흐름: 
1. 첫 번째 조치 단계
2. 두 번째 조치 단계  
3. 세 번째 조치 단계

이메일 초안: 
안녕하세요, [고객님 성함]님.

{customer_input}에 대한 답변드립니다.

문제를 해결하기 위해 아래의 단계를 따라주시기를 부탁드립니다:

1. [조치 흐름의 첫 번째 단계를 여기에 작성]
2. [조치 흐름의 두 번째 단계를 여기에 작성]  
3. [조치 흐름의 세 번째 단계를 여기에 작성]

위의 방법으로 문제가 해결되지 않는다면, 추가적인 지원이 필요할 수 있습니다. 언제든지 문의해 주세요.

감사합니다.
[고객지원팀 이름]

[예외 처리 기준]
- 조건 정보가 불충분하거나 고객 상태가 불명확한 경우 → "추가 확인이 필요합니다. 다음 질문을 해주세요."라고 안내하십시오.
- 문제가 시나리오 DB에 존재하지 않거나, 적절한 해결책이 없는 경우 → "현장 출동이 필요할 수 있습니다."로 안내하십시오.
- 확실한 답변이 불가능한 경우에도 → "현장 확인 후 조치가 필요합니다" 또는 "엔지니어 출동을 권장합니다" 등으로 마무리하십시오."""
        else:
            prompt_template = self.prompt_template
            
        prompt = prompt_template.format(
            customer_input=customer_input,
            issue_type=issue_type,
            condition_1=condition_1,
            condition_2=condition_2
        )
        return prompt
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Gemini API를 사용한 응답 생성"""
        if not self.model:
            return {
                "success": False,
                "error": "Gemini API가 초기화되지 않았습니다.",
                "response": "죄송합니다. AI 서비스에 연결할 수 없습니다. 수동으로 대응해주세요.",
                "model": "gemini-1.5-pro"
            }
        
        try:
            import time
            start_time = time.time()
            
            # 더 간단한 API 호출 방식 사용
            response = self.model.generate_content(prompt)
            
            elapsed_time = time.time() - start_time
            
            # 응답 검증
            if not response or not response.text:
                return {
                    "success": False,
                    "error": "API 응답이 비어있습니다",
                    "response": "죄송합니다. AI 응답이 비어있어 기본 응답을 제공합니다.",
                    "model": "gemini-1.5-pro",
                    "response_time": elapsed_time
                }
            
            # 응답 길이 검증
            response_text = response.text.strip()
            if len(response_text) < 50:  # 너무 짧은 응답은 의심스러움
                return {
                    "success": False,
                    "error": "API 응답이 너무 짧습니다",
                    "response": "죄송합니다. AI 응답이 너무 짧아 기본 응답을 제공합니다.",
                    "model": "gemini-1.5-pro",
                    "response_time": elapsed_time
                }
            
            # 타임아웃 체크
            if elapsed_time > 15:
                return {
                    "success": False,
                    "error": "API 응답 시간 초과",
                    "response": "죄송합니다. 응답 생성에 시간이 오래 걸려 기본 응답을 제공합니다.",
                    "model": "gemini-1.5-pro",
                    "response_time": elapsed_time
                }
            
            return {
                "success": True,
                "response": response_text,
                "model": "gemini-1.5-pro",
                "tokens_used": len(response_text.split()),  # 대략적인 토큰 수
                "response_time": elapsed_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요.",
                "model": "gemini-1.5-pro"
            }
    
    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """응답 텍스트를 구조화된 형태로 파싱"""
        try:
            # 기본값 설정
            response_type = "해결안"
            summary = ""
            action_flow = ""
            email_draft = ""
            
            # 응답 유형 결정 (더 정확하게)
            response_text_lower = response_text.lower()
            if "질문" in response_text_lower and "출동" not in response_text_lower:
                response_type = "질문"
            elif "출동" in response_text_lower and "질문" not in response_text_lower:
                response_type = "출동"
            elif "해결안" in response_text_lower:
                response_type = "해결안"
            
            # 정규식을 사용한 더 정확한 파싱
            import re
            
            # 요약 추출 - "요약:" 다음에 오는 텍스트 (더 유연하게)
            summary_patterns = [
                r'요약[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:조치\s*흐름|이메일\s*초안|$))',
                r'요약[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:조치|이메일|$))',
                r'요약[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*$)',
                r'요약[:\s]*([^\n]+)'
            ]
            
            for pattern in summary_patterns:
                summary_match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if summary_match:
                    summary = summary_match.group(1).strip()
                    # 불필요한 텍스트 제거
                    summary = re.sub(r'아래\s*형식을\s*참고하여|실무자가\s*이해하기\s*쉽도록|자연스럽고\s*정확하게\s*응답을\s*생성하십시오', '', summary, flags=re.IGNORECASE).strip()
                    if summary and len(summary) > 5:  # 의미있는 길이인지 확인
                        break
            
            # 조치 흐름 추출 - "조치 흐름:" 다음에 오는 텍스트
            action_patterns = [
                r'조치\s*흐름[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:이메일\s*초안|$))',
                r'조치\s*흐름[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*$)',
                r'조치\s*흐름[:\s]*([^\n]+)'
            ]
            
            for pattern in action_patterns:
                action_match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if action_match:
                    action_text = action_match.group(1).strip()
                    # 줄별로 처리하여 번호가 있는 항목만 추출
                    action_lines = []
                    for line in action_text.split('\n'):
                        line = line.strip()
                        if line and not any(unwanted in line.lower() for unwanted in [
                            "아래 형식을 따라", "단계별로 줄바꿈하며", "번호를 붙여 설명하십시오",
                            "각 단계는 짧고 명확하게", "실무자가 바로 이해할 수 있도록",
                            "※ 각 단계는", "짧고 명확하게", "실무자가 바로 이해할 수 있도록 작성하십시오",
                            "[응답내용]", "[대응유형]", "요약:", "조치 흐름:", "이메일 초안:"
                        ]):
                            if re.match(r'^\d+\.', line) or (line and not line.startswith('-')):
                                action_lines.append(line)
                    action_flow = '\n'.join(action_lines)
                    if action_flow and len(action_flow) > 10:  # 의미있는 길이인지 확인
                        break
            
            # 이메일 초안 추출 - "이메일 초안:" 다음에 오는 텍스트
            email_patterns = [
                r'이메일\s*초안[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*$)',
                r'이메일\s*초안[:\s]*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:$))',
                r'이메일\s*초안[:\s]*([^\n]+)'
            ]
            
            for pattern in email_patterns:
                email_match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if email_match:
                    email_text = email_match.group(1).strip()
                    # 불필요한 텍스트 제거
                    email_lines = []
                    for line in email_text.split('\n'):
                        line = line.strip()
                        if line and not any(unwanted in line.lower() for unwanted in [
                            "[응답내용]", "[대응유형]", "요약:", "조치 흐름:", "이메일 초안:",
                            "아래 형식을 참고하여", "실무자가 이해하기 쉽도록", "자연스럽고 정확하게 응답을 생성하십시오"
                        ]):
                            email_lines.append(line)
                    email_draft = '\n'.join(email_lines)
                    if email_draft and len(email_draft) > 20:  # 의미있는 길이인지 확인
                        break
            
            # 정규식 파싱이 실패한 경우 더 강력한 폴백 로직
            if not summary or not action_flow or not email_draft:
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
                            summary = summary_content
                    elif "조치" in line_lower and "흐름" in line_lower and ":" in line:
                        current_section = "action"
                        # 조치 흐름 내용이 같은 줄에 있는 경우
                        action_content = line.split(":", 1)[1].strip() if ":" in line else ""
                        if action_content and len(action_content) > 5:
                            action_flow = action_content + "\n"
                    elif "이메일" in line_lower and "초안" in line_lower and ":" in line:
                        current_section = "email"
                        # 이메일 초안 내용이 같은 줄에 있는 경우
                        email_content = line.split(":", 1)[1].strip() if ":" in line else ""
                        if email_content and len(email_content) > 10:
                            email_draft = email_content + "\n"
                    else:
                        # 현재 섹션에 내용 추가
                        if current_section == "summary" and not summary:
                            if len(line) > 5 and not any(keyword in line.lower() for keyword in ["조치", "이메일", "[응답내용]", "[대응유형]"]):
                                summary = line
                        elif current_section == "action" and not action_flow:
                            if len(line) > 5 and not any(instruction in line.lower() for instruction in [
                                "아래 형식을 따라", "단계별로 줄바꿈하며", "번호를 붙여 설명하십시오",
                                "각 단계는 짧고 명확하게", "실무자가 바로 이해할 수 있도록",
                                "※ 각 단계는", "짧고 명확하게", "실무자가 바로 이해할 수 있도록 작성하십시오",
                                "[응답내용]", "[대응유형]", "요약:", "조치 흐름:", "이메일 초안:"
                            ]):
                                if re.match(r'^\d+\.', line) or (line and not line.startswith('-')):
                                    action_flow = line + "\n"
                        elif current_section == "email" and not email_draft:
                            if len(line) > 5 and not any(unwanted in line.lower() for unwanted in [
                                "[응답내용]", "[대응유형]", "요약:", "조치 흐름:", "이메일 초안:",
                                "아래 형식을 참고하여", "실무자가 이해하기 쉽도록", "자연스럽고 정확하게 응답을 생성하십시오"
                            ]):
                                email_draft = line + "\n"
            
            # 줄바꿈 정리
            action_flow = action_flow.strip()
            email_draft = email_draft.strip()
            
            # 빈 값 체크 및 기본값 설정 (더 엄격하게)
            if not summary or len(summary.strip()) < 5:
                summary = "AI 분석 결과를 파싱할 수 없습니다. 고객 문의 내용을 확인해주세요."
            if not action_flow or len(action_flow.strip()) < 10:
                action_flow = "AI 분석 결과를 파싱할 수 없습니다. 단계별 조치 사항을 확인해주세요."
            if not email_draft or len(email_draft.strip()) < 20:
                email_draft = "AI 분석 결과를 파싱할 수 없습니다. 이메일 초안을 확인해주세요."
            
            result = {
                "response_type": response_type,
                "summary": summary.strip(),
                "action_flow": action_flow,
                "email_draft": email_draft,
                "full_response": response_text
            }
            
            return result
            
        except Exception as e:
            # 오류 발생 시 기본값 반환
            return {
                "response_type": "해결안",
                "summary": "파싱 오류로 인해 요약을 생성할 수 없습니다. 고객 문의 내용을 확인해주세요.",
                "action_flow": "파싱 오류로 인해 조치 흐름을 생성할 수 없습니다. 단계별 조치 사항을 확인해주세요.",
                "email_draft": "파싱 오류로 인해 이메일 초안을 생성할 수 없습니다. 이메일 초안을 확인해주세요.",
                "full_response": response_text
            }
    
    def generate_complete_response(self,
                                 customer_input: str,
                                 issue_type: str,
                                 condition_1: str = "",
                                 condition_2: str = "",
                                 model: str = "gpt-4o") -> Dict[str, Any]:
        """완전한 응답 생성 프로세스"""
        try:
            # 프롬프트 조립
            prompt = self.build_prompt(
                customer_input=customer_input,
                issue_type=issue_type,
                condition_1=condition_1,
                condition_2=condition_2
            )
            
            # GPT API 호출
            api_response = self.generate_response(prompt, model)
            
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
                    "gpt_result": {
                        "api_response": api_response,
                        "parsed_response": parsed_response,
                        "raw_response": api_response["response"],  # 원본 응답 텍스트 포함
                        "prompt_used": prompt,
                        "model_used": model
                    }
                }
            else:
                # API 실패 시 기본 응답 생성
                default_response = self._generate_default_response(
                    customer_input, issue_type, condition_1, condition_2
                )
                
                return {
                    "success": False,
                    "error": api_response.get("error", "GPT API 호출 실패"),
                    "gpt_result": {
                        "api_response": api_response,
                        "parsed_response": default_response,
                        "raw_response": "",  # API 실패 시 빈 문자열
                        "prompt_used": prompt,
                        "model_used": model
                    }
                }
                
        except Exception as e:
            print(f"GPT 응답 생성 중 오류: {e}")
            # 전체 프로세스 실패 시 기본 응답 생성
            default_response = self._generate_default_response(
                customer_input, issue_type, condition_1, condition_2
            )
            
            return {
                "success": False,
                "error": str(e),
                "gpt_result": {
                    "api_response": {"success": False, "error": str(e)},
                    "parsed_response": default_response,
                    "raw_response": "",  # 오류 발생 시 빈 문자열
                    "prompt_used": "",
                    "model_used": model
                }
            }
    
    def _generate_default_response(self, customer_input: str, issue_type: str, 
                                 condition_1: str, condition_2: str) -> Dict[str, Any]:
        """기본 응답 생성 (Gemini API 실패 시)"""
        
        # 문제 유형별 기본 응답 템플릿
        default_responses = {
            "현재 비밀번호가 맞지 않습니다": {
                "response_type": "해결안",
                "summary": "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안되는 문제입니다.",
                "action_flow": "1. PK P 설정에서 CCTV 비밀번호 확인\n2. HTTPS/HTTP 프로토콜 설정 확인\n3. 필요시 현장 확인",
                "email_draft": f"""안녕하세요,

{customer_input}에 대한 답변드립니다.

현재 발생한 문제는 PK P에 저장된 비밀번호로 CCTV 웹 접속이 안되는 것으로 파악됩니다.

권장 조치사항:
1. PK P 설정에서 CCTV 비밀번호를 확인해주세요
2. HTTPS/HTTP 프로토콜 설정이 올바른지 확인해주세요
3. 위 조치로 해결되지 않으면 현장 확인이 필요할 수 있습니다

추가 문의사항이 있으시면 언제든지 연락주시기 바랍니다.

감사합니다."""
            },
            "VMS와의 통신에 실패했습니다": {
                "response_type": "해결안",
                "summary": "SVMS와 PK P 간 통신 실패 문제입니다.",
                "action_flow": "1. PKP 웹 설정 > NVR/VMS 항목 확인\n2. VMS 패스워드 일치 여부 확인\n3. 네트워크 연결 상태 확인",
                "email_draft": f"""안녕하세요,

{customer_input}에 대한 답변드립니다.

현재 발생한 문제는 VMS와의 통신 실패로 파악됩니다.

권장 조치사항:
1. PKP 웹 설정 > NVR/VMS 항목에서 등록된 VMS 패스워드 확인
2. VMS 패스워드와 PK P 설정이 일치하는지 확인
3. 네트워크 연결 상태 확인

추가 문의사항이 있으시면 언제든지 연락주시기 바랍니다.

감사합니다."""
            },
            "Ping 테스트에 실패했습니다": {
                "response_type": "출동",
                "summary": "네트워크 연결 상태 확인이 필요한 문제입니다.",
                "action_flow": "1. 네트워크 케이블 연결 상태 확인\n2. 네트워크 설정 점검\n3. 현장 출동 필요",
                "email_draft": f"""안녕하세요,

{customer_input}에 대한 답변드립니다.

현재 발생한 문제는 네트워크 연결 상태 확인이 필요한 것으로 파악됩니다.

권장 조치사항:
1. 네트워크 케이블 연결 상태를 확인해주세요
2. 네트워크 설정을 점검해주세요
3. 현장 출동이 필요할 수 있습니다

추가 문의사항이 있으시면 언제든지 연락주시기 바랍니다.

감사합니다."""
            }
        }
        
        # 기본 응답 선택
        if issue_type in default_responses:
            response = default_responses[issue_type]
        else:
            response = {
                "response_type": "질문",
                "summary": f"{issue_type} 관련 문제입니다.",
                "action_flow": "1. 추가 정보 확인 필요\n2. 상세한 증상 파악\n3. 필요시 현장 확인",
                "email_draft": f"""안녕하세요,

{customer_input}에 대한 답변드립니다.

현재 발생한 문제에 대해 추가 정보가 필요합니다.

다음 사항을 확인해주시기 바랍니다:
1. 문제 발생 시점과 상황
2. 사용 중인 시스템 버전
3. 기타 관련 정보

추가 문의사항이 있으시면 언제든지 연락주시기 바랍니다.

감사합니다."""
            }
        
        response["full_response"] = f"""
[대응유형] {response['response_type']}

[응답내용]

- 요약: {response['summary']}

- 조치 흐름:

{response['action_flow']}

- 이메일 초안:

{response['email_draft']}
"""
        
        return response

# 사용 예시
if __name__ == "__main__":
    handler = GPTHandler()
    
    # 테스트 데이터
    test_data = {
        "customer_input": "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다. 비밀번호는 정확히 입력했는데도 인증 실패가 발생합니다.",
        "issue_type": "현재 비밀번호가 맞지 않습니다",
        "condition_1": "고객이 PK P에 저장된 비밀번호로 CCTV 웹 접속 가능한가?",
        "condition_2": "접속 방식이 HTTPS 또는 HTTP인지 확인되었는가?",
        "similar_cases": """
사례 1:
- 문제 유형: 현재 비밀번호가 맞지 않습니다
- 고객 문의: PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다
- 조건 1: 고객이 PK P에 저장된 비밀번호로 CCTV 웹 접속 가능한가?
- 조건 2: 접속 방식이 HTTPS 또는 HTTP인지 확인되었는가?
- 해결책: 비밀번호 방식 확인 후 설정창 접근. 필요시 현장 확인
- 현장 출동 필요: Y
- 최종 해결: HTTPS/HTTP 프로토콜 설정을 확인하여 일치시킨 후 해결됨
""",
        "manual_ref": ""
    }
    
    # 응답 생성
    result = handler.generate_complete_response(**test_data)
    
    if result["success"]:
        print("✅ 응답 생성 성공")
        print(f"대응 유형: {result['parsed_response']['response_type']}")
        print(f"요약: {result['parsed_response']['summary']}")
        print(f"조치 흐름: {result['parsed_response']['action_flow']}")
        print(f"이메일 초안: {result['parsed_response']['email_draft']}")
    else:
        print("❌ 응답 생성 실패")
        print(f"오류: {result['error']}")
    
    print("\n" + "="*50)
    print("전체 응답:")
    print(result['parsed_response']['full_response']) 