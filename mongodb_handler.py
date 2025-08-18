import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz

class MongoDBHandler:
    """MongoDB Atlas 연동 핸들러"""
    
    def __init__(self):
        """MongoDB 연결 초기화"""
        try:
            # Streamlit Secrets에서 MongoDB 연결 문자열 가져오기
            self.connection_string = st.secrets["MONGODB_URI"]
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            
            # 연결 문자열에서 데이터베이스 이름 추출
            if '/sample_mflix' in self.connection_string:
                self.db = self.client.sample_mflix
            elif '/privkeeper_db' in self.connection_string:
                self.db = self.client.privkeeper_db
            else:
                # 기본값으로 privkeeper_db 사용
                self.db = self.client.privkeeper_db
            
            self.history_collection = self.db.analysis_history
            self.users_collection = self.db.users
            
            # 연결 테스트
            self.client.admin.command('ping')
            print("✅ MongoDB Atlas 연결 성공")
            
            # 인덱스 생성 (성능 최적화)
            self._create_indexes()
            
        except KeyError:
            print("❌ MONGODB_URI가 Streamlit Secrets에 설정되지 않았습니다.")
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ MongoDB 연결 실패: {e}")
            raise
        except Exception as e:
            print(f"❌ MongoDB 초기화 오류: {e}")
            raise
    
    def _create_indexes(self):
        """데이터베이스 인덱스 생성"""
        try:
            # 타임스탬프 기반 정렬을 위한 인덱스
            self.history_collection.create_index([("timestamp", -1)])
            # 사용자별 조회를 위한 인덱스
            self.history_collection.create_index([("user_id", 1)])
            # 고객사별 조회를 위한 인덱스
            self.history_collection.create_index([("customer_name", 1)])
            # 문제 유형별 조회를 위한 인덱스
            self.history_collection.create_index([("issue_type", 1)])
            print("✅ MongoDB 인덱스 생성 완료")
        except Exception as e:
            print(f"⚠️ 인덱스 생성 실패: {e}")
    
    def save_analysis(self, analysis_data: Dict, inquiry_data: Dict) -> Dict:
        """분석 결과 저장"""
        try:
            # 저장할 데이터 구성
            document = {
                'timestamp': inquiry_data.get('timestamp', datetime.now().isoformat()),
                'customer_name': inquiry_data.get('customer_name', ''),
                'customer_contact': inquiry_data.get('customer_contact', ''),
                'customer_manager': inquiry_data.get('customer_manager', ''),
                'inquiry_content': inquiry_data.get('inquiry_content', ''),
                'issue_type': analysis_data.get('issue_type', ''),
                'classification_method': analysis_data.get('classification', {}).get('method', ''),
                'confidence': analysis_data.get('classification', {}).get('confidence', ''),
                'response_type': analysis_data.get('gemini_result', {}).get('parsed_response', {}).get('response_type', ''),
                'summary': analysis_data.get('gemini_result', {}).get('parsed_response', {}).get('summary', ''),
                'action_flow': analysis_data.get('gemini_result', {}).get('parsed_response', {}).get('action_flow', ''),
                'email_draft': analysis_data.get('gemini_result', {}).get('parsed_response', {}).get('email_draft', ''),
                'user_name': inquiry_data.get('user_name', ''),
                'user_role': inquiry_data.get('user_role', ''),
                'system_version': inquiry_data.get('system_version', ''),
                'browser_info': inquiry_data.get('browser_info', ''),
                'os_info': inquiry_data.get('os_info', ''),
                'error_code': inquiry_data.get('error_code', ''),
                'priority': inquiry_data.get('priority', ''),
                'contract_type': inquiry_data.get('contract_type', ''),
                'full_analysis_result': analysis_data,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # MongoDB에 저장
            result = self.history_collection.insert_one(document)
            
            print(f"✅ MongoDB에 분석 결과 저장 완료 (ID: {result.inserted_id})")
            return {
                "success": True, 
                "database": "mongodb",
                "id": str(result.inserted_id)
            }
            
        except Exception as e:
            print(f"❌ MongoDB 저장 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_history(self, user_id: str = None, limit: int = 100, skip: int = 0) -> List[Dict]:
        """이력 조회"""
        try:
            # 쿼리 조건 구성
            query = {}
            if user_id:
                query['user_name'] = user_id
            
            # MongoDB에서 데이터 조회
            cursor = self.history_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
            
            # ObjectId를 문자열로 변환
            results = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                # datetime 객체를 문자열로 변환
                if 'created_at' in doc:
                    doc['created_at'] = doc['created_at'].isoformat()
                if 'updated_at' in doc:
                    doc['updated_at'] = doc['updated_at'].isoformat()
                results.append(doc)
            
            print(f"✅ MongoDB에서 {len(results)}개 이력 조회 완료")
            return results
            
        except Exception as e:
            print(f"❌ MongoDB 조회 실패: {e}")
            return []
    
    def get_history_by_date_range(self, start_date: str, end_date: str, user_id: str = None) -> List[Dict]:
        """날짜 범위별 이력 조회"""
        try:
            # 날짜 파싱
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # 쿼리 조건 구성
            query = {
                'timestamp': {
                    '$gte': start_dt.isoformat(),
                    '$lte': end_dt.isoformat()
                }
            }
            if user_id:
                query['user_name'] = user_id
            
            # MongoDB에서 데이터 조회
            cursor = self.history_collection.find(query).sort("timestamp", -1)
            
            results = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                if 'created_at' in doc:
                    doc['created_at'] = doc['created_at'].isoformat()
                if 'updated_at' in doc:
                    doc['updated_at'] = doc['updated_at'].isoformat()
                results.append(doc)
            
            print(f"✅ MongoDB에서 날짜 범위별 {len(results)}개 이력 조회 완료")
            return results
            
        except Exception as e:
            print(f"❌ MongoDB 날짜 범위 조회 실패: {e}")
            return []
    
    def delete_history(self, history_id: str) -> Dict:
        """특정 이력 삭제"""
        try:
            from bson import ObjectId
            
            result = self.history_collection.delete_one({"_id": ObjectId(history_id)})
            
            if result.deleted_count > 0:
                print(f"✅ MongoDB에서 이력 삭제 완료 (ID: {history_id})")
                return {"success": True, "deleted_count": result.deleted_count}
            else:
                print(f"⚠️ 삭제할 이력을 찾을 수 없습니다 (ID: {history_id})")
                return {"success": False, "error": "이력을 찾을 수 없습니다"}
                
        except Exception as e:
            print(f"❌ MongoDB 이력 삭제 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_statistics(self) -> Dict:
        """통계 정보 조회"""
        try:
            # 전체 이력 수
            total_count = self.history_collection.count_documents({})
            
            # 사용자별 이력 수
            user_stats = list(self.history_collection.aggregate([
                {"$group": {"_id": "$user_name", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            # 문제 유형별 통계
            issue_stats = list(self.history_collection.aggregate([
                {"$group": {"_id": "$issue_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            # 최근 7일 이력 수
            week_ago = datetime.now() - timedelta(days=7)
            recent_count = self.history_collection.count_documents({
                "created_at": {"$gte": week_ago}
            })
            
            return {
                "total_count": total_count,
                "recent_count": recent_count,
                "user_stats": user_stats,
                "issue_stats": issue_stats
            }
            
        except Exception as e:
            print(f"❌ MongoDB 통계 조회 실패: {e}")
            return {}
    
    def close_connection(self):
        """MongoDB 연결 종료"""
        try:
            self.client.close()
            print("✅ MongoDB 연결 종료")
        except Exception as e:
            print(f"⚠️ MongoDB 연결 종료 실패: {e}")
