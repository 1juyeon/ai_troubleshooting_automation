import openai
import os
import streamlit as st
from typing import Dict, Any, Optional
import json

class OpenAIHandler:
    def __init__(self, api_key: str = None):
        """OpenAI GPT 핸들러 초기화"""
        # 프롬프트 템플릿 로딩 (API 키와 관계없이 항상 로드)
        self.prompt_template = self._load_prompt_template()
        
        try:
            # API 키 설정 (st.secrets 우선, 파라미터 차선, 환경변수 마지막)
            if api_key:
                self.api_key = api_key
            else:
                # st.secrets에서 먼저 시도
                try:
                    self.api_key = st.secrets["OPENAI_API_KEY"]
                    print("✅ OpenAI API 키를 Streamlit Secrets에서 로드했습니다.")
                except:
                    # 환경변수로 폴백
                    self.api_key = os.getenv("OPENAI_API_KEY")
                    if self.api_key:
                        print("✅ OpenAI API 키를 환경변수에서 로드했습니다.")
            
            if not self.api_key:
                print("⚠️ OpenAI API 키가 설정되지 않았습니다.")
                print("Streamlit Cloud Secrets 또는 환경변수 OPENAI_API_KEY를 설정해주세요.")
                self.client = None
                return
            
            # OpenAI 클라이언트 설정
            self.client = openai.OpenAI(api_key=self.api_key)
            # 기본 모델 설정 (GPT-4o 사용)
            self.model = "gpt-4o"
            
            print("✅ OpenAI API 초기화 성공 (gpt-4o)")
            
        except Exception as e:
            print(f"❌ OpenAI API 초기화 실패: {e}")
            self.client = None
        
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

- 이메일 초안: 고객에게 보낼 수 있는 실제 이메일 본문 형식으로 작성하십시오. 조치 흐름의 내용을 이메일 본문에 자연스럽게 포함하여 작성하십시오. 간결하고 정중한 표현을 사용하십시오.

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

- 이메일 초안: 고객에게 보낼 수 있는 실제 이메일 본문 형식으로 작성하십시오. 조치 흐름의 내용을 이메일 본문에 자연스럽게 포함하여 작성하십시오. 간결하고 정중한 표현을 사용하십시오.

[예외 처리 기준]
- 조건 정보가 불충분하거나 고객 상태가 불명확한 경우 → "추가 확인이 필요합니다. 다음 질문을 해주세요."라고 안내하십시오.
- 문제가 시나리오 DB에 존재하지 않거나, 적절한 해결책이 없는 경우 → "현장 출동이 필요할 수 있습니다."로 안내하십시오.
- 확실한 답변이 불가능한 경우에도 → "현장 확인 후 조치가 필요합니다" 또는 "엔지니어 출동을 권장합니다" 등으로 마무리하십시오."""
        else:
            prompt_template = self.prompt_template
        
        return prompt_template.format(
            customer_input=customer_input,
            issue_type=issue_type,
            condition_1=condition_1,
            condition_2=condition_2
        )
    
    def generate_response(self, 
                         customer_input: str,
                         issue_type: str,
                         condition_1: str = "",
                         condition_2: str = "",
                         model: str = None) -> Dict[str, Any]:
        """GPT API를 사용하여 응답 생성"""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API가 초기화되지 않았습니다. API 키를 확인해주세요.",
                "response": None
            }
        
        try:
            # 사용할 모델 결정 (파라미터 우선, 기본값 차선)
            use_model = model if model else self.model
            
            # 프롬프트 조립
            prompt = self.build_prompt(customer_input, issue_type, condition_1, condition_2)
            
            # GPT API 호출
            response = self.client.chat.completions.create(
                model=use_model,
                messages=[
                    {"role": "system", "content": "당신은 PrivKeeper P 장애 대응 전문가입니다. 고객의 문의에 대해 정확하고 실용적인 해결책을 제시해주세요. 반드시 제공된 형식을 정확히 따라 응답하고, 이메일 초안에는 조치 흐름의 내용이 포함되어야 합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # 응답 추출
            generated_text = response.choices[0].message.content
            
            return {
                "success": True,
                "response": generated_text,
                "model": use_model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            error_msg = f"GPT API 호출 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "response": None
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """API 연결 테스트"""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API가 초기화되지 않았습니다."
            }
        
        try:
            # 간단한 테스트 요청
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "안녕하세요. 연결 테스트입니다."}
                ],
                max_tokens=10
            )
            
            return {
                "success": True,
                "message": "OpenAI API 연결 성공",
                "model": self.model,
                "test_response": response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"연결 테스트 실패: {str(e)}"
            }
    
    def get_available_models(self) -> list:
        """사용 가능한 모델 목록 조회"""
        if not self.client:
            return []
        
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"모델 목록 조회 실패: {e}")
            return []
    
    def switch_model(self, model_name: str) -> bool:
        """모델 변경"""
        try:
            # 간단한 테스트로 모델 유효성 확인
            test_response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": "테스트"}
                ],
                max_tokens=5
            )
            
            self.model = model_name
            print(f"✅ 모델을 {model_name}으로 변경했습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 모델 변경 실패 ({model_name}): {e}")
            return False
