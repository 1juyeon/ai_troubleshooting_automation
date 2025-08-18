import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class HistoryDB:
    def __init__(self, history_file: str = "analysis_history.json"):
        """JSON 기반 이력 저장소 초기화"""
        # Streamlit Cloud 환경 감지
        self.is_cloud = self._is_streamlit_cloud()
        
        if self.is_cloud:
            # Streamlit Cloud에서 영구 저장소 경로 설정
            self.history_file = self._get_cloud_history_path(history_file)
            print(f"☁️ Streamlit Cloud 환경 - 영구 저장소 사용: {self.history_file}")
        else:
            self.history_file = history_file
            print(f"💻 로컬 환경 - 파일 시스템 사용: {self.history_file}")
        
        self._ensure_history_file()
    
    def _is_streamlit_cloud(self) -> bool:
        """Streamlit Cloud 환경인지 확인"""
        cloud_indicators = [
            os.getenv('STREAMLIT_SERVER_RUNNING') == 'true',
            os.getenv('STREAMLIT_CLOUD') == 'true',
            os.getenv('STREAMLIT_SERVER_PORT') == '8501',
            'streamlit.app' in os.getenv('STREAMLIT_SERVER_HEADLESS', ''),
            os.path.exists('/tmp/streamlit_data'),
            os.path.exists('/home/appuser')
        ]
        return any(cloud_indicators)
    
    def _get_cloud_history_path(self, filename: str) -> str:
        """Streamlit Cloud에서 영구 저장 가능한 경로 반환"""
        # 여러 가능한 영구 저장소 경로 시도
        possible_paths = [
            "/tmp/streamlit_data",
            "/home/appuser/streamlit_data", 
            "/app/streamlit_data",
            "./streamlit_data"
        ]
        
        for base_path in possible_paths:
            try:
                if not os.path.exists(base_path):
                    os.makedirs(base_path, exist_ok=True)
                
                # 쓰기 권한 테스트
                test_file = os.path.join(base_path, "test_write.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                
                full_path = os.path.join(base_path, filename)
                print(f"✅ 영구 저장소 경로 설정: {full_path}")
                return full_path
                
            except Exception as e:
                print(f"⚠️ 경로 {base_path} 사용 불가: {e}")
                continue
        
        # 모든 경로가 실패하면 현재 디렉토리 사용
        fallback_path = f"./streamlit_data/{filename}"
        try:
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            print(f"⚠️ 폴백 경로 사용: {fallback_path}")
            return fallback_path
        except Exception as e:
            print(f"❌ 폴백 경로도 실패: {e}")
            return filename
    
    def _ensure_history_file(self):
        """히스토리 파일이 존재하는지 확인하고 없으면 생성"""
        try:
            # 디렉토리가 존재하는지 확인
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            if not os.path.exists(self.history_file):
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                print(f"✅ 이력 파일 생성 완료: {self.history_file}")
            else:
                print(f"✅ 기존 이력 파일 확인: {self.history_file}")
                
        except Exception as e:
            print(f"❌ 이력 파일 생성 실패: {e}")
            # 폴백: 현재 디렉토리에 생성
            try:
                fallback_file = os.path.basename(self.history_file)
                with open(fallback_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                self.history_file = fallback_file
                print(f"⚠️ 폴백 경로에 이력 파일 생성: {fallback_file}")
            except Exception as e2:
                print(f"❌ 폴백 이력 파일 생성도 실패: {e2}")
    
    def _load_history(self) -> List[Dict]:
        """히스토리 데이터 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ 이력 데이터 로드 완료: {len(data)}개 항목")
                    return data
            else:
                print(f"⚠️ 이력 파일이 존재하지 않음: {self.history_file}")
                return []
                
        except Exception as e:
            print(f"❌ 이력 로드 실패: {e}")
            # 백업 파일에서 복구 시도
            try:
                backup_file = self.history_file + '.backup'
                if os.path.exists(backup_file):
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"✅ 백업 파일에서 복구 완료: {len(data)}개 항목")
                        return data
            except Exception as e2:
                print(f"❌ 백업 파일 복구도 실패: {e2}")
            
            return []
    
    def _save_history(self, history_data: List[Dict]):
        """히스토리 데이터 저장"""
        try:
            # 디렉토리가 존재하는지 확인
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # 임시 파일에 먼저 저장
            temp_file = self.history_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            
            # 백업 파일 생성
            if os.path.exists(self.history_file):
                backup_file = self.history_file + '.backup'
                try:
                    os.rename(self.history_file, backup_file)
                    print(f"✅ 백업 파일 생성: {backup_file}")
                except Exception as e:
                    print(f"⚠️ 백업 파일 생성 실패: {e}")
            
            # 원본 파일로 이동
            os.rename(temp_file, self.history_file)
            print(f"✅ 이력 데이터 저장 완료: {self.history_file}")
            return True
            
        except PermissionError as e:
            print(f"❌ 파일 권한 오류: {e}")
            print(f"파일 경로: {self.history_file}")
            return False
        except OSError as e:
            print(f"❌ 파일 시스템 오류: {e}")
            print(f"파일 경로: {self.history_file}")
            return False
        except Exception as e:
            print(f"❌ 이력 저장 실패: {e}")
            print(f"파일 경로: {self.history_file}")
            return False
    
    def create_backup(self) -> bool:
        """현재 이력 데이터의 백업 생성"""
        try:
            history_data = self._load_history()
            if not history_data:
                print("⚠️ 백업할 데이터가 없습니다.")
                return False
            
            backup_dir = os.path.join(os.path.dirname(self.history_file), "backup")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f"history_backup_{timestamp}.json")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 백업 생성 완료: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ 백업 생성 실패: {e}")
            return False
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """백업 파일에서 데이터 복구"""
        try:
            if not os.path.exists(backup_file):
                print(f"❌ 백업 파일이 존재하지 않음: {backup_file}")
                return False
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            if self._save_history(backup_data):
                print(f"✅ 백업에서 복구 완료: {len(backup_data)}개 항목")
                return True
            else:
                print("❌ 백업 복구 실패")
                return False
                
        except Exception as e:
            print(f"❌ 백업 복구 실패: {e}")
            return False
    
    def save_analysis(self, analysis_result: Dict, inquiry_data: Dict):
        """분석 결과 저장"""
        try:
            # 현재 이력 로드
            history = self._load_history()
            
            # 새로운 분석 결과 생성
            new_entry = {
                'id': len(history) + 1,
                'timestamp': inquiry_data.get('timestamp', datetime.now().isoformat()),
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
                'user_name': inquiry_data.get('user_name', ''),
                'user_role': inquiry_data.get('user_role', ''),
                'system_version': inquiry_data.get('system_version', ''),
                'browser_info': inquiry_data.get('browser_info', ''),
                'os_info': inquiry_data.get('os_info', ''),
                'error_code': inquiry_data.get('error_code', ''),
                'priority': inquiry_data.get('priority', ''),
                'contract_type': inquiry_data.get('contract_type', ''),
                'full_analysis_result': analysis_result
            }
            
            # 이력에 추가
            history.append(new_entry)
            
            # 저장
            if self._save_history(history):
                print("✅ 분석 결과가 JSON 파일에 저장되었습니다.")
                return {"success": True, "database": "json"}
            else:
                return {"success": False, "error": "저장 실패"}
                
        except Exception as e:
            print(f"❌ JSON 저장 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_history(self, limit: int = 50, offset: int = 0, 
                   issue_type: str = None, date_from: str = None, 
                   date_to: str = None, keyword: str = None,
                   user_name: str = None):
        """이력 조회"""
        try:
            history = self._load_history()
            
            # 필터링
            filtered_history = []
            for entry in history:
                # 문제 유형 필터
                if issue_type and entry.get('issue_type') != issue_type:
                    continue
                
                # 날짜 필터
                if date_from and entry.get('timestamp', '') < date_from:
                    continue
                if date_to:
                    # 종료 날짜를 포함하도록 수정 (시간까지 고려)
                    if entry.get('timestamp', '') > date_to:
                        continue
                
                # 키워드 필터
                if keyword:
                    content = entry.get('inquiry_content', '') + ' ' + entry.get('summary', '')
                    if keyword.lower() not in content.lower():
                        continue
                
                # 사용자 필터
                if user_name and entry.get('user_name', '') != user_name:
                    continue
                
                filtered_history.append(entry)
            
            # 정렬 (최신순)
            filtered_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # 페이징
            start_idx = offset
            end_idx = start_idx + limit
            result = filtered_history[start_idx:end_idx]
            
            # 튜플 형태로 변환 (기존 코드와 호환)
            tuples = []
            for entry in result:
                tuples.append((
                    entry.get('id'),
                    entry.get('timestamp'),
                    entry.get('customer_name'),
                    entry.get('customer_contact'),
                    entry.get('customer_manager'),
                    entry.get('inquiry_content'),
                    entry.get('issue_type'),
                    entry.get('classification_method'),
                    entry.get('confidence'),
                    entry.get('response_type'),
                    entry.get('summary'),
                    entry.get('action_flow'),
                    entry.get('email_draft'),
                    entry.get('user_name'),
                    entry.get('user_role'),
                    entry.get('system_version'),
                    entry.get('browser_info'),
                    entry.get('os_info'),
                    entry.get('error_code'),
                    entry.get('priority'),
                    entry.get('contract_type'),
                    json.dumps(entry.get('full_analysis_result', {}), ensure_ascii=False)
                ))
            
            return tuples
            
        except Exception as e:
            print(f"❌ JSON 조회 실패: {e}")
            return []
    
    def get_statistics(self):
        """통계 정보 조회"""
        try:
            history = self._load_history()
            
            # 총 건수
            total_count = len(history)
            
            # 최근 30일 건수
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            recent_count = len([entry for entry in history if entry.get('timestamp', '') >= thirty_days_ago])
            
            # 문제 유형별 분포
            issue_type_distribution = {}
            for entry in history:
                issue_type = entry.get('issue_type', '')
                if issue_type:
                    issue_type_distribution[issue_type] = issue_type_distribution.get(issue_type, 0) + 1
            
            # 사용자별 분포
            user_distribution = {}
            for entry in history:
                user_name = entry.get('user_name', '')
                if user_name:
                    user_distribution[user_name] = user_distribution.get(user_name, 0) + 1
            
            return {
                'total_count': total_count,
                'recent_count': recent_count,
                'issue_type_distribution': issue_type_distribution,
                'user_distribution': user_distribution
            }
            
        except Exception as e:
            print(f"❌ JSON 통계 조회 실패: {e}")
            return {
                'total_count': 0,
                'recent_count': 0,
                'issue_type_distribution': {},
                'user_distribution': {}
            } 