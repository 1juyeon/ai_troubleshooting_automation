import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz
import streamlit as st

class CloudDataStorage:
    """Streamlit Cloud 환경용 임시 데이터 저장소"""
    
    def __init__(self):
        self.data = {}
        self.timestamp = datetime.now().isoformat()
    
    def save(self, key: str, data: Any) -> bool:
        """세션 상태에 데이터 저장"""
        try:
            self.data[key] = {
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            return True
        except Exception as e:
            print(f"❌ 클라우드 저장 실패: {e}")
            return False
    
    def load(self, key: str) -> Any:
        """세션 상태에서 데이터 로드"""
        return self.data.get(key, {}).get('data', None)
    
    def get_all_keys(self) -> List[str]:
        """저장된 모든 키 반환"""
        return list(self.data.keys())

class MultiUserHistoryDB:
    def __init__(self, data_dir: str = "user_data"):
        """다중 사용자 이력 저장소 초기화"""
        # Streamlit Cloud 환경 감지
        self.is_cloud = self._is_streamlit_cloud()
        
        # MongoDB 핸들러 초기화 (나중에 설정)
        self.mongo_handler = None
        
        if self.is_cloud:
            print("☁️ Streamlit Cloud 환경 감지 - 클라우드 저장소 확인 중...")
            self.storage_handler = self._get_cloud_storage()
        else:
            print("💻 로컬 환경 감지 - 파일 시스템 사용")
            # 절대 경로로 변환
            if not os.path.isabs(data_dir):
                self.data_dir = os.path.join(os.getcwd(), data_dir)
            else:
                self.data_dir = data_dir
            self._ensure_data_directory()
    
    def set_mongo_handler(self, mongo_handler):
        """MongoDB 핸들러 설정"""
        self.mongo_handler = mongo_handler
        print("✅ MongoDB 핸들러가 설정되었습니다.")
    
    def _is_streamlit_cloud(self) -> bool:
        """Streamlit Cloud 환경인지 확인"""
        return os.getenv('STREAMLIT_SERVER_RUNNING') == 'true'
    
    def _get_cloud_storage(self):
        """클라우드 환경용 저장소 선택"""
        try:
            # MongoDB 우선 시도
            if "MONGODB_URI" in st.secrets:
                print("✅ MongoDB Atlas 연결 시도 중...")
                from mongodb_handler import MongoDBHandler
                return MongoDBHandler()
            else:
                # MongoDB 설정이 없으면 임시 저장소 사용
                print("⚠️ MongoDB 설정이 없습니다. 임시 저장소를 사용합니다.")
                return CloudDataStorage()
        except Exception as e:
            print(f"⚠️ 클라우드 저장소 초기화 실패: {e}")
            print("임시 저장소로 폴백합니다.")
            return CloudDataStorage()
    
    def _ensure_data_directory(self):
        """데이터 디렉토리 생성 (로컬 환경만)"""
        if self.is_cloud:
            return
            
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
                print(f"✅ 사용자 데이터 디렉토리 생성: {self.data_dir}")
            except Exception as e:
                print(f"⚠️ 디렉토리 생성 실패: {e}")
    
    def _get_safe_timestamp(self) -> str:
        """안전한 타임스탬프 생성 (한국 시간대, 실패 시 UTC 사용)"""
        try:
            return datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
        except Exception as e:
            print(f"⚠️ 한국 시간대 설정 실패, UTC 사용: {e}")
            return datetime.now().isoformat()
    
    def _get_user_id(self, user_name: str, user_role: str) -> str:
        """사용자 ID 생성 (이름 + 역할 기반)"""
        user_string = f"{user_name}_{user_role}"
        return hashlib.md5(user_string.encode()).hexdigest()[:8]
    
    def _get_user_history_file(self, user_id: str) -> str:
        """사용자별 이력 파일 경로 (로컬 환경만)"""
        if self.is_cloud:
            return f"cloud_history_{user_id}"
        return os.path.join(self.data_dir, f"history_{user_id}.json")
    
    def _get_global_history_file(self) -> str:
        """전체 이력 파일 경로 (로컬 환경만)"""
        if self.is_cloud:
            return "cloud_global_history"
        return os.path.join(self.data_dir, "global_history.json")
    
    def _ensure_history_file(self, file_path: str):
        """이력 파일 생성 (로컬 환경만)"""
        if self.is_cloud:
            return
            
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ 파일 생성 실패: {e}")
    
    def _load_history(self, file_path: str) -> List[Dict]:
        """이력 데이터 로드"""
        if self.is_cloud:
            # 클라우드 환경에서는 세션 상태에서 로드
            cloud_key = file_path
            data = self.cloud_storage.load(cloud_key)
            return data if data else []
        
        try:
            self._ensure_history_file(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 이력 로드 실패: {e}")
            return []
    
    def _save_history(self, history_data: List[Dict], file_path: str) -> bool:
        """이력 데이터 저장"""
        if self.is_cloud:
            # 클라우드 환경에서는 세션 상태에 저장
            cloud_key = file_path
            return self.cloud_storage.save(cloud_key, history_data)
        
        try:
            # 디렉토리가 존재하는지 확인
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 임시 파일에 먼저 저장
            temp_file = file_path + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            
            # 성공적으로 저장되면 원본 파일로 이동
            if os.path.exists(file_path):
                backup_file = file_path + '.backup'
                try:
                    os.rename(file_path, backup_file)
                except Exception as e:
                    print(f"⚠️ 백업 파일 생성 실패: {e}")
            
            os.rename(temp_file, file_path)
            return True
            
        except PermissionError as e:
            print(f"❌ 파일 권한 오류: {e}")
            print(f"파일 경로: {file_path}")
            return False
        except OSError as e:
            print(f"❌ 파일 시스템 오류: {e}")
            print(f"파일 경로: {file_path}")
            return False
        except Exception as e:
            print(f"❌ 이력 저장 실패: {e}")
            print(f"파일 경로: {file_path}")
            return False
    
    def save_analysis(self, analysis_result: Dict, inquiry_data: Dict):
        """분석 결과 저장 (사용자별 + 전체)"""
        try:
            # 사용자 ID 생성
            user_name = inquiry_data.get('user_name', 'Unknown')
            user_role = inquiry_data.get('user_role', 'Unknown')
            user_id = self._get_user_id(user_name, user_role)
            
            # 사용자별 이력 파일
            user_history_file = self._get_user_history_file(user_id)
            user_history = self._load_history(user_history_file)
            
            # 전체 이력 파일
            global_history_file = self._get_global_history_file()
            global_history = self._load_history(global_history_file)
            
            # 새로운 분석 결과 생성
            new_entry = {
                'id': len(user_history) + 1,
                'user_id': user_id,
                'user_name': user_name,
                'user_role': user_role,
                'timestamp': inquiry_data.get('timestamp', self._get_safe_timestamp()),
                'customer_name': inquiry_data.get('customer_name', ''),
                'customer_contact': inquiry_data.get('customer_contact', ''),
                'customer_manager': inquiry_data.get('customer_manager', ''),
                'inquiry_content': inquiry_data.get('inquiry_content', ''),
                'issue_type': analysis_result.get('issue_type', ''),
                'classification_method': analysis_result.get('classification', {}).get('method', ''),
                'confidence': analysis_result.get('classification', {}).get('confidence', ''),
                'response_type': analysis_result.get('gemini_result', {}).get('parsed_response', {}).get('response_type', ''),
                'summary': analysis_result.get('gemini_result', {}).get('parsed_response', {}).get('summary', ''),
                'action_flow': analysis_result.get('gemini_result', {}).get('parsed_response', {}).get('action_flow', ''),
                'email_draft': analysis_result.get('gemini_result', {}).get('parsed_response', {}).get('email_draft', ''),
                'system_version': inquiry_data.get('system_version', ''),
                'browser_info': inquiry_data.get('browser_info', ''),
                'os_info': inquiry_data.get('os_info', ''),
                'error_code': inquiry_data.get('error_code', ''),
                'priority': inquiry_data.get('priority', ''),
                'contract_type': inquiry_data.get('contract_type', ''),
                'full_analysis_result': analysis_result
            }
            
            # 사용자별 이력에 추가
            user_history.append(new_entry)
            
            # 전체 이력에 추가 (사용자 정보 포함)
            global_entry = new_entry.copy()
            global_entry['global_id'] = len(global_history) + 1
            global_history.append(global_entry)
            
            # 저장
            user_saved = self._save_history(user_history, user_history_file)
            global_saved = self._save_history(global_history, global_history_file)
            
            if user_saved and global_saved:
                print(f"✅ 분석 결과 저장 완료 (사용자: {user_name}, ID: {user_id})")
                return {
                    "success": True, 
                    "database": "multi_user_json",
                    "id": new_entry['id'],  # 분석 결과 ID 추가
                    "user_id": user_id,
                    "user_name": user_name
                }
            else:
                return {"success": False, "error": "저장 실패"}
                
        except Exception as e:
            print(f"❌ 다중 사용자 저장 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_history(self, user_name: str, user_role: str, 
                        limit: int = 50, offset: int = 0,
                        issue_type: str = None, date_from: str = None, 
                        date_to: str = None, keyword: str = None):
        """사용자별 이력 조회"""
        try:
            user_id = self._get_user_id(user_name, user_role)
            user_history_file = self._get_user_history_file(user_id)
            history = self._load_history(user_history_file)
            
            # 필터링
            filtered_history = self._filter_history(history, issue_type, date_from, date_to, keyword)
            
            # 페이징
            total_count = len(filtered_history)
            paginated_history = filtered_history[offset:offset + limit]
            
            return {
                "success": True,
                "data": paginated_history,
                "total_count": total_count,
                "user_id": user_id,
                "user_name": user_name
            }
            
        except Exception as e:
            print(f"❌ 사용자 이력 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_global_history(self, limit: int = 50, offset: int = 0,
                          issue_type: str = None, date_from: str = None, 
                          date_to: str = None, keyword: str = None,
                          user_name: str = None):
        """전체 이력 조회"""
        try:
            global_history_file = self._get_global_history_file()
            history = self._load_history(global_history_file)
            
            # 필터링
            filtered_history = self._filter_history(history, issue_type, date_from, date_to, keyword, user_name)
            
            # 페이징
            total_count = len(filtered_history)
            paginated_history = filtered_history[offset:offset + limit]
            
            return {
                "success": True,
                "data": paginated_history,
                "total_count": total_count
            }
            
        except Exception as e:
            print(f"❌ 전체 이력 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def _filter_history(self, history: List[Dict], issue_type: str = None, 
                       date_from: str = None, date_to: str = None, 
                       keyword: str = None, user_name: str = None) -> List[Dict]:
        """이력 필터링"""
        filtered_history = []
        
        for entry in history:
            # 문제 유형 필터
            if issue_type and entry.get('issue_type') != issue_type:
                continue
            
            # 사용자 필터
            if user_name and entry.get('user_name') != user_name:
                continue
            
            # 날짜 필터
            if date_from and entry.get('timestamp', '') < date_from:
                continue
            if date_to and entry.get('timestamp', '') > date_to:
                continue
            
            # 키워드 필터
            if keyword:
                search_text = f"{entry.get('inquiry_content', '')} {entry.get('customer_name', '')} {entry.get('issue_type', '')}"
                if keyword.lower() not in search_text.lower():
                    continue
            
            filtered_history.append(entry)
        
        # 최신순 정렬
        filtered_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return filtered_history
    
    def get_statistics(self, user_name: str = None, user_role: str = None):
        """통계 조회"""
        try:
            if user_name and user_role:
                # 사용자별 통계
                user_id = self._get_user_id(user_name, user_role)
                user_history_file = self._get_user_history_file(user_id)
                history = self._load_history(user_history_file)
                
                issue_types = list(set([entry.get('issue_type', '') for entry in history if entry.get('issue_type')]))
                response_types = list(set([entry.get('response_type', '') for entry in history if entry.get('response_type')]))
                
                return {
                    "success": True,
                    "total_analyses": len(history),
                    "issue_types": issue_types,
                    "response_types": response_types,
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_role": user_role
                }
            else:
                # 전체 통계
                global_history_file = self._get_global_history_file()
                history = self._load_history(global_history_file)
                
                # 사용자 정보 추출 (user_name과 user_role이 모두 있는 경우만)
                users = []
                for entry in history:
                    user_name_val = entry.get('user_name', '')
                    user_role_val = entry.get('user_role', '')
                    if user_name_val and user_role_val:
                        user_key = f"{user_name_val}_{user_role_val}"
                        if user_key not in users:
                            users.append(user_key)
                
                # 문제 유형 추출 (issue_type이 있는 경우만)
                issue_types = []
                for entry in history:
                    issue_type = entry.get('issue_type', '')
                    if issue_type and issue_type not in issue_types:
                        issue_types.append(issue_type)
                
                # 응답 유형 추출 (response_type이 있는 경우만)
                response_types = []
                for entry in history:
                    response_type = entry.get('response_type', '')
                    if response_type and response_type not in response_types:
                        response_types.append(response_type)
                
                # full_analysis_result에서 response_type 추출 시도
                for entry in history:
                    full_result = entry.get('full_analysis_result', {})
                    if full_result:
                        gemini_result = full_result.get('gemini_result', {})
                        if gemini_result:
                            parsed_response = gemini_result.get('parsed_response', {})
                            if parsed_response:
                                response_type = parsed_response.get('response_type', '')
                                if response_type and response_type not in response_types:
                                    response_types.append(response_type)
                
                return {
                    "success": True,
                    "total_analyses": len(history),
                    "total_users": len(users),
                    "issue_types": issue_types,
                    "response_types": response_types
                }
                
        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_user_history(self, user_name: str, user_role: str):
        """사용자별 이력 삭제"""
        try:
            user_id = self._get_user_id(user_name, user_role)
            user_history_file = self._get_user_history_file(user_id)
            
            if self.is_cloud:
                # 클라우드 환경에서는 세션 상태에서 삭제
                cloud_key = user_history_file
                self.cloud_storage.data.pop(cloud_key, None)
                print(f"✅ 사용자 이력 삭제 완료 (클라우드): {user_name} ({user_id})")
                return {"success": True, "user_id": user_id}
            else:
                if os.path.exists(user_history_file):
                    os.remove(user_history_file)
                    print(f"✅ 사용자 이력 삭제 완료: {user_name} ({user_id})")
                    return {"success": True, "user_id": user_id}
                else:
                    return {"success": False, "error": "사용자 이력 파일이 존재하지 않습니다."}
                
        except Exception as e:
            print(f"❌ 사용자 이력 삭제 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_analysis_by_customer_and_date(self, customer_name: str, inquiry_date: str):
        """고객사명과 날짜를 기준으로 분석 결과 조회"""
        try:
            # 전체 이력에서 해당 고객의 문의 찾기
            global_history_file = self._get_global_history_file()
            history = self._load_history(global_history_file)
            
            # 고객사명과 날짜로 필터링
            matching_entries = []
            for entry in history:
                entry_customer = entry.get('customer_name', '')
                entry_timestamp = entry.get('timestamp', '')
                
                # 고객사명 매칭
                if customer_name and entry_customer != customer_name:
                    continue
                
                # 날짜 매칭 (YYYY-MM-DD 형식으로 비교)
                if inquiry_date and entry_timestamp:
                    entry_date = entry_timestamp.split('T')[0] if 'T' in entry_timestamp else entry_timestamp.split(' ')[0]
                    if entry_date != inquiry_date:
                        continue
                
                matching_entries.append(entry)
            
            if matching_entries:
                # 가장 최근 항목 반환
                latest_entry = max(matching_entries, key=lambda x: x.get('timestamp', ''))
                
                # full_analysis_result에서 실제 AI 분석 데이터 추출
                full_result = latest_entry.get('full_analysis_result', {})
                
                # 분석 결과 데이터 구성
                analysis_data = {
                    'issue_type': full_result.get('issue_type', latest_entry.get('issue_type', '')),
                    'best_scenario': full_result.get('best_scenario', {}),
                    'gemini_result': full_result.get('gemini_result', {}),
                    'classification': full_result.get('classification', {}),
                    'customer_name': latest_entry.get('customer_name', ''),
                    'timestamp': latest_entry.get('timestamp', ''),
                    'inquiry_content': latest_entry.get('inquiry_content', ''),
                    'priority': latest_entry.get('priority', ''),
                    'contract_type': latest_entry.get('contract_type', '')
                }
                
                return {
                    "success": True,
                    "data": analysis_data
                }
            else:
                return {
                    "success": False,
                    "error": "해당 조건에 맞는 분석 결과를 찾을 수 없습니다."
                }
                
        except Exception as e:
            print(f"❌ 분석 결과 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_all_history(self):
        """전체 이력 삭제"""
        try:
            if self.is_cloud:
                # 클라우드 환경에서는 세션 상태 데이터 모두 삭제
                self.cloud_storage.data.clear()
                print("✅ 전체 이력 삭제 완료 (클라우드)")
                return {"success": True}
            else:
                # 로컬 환경에서는 파일들 삭제
                for filename in os.listdir(self.data_dir):
                    if filename.startswith("history_") and filename.endswith(".json"):
                        file_path = os.path.join(self.data_dir, filename)
                        os.remove(file_path)
                
                # 전체 이력 파일 삭제
                global_history_file = self._get_global_history_file()
                if os.path.exists(global_history_file):
                    os.remove(global_history_file)
                
                print("✅ 전체 이력 삭제 완료")
                return {"success": True}
            
        except Exception as e:
            print(f"❌ 전체 이력 삭제 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def save_feedback(self, analysis_id, feedback_type: str, user_name: str = "", user_role: str = ""):
        """AI 응답에 대한 피드백 저장 (MongoDB 우선)"""
        try:
            print(f"🔍 피드백 저장 시도 - Analysis ID: {analysis_id}, Type: {type(analysis_id)}")
            print(f"🔍 피드백 타입: {feedback_type}, 사용자: {user_name}, 역할: {user_role}")
            
            # MongoDB 연결 상태 확인 및 우선 사용
            if hasattr(self, 'mongo_handler') and self.mongo_handler and self.mongo_handler.is_connected():
                print("📊 MongoDB를 통한 피드백 저장 시도")
                result = self.mongo_handler.save_feedback(analysis_id, feedback_type, user_name, user_role)
                print(f"📊 MongoDB 피드백 저장 결과: {result}")
                return result
            
            # MongoDB 사용 불가시 로컬/클라우드 저장소 사용
            print("📊 로컬/클라우드 저장소를 통한 피드백 저장 시도")
            feedback_file = self._get_feedback_file()
            feedback_data = self._load_history(feedback_file)
            
            new_feedback = {
                'analysis_id': analysis_id,
                'feedback_type': feedback_type,
                'user_name': user_name,
                'user_role': user_role,
                'timestamp': self._get_safe_timestamp()
            }
            
            feedback_data.append(new_feedback)
            
            if self._save_history(feedback_data, feedback_file):
                print("✅ 로컬/클라우드 피드백 저장 성공")
                return {"success": True}
            else:
                print("❌ 로컬/클라우드 피드백 저장 실패")
                return {"success": False, "error": "피드백 저장 실패"}
                
        except Exception as e:
            print(f"❌ 피드백 저장 중 오류: {e}")
            return {"success": False, "error": str(e)}
    
    def get_liked_responses(self, issue_type: str = None, limit: int = 3):
        """좋아요를 받은 응답들 조회 (AI 학습용, MongoDB 우선)"""
        try:
            # MongoDB 연결 상태 확인 및 우선 사용
            if hasattr(self, 'mongo_handler') and self.mongo_handler and self.mongo_handler.is_connected():
                return self.mongo_handler.get_liked_responses(issue_type, limit)
            
            # MongoDB 사용 불가시 로컬/클라우드 저장소 사용
            feedback_file = self._get_feedback_file()
            feedback_data = self._load_history(feedback_file)
            
            # 좋아요를 받은 분석 ID들 추출
            liked_ids = [f['analysis_id'] for f in feedback_data if f.get('feedback_type') == 'like']
            
            if not liked_ids:
                return []
            
            # 해당 분석 결과들 조회
            global_history_file = self._get_global_history_file()
            global_history = self._load_history(global_history_file)
            
            liked_responses = []
            for entry in global_history:
                if entry.get('id') in liked_ids:
                    if not issue_type or entry.get('issue_type') == issue_type:
                        liked_responses.append({
                            'summary': entry.get('summary', ''),
                            'action_flow': entry.get('action_flow', ''),
                            'email_draft': entry.get('email_draft', '')
                        })
            
            return liked_responses[:limit]
            
        except Exception as e:
            print(f"❌ 좋아요 응답 조회 실패: {e}")
            return []
    
    def _get_feedback_file(self):
        """피드백 파일 경로 반환"""
        if self.is_cloud:
            return "feedback_data"
        else:
            return os.path.join(self.data_dir, "feedback_data.json")