import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz
import streamlit as st

class CloudDataStorage:
    """Streamlit Cloud 환경용 영구 데이터 저장소"""
    
    def __init__(self):
        self.data = {}
        self.timestamp = datetime.now().isoformat()
        # Streamlit Cloud에서 사용할 수 있는 임시 디렉토리
        self.cloud_data_dir = "/tmp/streamlit_cloud_data"
        self._ensure_cloud_directory()
    
    def _ensure_cloud_directory(self):
        """클라우드 데이터 디렉토리 생성"""
        try:
            if not os.path.exists(self.cloud_data_dir):
                os.makedirs(self.cloud_data_dir, exist_ok=True)
        except Exception as e:
            print(f"⚠️ 클라우드 디렉토리 생성 실패: {e}")
    
    def save(self, key: str, data: Any) -> bool:
        """세션 상태와 파일에 데이터 저장"""
        try:
            # 세션 상태에 저장
            self.data[key] = {
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            # 파일에도 저장 (영구 보존)
            file_path = os.path.join(self.cloud_data_dir, f"{key}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ 클라우드 저장 실패: {e}")
            return False
    
    def load(self, key: str) -> Any:
        """세션 상태 또는 파일에서 데이터 로드"""
        # 먼저 세션 상태에서 확인
        if key in self.data:
            return self.data[key].get('data', None)
        
        # 세션 상태에 없으면 파일에서 로드
        try:
            file_path = os.path.join(self.cloud_data_dir, f"{key}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    # 세션 상태에도 복원
                    self.data[key] = file_data
                    return file_data.get('data', None)
        except Exception as e:
            print(f"⚠️ 파일에서 데이터 로드 실패: {e}")
        
        return None
    
    def get_all_keys(self) -> List[str]:
        """저장된 모든 키 반환 (세션 + 파일)"""
        keys = set(self.data.keys())
        
        # 파일에서도 키 확인
        try:
            if os.path.exists(self.cloud_data_dir):
                for filename in os.listdir(self.cloud_data_dir):
                    if filename.endswith('.json'):
                        key = filename[:-5]  # .json 제거
                        keys.add(key)
        except Exception as e:
            print(f"⚠️ 파일 키 확인 실패: {e}")
        
        return list(keys)
    
    def clear_all(self):
        """모든 데이터 삭제 (세션 + 파일)"""
        try:
            # 세션 상태 클리어
            self.data.clear()
            
            # 파일도 삭제
            if os.path.exists(self.cloud_data_dir):
                for filename in os.listdir(self.cloud_data_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.cloud_data_dir, filename)
                        os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"❌ 클라우드 데이터 삭제 실패: {e}")
            return False

class MultiUserHistoryDB:
    def __init__(self, data_dir: str = "user_data"):
        """다중 사용자 이력 저장소 초기화"""
        # Streamlit Cloud 환경 감지
        self.is_cloud = self._is_streamlit_cloud()
        
        if self.is_cloud:
            print("☁️ Streamlit Cloud 환경 감지 - 영구 저장소 사용")
            self.cloud_storage = CloudDataStorage()
        else:
            print("💻 로컬 환경 감지 - 파일 시스템 사용")
            # 절대 경로로 변환
            if not os.path.isabs(data_dir):
                self.data_dir = os.path.join(os.getcwd(), data_dir)
            else:
                self.data_dir = data_dir
            self._ensure_data_directory()
    
    def _is_streamlit_cloud(self) -> bool:
        """Streamlit Cloud 환경인지 확인"""
        return os.getenv('STREAMLIT_SERVER_RUNNING') == 'true'
    
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
        """사용자별 이력 파일 경로"""
        if self.is_cloud:
            return f"cloud_history_{user_id}"
        return os.path.join(self.data_dir, f"history_{user_id}.json")
    
    def _get_global_history_file(self) -> str:
        """전체 이력 파일 경로"""
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
                print(f"✅ 이력 파일 생성: {file_path}")
            except Exception as e:
                print(f"⚠️ 이력 파일 생성 실패: {e}")
    
    def _load_history(self, file_path: str) -> List[Dict]:
        """이력 데이터 로드"""
        try:
            if self.is_cloud:
                # 클라우드 환경에서는 CloudDataStorage 사용
                data = self.cloud_storage.load(file_path)
                return data if data is not None else []
            else:
                # 로컬 환경에서는 파일에서 로드
                if not os.path.exists(file_path):
                    self._ensure_history_file(file_path)
                    return []
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 이력 로드 실패: {e}")
            return []
    
    def _save_history(self, history: List[Dict], file_path: str) -> bool:
        """이력 데이터 저장"""
        try:
            if self.is_cloud:
                # 클라우드 환경에서는 CloudDataStorage 사용
                return self.cloud_storage.save(file_path, history)
            else:
                # 로컬 환경에서는 파일에 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                return True
        except Exception as e:
            print(f"❌ 이력 저장 실패: {e}")
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
                
                issue_types = list(set([entry.get('issue_type', '') for entry in history]))
                response_types = list(set([entry.get('response_type', '') for entry in history]))
                
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
                
                users = list(set([f"{entry.get('user_name', '')}_{entry.get('user_role', '')}" for entry in history]))
                issue_types = list(set([entry.get('issue_type', '') for entry in history]))
                response_types = list(set([entry.get('response_type', '') for entry in history]))
                
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
                # 클라우드 환경에서는 CloudDataStorage 사용
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
                # 클라우드 환경에서는 CloudDataStorage 사용
                self.cloud_storage.clear_all()
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
