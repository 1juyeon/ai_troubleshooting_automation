import requests
import json
import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
import os

class SOLAPIHandler:
    """SOLAPI를 사용하여 SMS를 발송하는 핸들러"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """SOLAPI 핸들러 초기화"""
        # API 키 설정 (사이드바 우선, st.secrets 차선, 환경변수 마지막)
        if api_key:
            self.api_key = api_key
        else:
            try:
                # Streamlit Cloud secrets에서 가져오기
                if hasattr(st, 'secrets') and st.secrets:
                    self.api_key = st.secrets.get("SOLAPI_API_KEY", "")
                else:
                    self.api_key = ""
            except:
                self.api_key = ""
            
            # 환경변수에서도 시도
            if not self.api_key:
                self.api_key = os.getenv("SOLAPI_API_KEY", "")
        
        if api_secret:
            self.api_secret = api_secret
        else:
            try:
                # Streamlit Cloud secrets에서 가져오기
                if hasattr(st, 'secrets') and st.secrets:
                    self.api_secret = st.secrets.get("SOLAPI_API_SECRET", "")
                else:
                    self.api_secret = ""
            except:
                self.api_secret = ""
                
            # 환경변수에서도 시도
            if not self.api_secret:
                self.api_secret = os.getenv("SOLAPI_API_SECRET", "")
        
        # SOLAPI 기본 설정
        self.base_url = "https://api.solapi.com"
        self.sender = "01012345678"  # 발신자 번호 (기본값)
        
        if not self.api_key or not self.api_secret:
            st.warning("⚠️ SOLAPI API 키 또는 시크릿이 설정되지 않았습니다.")
            st.info("Streamlit Cloud Secrets 또는 환경변수에 SOLAPI_API_KEY와 SOLAPI_API_SECRET을 설정해주세요.")
    
    def send_sms(self, 
                 phone_number: str, 
                 message: str, 
                 recipient_name: str = "",
                 sender_name: str = "PrivKeeper") -> Dict[str, Any]:
        """SMS 발송"""
        if not self.api_key or not self.api_secret:
            return {
                "success": False,
                "error": "SOLAPI API 키가 설정되지 않았습니다.",
                "message": "API 키를 설정해주세요."
            }
        
        try:
            # SOLAPI SMS 발송 API 엔드포인트
            url = f"{self.base_url}/messages/v4/send"
            
            # 헤더 설정 (SOLAPI는 API Key와 Secret을 헤더에 포함)
            headers = {
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key,
                "X-API-SECRET": self.api_secret
            }
            
            # 요청 데이터
            data = {
                "message": {
                    "to": phone_number,
                    "from": self.sender,
                    "text": full_message
                }
            }
            
            # 메시지 내용 구성
            if recipient_name:
                full_message = f"[{sender_name}]\n{recipient_name}님, {message}"
            else:
                full_message = f"[{sender_name}]\n{message}"
            
            # API 호출 (요청 본문에 API 키와 Secret 포함)
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # 성공 여부 확인
                if result.get("status") == "SUCCESS":
                    return {
                        "success": True,
                        "message": "SMS가 성공적으로 발송되었습니다.",
                        "message_id": result.get("messageId", ""),
                        "recipient": phone_number,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"SMS 발송 실패: {result.get('errorMessage', '알 수 없는 오류')}",
                        "status": result.get("status", "UNKNOWN")
                    }
            else:
                return {
                    "success": False,
                    "error": f"API 호출 실패: HTTP {response.status_code}",
                    "response": response.text
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "API 호출 시간 초과",
                "message": "네트워크 상태를 확인하고 다시 시도해주세요."
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"네트워크 오류: {str(e)}",
                "message": "인터넷 연결을 확인하고 다시 시도해주세요."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"예상치 못한 오류: {str(e)}",
                "message": "잠시 후 다시 시도해주세요."
            }
    
    def send_analysis_summary_sms(self, 
                                 phone_number: str, 
                                 recipient_name: str,
                                 analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """AI 분석 결과 요약을 SMS로 발송"""
        try:
            # 분석 결과에서 핵심 정보 추출
            issue_type = analysis_result.get('issue_type', '문의')
            summary = ""
            action_flow = ""
            
            # full_analysis_result에서 정보 추출 시도
            if 'full_analysis_result' in analysis_result:
                full_result = analysis_result['full_analysis_result']
                if 'gemini_result' in full_result:
                    gemini_result = full_result['gemini_result']
                    if 'parsed_response' in gemini_result:
                        parsed = gemini_result['parsed_response']
                        summary = parsed.get('summary', '')
                        action_flow = parsed.get('action_flow', '')
            
            # 요약이 없으면 기본 메시지 사용
            if not summary:
                summary = f"{issue_type}에 대한 AI 분석이 완료되었습니다."
            
            # SMS 메시지 구성 (길이 제한 고려)
            sms_message = f"{issue_type} 분석 완료\n"
            if summary:
                # 요약을 100자 이내로 제한
                summary_short = summary[:100] + "..." if len(summary) > 100 else summary
                sms_message += f"요약: {summary_short}\n"
            
            if action_flow:
                # 조치 흐름을 100자 이내로 제한
                action_short = action_flow[:100] + "..." if len(action_flow) > 100 else action_flow
                sms_message += f"조치: {action_short}"
            
            # SMS 발송
            return self.send_sms(phone_number, sms_message, recipient_name)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"SMS 메시지 구성 실패: {str(e)}",
                "message": "메시지 구성 중 오류가 발생했습니다."
            }
    
    def set_sender(self, phone_number: str):
        """발신자 번호 설정"""
        self.sender = phone_number
    
    def test_connection(self) -> Dict[str, Any]:
        """SOLAPI 연결 테스트"""
        if not self.api_key or not self.api_secret:
            return {
                "success": False,
                "message": "API 키가 설정되지 않았습니다."
            }
        
        try:
            # SOLAPI 계정 정보 조회 API로 연결 테스트 (더 안정적)
            url = f"{self.base_url}/account/v1/balance"
            headers = {
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key,
                "X-API-SECRET": self.api_secret
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                balance = result.get('balance', 0)
                return {
                    "success": True,
                    "message": f"SOLAPI 연결 성공 (잔액: {balance:,}원)"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "SOLAPI 인증 실패: API 키 또는 Secret이 올바르지 않습니다."
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "message": "SOLAPI 권한 없음: API 키에 계정 조회 권한이 없습니다."
                }
            else:
                return {
                    "success": False,
                    "message": f"SOLAPI 연결 실패: HTTP {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "SOLAPI 연결 시간 초과: 네트워크 상태를 확인해주세요."
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "SOLAPI 서버 연결 실패: 인터넷 연결을 확인해주세요."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"SOLAPI 연결 테스트 실패: {str(e)}"
            }

# 사용 예시
if __name__ == "__main__":
    # 테스트용 핸들러 생성
    handler = SOLAPIHandler()
    
    # 연결 테스트
    test_result = handler.test_connection()
    print(f"연결 테스트: {test_result}")
    
    # SMS 발송 테스트 (실제 발송되지 않음)
    if test_result["success"]:
        test_sms = handler.send_sms(
            phone_number="01012345678",
            message="테스트 메시지입니다.",
            recipient_name="테스트"
        )
        print(f"SMS 발송 테스트: {test_sms}")
