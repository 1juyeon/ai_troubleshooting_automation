import google.generativeai as genai
import os
import streamlit as st
from typing import Dict, Any, Optional
import json

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
            print(f"프롬프트 템플릿 로딩 실패: {e}")
            # 기본 프롬프트 템플릿 (프롬프트.txt와 동일)
            return """[고객 문의 내용]
{customer_input}

[문제 유형]
{issue_type}

[조건 정보]
- 조건 1: {condition_1}
- 조건 2: {condition_2}

[대응안 작성 지침]
아래 형식을 참고하여, 실무자가 이해하기 쉽도록 자연스럽고 정확하게 응답을 생성하십시오.

[대응유형] 해결안 / 질문 / 출동 중 하나를 선택하십시오.

[응답내용]
- 요약: 고객 문의의 핵심 내용을 간결하게 정리하십시오.

- 조치 흐름: 아래 형식을 따라 단계별로 줄바꿈하며 번호를 붙여 설명하십시오.

1. 단계 제목: 해당 단계에서 수행할 조치 설명

2. 단계 제목: 해당 단계에서 수행할 조치 설명

3. 단계 제목: 해당 단계에서 수행할 조치 설명

※ 각 단계는 짧고 명확하게, 실무자가 바로 이해할 수 있도록 작성하십시오.

- 이메일 초안: 고객에게 보낼 수 있는 실제 이메일 본문 형식으로 작성하십시오. 간결하고 정중한 표현을 사용하십시오.

[예외 처리 기준]
- 조건 정보가 불충분하거나 고객 상태가 불명확한 경우 → "추가 확인이 필요합니다. 다음 질문을 해주세요."라고 안내하십시오.
- 문제가 시나리오 DB에 존재하지 않거나, 적절한 해결책이 없는 경우 → "현장 출동이 필요할 수 있습니다."로 안내하십시오.
- 확실한 답변이 불가능한 경우에도 → "현장 확인 후 조치가 필요합니다" 또는 "엔지니어 출동을 권장합니다" 등으로 마무리하십시오."""
    
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
아래 형식을 참고하여, 실무자가 이해하기 쉽도록 자연스럽고 정확하게 응답을 생성하십시오.

[대응유형] 해결안 / 질문 / 출동 중 하나를 선택하십시오.

[응답내용]
- 요약: 고객 문의의 핵심 내용을 간결하게 정리하십시오.

- 조치 흐름: 아래 형식을 따라 단계별로 줄바꿈하며 번호를 붙여 설명하십시오.

1. 단계 제목: 해당 단계에서 수행할 조치 설명

2. 단계 제목: 해당 단계에서 수행할 조치 설명

3. 단계 제목: 해당 단계에서 수행할 조치 설명

※ 각 단계는 짧고 명확하게, 실무자가 바로 이해할 수 있도록 작성하십시오.

- 이메일 초안: 고객에게 보낼 수 있는 실제 이메일 본문 형식으로 작성하십시오. 간결하고 정중한 표현을 사용하십시오.

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
            
            # 타임아웃 체크
            if elapsed_time > 15:
                print(f"Gemini API 타임아웃 ({elapsed_time:.2f}초), 기본 응답 사용")
                return {
                    "success": False,
                    "error": "API 응답 시간 초과",
                    "response": "죄송합니다. 응답 생성에 시간이 오래 걸려 기본 응답을 제공합니다.",
                    "model": "gemini-1.5-pro",
                    "response_time": elapsed_time
                }
            
            print(f"Gemini API 응답 시간: {elapsed_time:.2f}초")
            
            return {
                "success": True,
                "response": response.text,
                "model": "gemini-1.5-pro",
                "tokens_used": len(response.text.split()),  # 대략적인 토큰 수
                "response_time": elapsed_time
            }
            
        except Exception as e:
            print(f"Gemini API 호출 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요.",
                "model": "gemini-1.5-pro"
            }
    
    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """응답 텍스트를 구조화된 형태로 파싱"""
        try:
            # 대응 유형 추출
            response_type = "해결안"  # 기본값
            if "질문" in response_text:
                response_type = "질문"
            elif "출동" in response_text:
                response_type = "출동"
            
            # 요약, 조치 흐름, 이메일 초안 추출 시도
            summary = ""
            action_flow = ""
            email_draft = ""
            
            lines = response_text.split('\n')
            current_section = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "요약:" in line or "요약" in line:
                    current_section = "summary"
                    summary = line.replace("요약:", "").replace("요약", "").strip()
                elif "조치 흐름:" in line or "조치 흐름" in line:
                    current_section = "action"
                    action_flow = line.replace("조치 흐름:", "").replace("조치 흐름", "").strip()
                elif "이메일 초안:" in line or "이메일 초안" in line:
                    current_section = "email"
                    email_draft = line.replace("이메일 초안:", "").replace("이메일 초안", "").strip()
                elif current_section == "summary":
                    if summary:  # 이미 내용이 있으면 줄바꿈 추가
                        summary += "\n" + line
                    else:
                        summary = line
                elif current_section == "action":
                    if action_flow:  # 이미 내용이 있으면 줄바꿈 추가
                        action_flow += "\n" + line
                    else:
                        action_flow = line
                elif current_section == "email":
                    if email_draft:  # 이미 내용이 있으면 줄바꿈 추가
                        email_draft += "\n" + line
                    else:
                        email_draft = line
            
            return {
                "response_type": response_type,
                "summary": summary.strip(),
                "action_flow": action_flow.strip(),
                "email_draft": email_draft.strip(),
                "full_response": response_text
            }
            
        except Exception as e:
            return {
                "response_type": "해결안",
                "summary": "응답 파싱 중 오류가 발생했습니다.",
                "action_flow": "",
                "email_draft": "",
                "full_response": response_text
            }
    
    def generate_complete_response(self,
                                 customer_input: str,
                                 issue_type: str,
                                 condition_1: str = "",
                                 condition_2: str = "") -> Dict[str, Any]:
        """완전한 응답 생성 프로세스"""
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
            
            return {
                "success": True,
                "api_response": api_response,
                "parsed_response": parsed_response,
                "prompt_used": prompt
            }
        else:
            # 기본 응답 생성
            default_response = self._generate_default_response(
                customer_input, issue_type, condition_1, condition_2
            )
            
            return {
                "success": False,
                "error": api_response["error"],
                "api_response": api_response,
                "parsed_response": default_response,
                "prompt_used": prompt
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