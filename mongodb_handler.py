import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz
import os

# .env 파일 로딩 (로컬 환경에서만)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env 파일 로드 완료")
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. 환경변수를 직접 설정해주세요.")

class MongoDBHandler:
    """MongoDB Atlas 연동 핸들러"""
    
    def __init__(self):
        """MongoDB 연결 초기화"""
        try:
            # 연결 문자열 가져오기 (Streamlit Secrets 우선, 환경변수 차선)
            if "MONGODB_URI" in st.secrets:
                self.connection_string = st.secrets["MONGODB_URI"]
                print("✅ MongoDB URI를 Streamlit Secrets에서 로드했습니다.")
            else:
                # 환경변수에서 로드
                import os
                self.connection_string = os.getenv("MONGODB_URI")
                if not self.connection_string:
                    raise ValueError("MONGODB_URI가 설정되지 않았습니다.")
                print("✅ MongoDB URI를 환경변수에서 로드했습니다.")
            
            # 연결 문자열 인코딩 문제 해결
            if self.connection_string:
                # 특수문자 인코딩 처리
                self.connection_string = self.connection_string.replace('%40', '@')
                
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=10000)
            
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
            print("💡 환경변수 MONGODB_URI를 설정하거나 Streamlit Secrets에 추가해주세요.")
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ MongoDB 연결 실패: {e}")
            print("💡 MongoDB Atlas 네트워크 접근 설정을 확인해주세요.")
            print("💡 IP 화이트리스트에 0.0.0.0/0 추가를 고려해주세요.")
            raise
        except Exception as e:
            print(f"❌ MongoDB 초기화 오류: {e}")
            print("💡 연결 문자열 형식과 인증 정보를 확인해주세요.")
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
    
    def test_connection(self) -> Dict[str, Any]:
        """MongoDB 연결 테스트"""
        try:
            # 연결 상태 확인
            self.client.admin.command('ping')
            
            # 데이터베이스 목록 조회
            db_list = self.client.list_database_names()
            
            # 컬렉션 목록 조회
            collections = self.db.list_collection_names()
            
            return {
                "success": True,
                "message": "MongoDB 연결 성공",
                "databases": db_list,
                "collections": collections,
                "current_db": self.db.name
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"MongoDB 연결 실패: {str(e)}",
                "error": str(e)
            }
    
    def save_analysis(self, analysis_data: Dict, inquiry_data: Dict) -> Dict:
        """분석 결과 저장"""
        try:
            # 저장할 데이터 구성
            # 파싱된 데이터 추출 (여러 구조 지원)
            parsed_data = None
            response_type = ""
            summary = ""
            action_flow = ""
            email_draft = ""
            
            # Gemini 응답 구조 확인
            if 'parsed_response' in analysis_data:
                # analysis_result에 직접 포함된 경우
                parsed_data = analysis_data['parsed_response']
            elif 'gemini_result' in analysis_data and 'parsed_response' in analysis_data['gemini_result']:
                parsed_data = analysis_data['gemini_result']['parsed_response']
                # Gemini 응답에서 raw_response가 있으면 GPT와 동일한 방식으로 파싱
                if 'raw_response' in analysis_data['gemini_result']:
                    try:
                        raw_parsed = self._parse_gpt_response(analysis_data['gemini_result']['raw_response'])
                        # raw_response 파싱 결과가 더 좋으면 사용
                        if raw_parsed.get('summary') and raw_parsed.get('action_flow') and raw_parsed.get('email_draft'):
                            parsed_data = raw_parsed
                    except Exception as e:
                        print(f"Gemini raw_response 파싱 실패: {e}")
            elif 'gpt_result' in analysis_data and 'parsed_response' in analysis_data['gpt_result']:
                parsed_data = analysis_data['gpt_result']['parsed_response']
                # GPT 응답에서 raw_response가 있으면 파싱
                if 'raw_response' in analysis_data['gpt_result']:
                    try:
                        raw_parsed = self._parse_gpt_response(analysis_data['gpt_result']['raw_response'])
                        # raw_response 파싱 결과가 더 좋으면 사용
                        if raw_parsed.get('summary') and raw_parsed.get('action_flow') and raw_parsed.get('email_draft'):
                            parsed_data = raw_parsed
                    except Exception as e:
                        print(f"GPT raw_response 파싱 실패: {e}")
            elif 'ai_result' in analysis_data:
                ai_result = analysis_data['ai_result']
                
                if 'gemini_result' in ai_result and 'parsed_response' in ai_result['gemini_result']:
                    parsed_data = ai_result['gemini_result']['parsed_response']
                    # Gemini 응답에서 raw_response가 있으면 GPT와 동일한 방식으로 파싱
                    if 'raw_response' in ai_result['gemini_result']:
                        try:
                            raw_parsed = self._parse_gpt_response(ai_result['gemini_result']['raw_response'])
                            # raw_response 파싱 결과가 더 좋으면 사용
                            if raw_parsed.get('summary') and raw_parsed.get('action_flow') and raw_parsed.get('email_draft'):
                                parsed_data = raw_parsed
                        except Exception as e:
                            print(f"Gemini raw_response 파싱 실패: {e}")
                elif 'gpt_result' in ai_result and 'parsed_response' in ai_result['gpt_result']:
                    parsed_data = ai_result['gpt_result']['parsed_response']
                    # GPT 응답에서 raw_response가 있으면 파싱
                    if 'raw_response' in ai_result['gpt_result']:
                        try:
                            raw_parsed = self._parse_gpt_response(ai_result['gpt_result']['raw_response'])
                            # raw_response 파싱 결과가 더 좋으면 사용
                            if raw_parsed.get('summary') and raw_parsed.get('action_flow') and raw_parsed.get('email_draft'):
                                parsed_data = raw_parsed
                        except Exception as e:
                            print(f"GPT raw_response 파싱 실패: {e}")
                elif 'parsed_response' in ai_result:
                    parsed_data = ai_result['parsed_response']
                elif 'response' in ai_result:
                    # 기존 GPT API 응답인 경우 파싱
                    parsed_data = self._parse_gpt_response(ai_result['response'])
            
            # 파싱된 데이터에서 정보 추출
            if parsed_data and isinstance(parsed_data, dict):
                response_type = parsed_data.get('response_type', '')
                summary = parsed_data.get('summary', '')
                action_flow = parsed_data.get('action_flow', '')
                email_draft = parsed_data.get('email_draft', '')
                
                # 빈 값 검증 및 기본값 설정
                if not response_type or len(response_type.strip()) < 2:
                    response_type = "해결안"
                if not summary or len(summary.strip()) < 5:
                    summary = "AI 분석 결과를 파싱할 수 없습니다. 고객 문의 내용을 확인해주세요."
                if not action_flow or len(action_flow.strip()) < 10:
                    action_flow = "AI 분석 결과를 파싱할 수 없습니다. 단계별 조치 사항을 확인해주세요."
                if not email_draft or len(email_draft.strip()) < 20:
                    email_draft = "AI 분석 결과를 파싱할 수 없습니다. 이메일 초안을 확인해주세요."
            else:
                # 파싱된 데이터가 없는 경우 기본값 사용
                response_type = "해결안"
                summary = "AI 분석 결과를 파싱할 수 없습니다. 고객 문의 내용을 확인해주세요."
                action_flow = "AI 분석 결과를 파싱할 수 없습니다. 단계별 조치 사항을 확인해주세요."
                email_draft = "AI 분석 결과를 파싱할 수 없습니다. 이메일 초안을 확인해주세요."
            
            # 원본 AI 응답도 함께 저장 (나중에 파싱 복원을 위해)
            original_ai_response = None
            if 'ai_result' in analysis_data:
                ai_result = analysis_data['ai_result']
                if 'gemini_result' in ai_result and 'raw_response' in ai_result['gemini_result']:
                    original_ai_response = ai_result['gemini_result']['raw_response']
                elif 'gpt_result' in ai_result and 'raw_response' in ai_result['gpt_result']:
                    original_ai_response = ai_result['gpt_result']['raw_response']
                elif 'response' in ai_result:
                    original_ai_response = ai_result['response']
            elif 'gemini_result' in analysis_data and 'raw_response' in analysis_data['gemini_result']:
                original_ai_response = analysis_data['gemini_result']['raw_response']
            elif 'gpt_result' in analysis_data and 'raw_response' in analysis_data['gpt_result']:
                original_ai_response = analysis_data['gpt_result']['raw_response']
            
            document = {
                'timestamp': inquiry_data.get('timestamp', datetime.now().isoformat()),
                'customer_name': inquiry_data.get('customer_name', ''),
                'customer_contact': inquiry_data.get('customer_contact', ''),
                'customer_manager': inquiry_data.get('customer_manager', ''),
                'inquiry_content': inquiry_data.get('inquiry_content', ''),
                'issue_type': analysis_data.get('issue_type', ''),
                'classification_method': analysis_data.get('classification', {}).get('method', ''),
                'confidence': analysis_data.get('classification', {}).get('confidence', ''),
                'response_type': response_type,
                'summary': summary,
                'action_flow': action_flow,
                'email_draft': email_draft,
                'user_name': inquiry_data.get('user_name', ''),
                'user_role': inquiry_data.get('user_role', ''),
                'system_version': inquiry_data.get('system_version', ''),
                'browser_info': inquiry_data.get('browser_info', ''),
                'os_info': inquiry_data.get('os_info', ''),
                'error_code': inquiry_data.get('error_code', ''),
                'priority': inquiry_data.get('priority', ''),
                'contract_type': inquiry_data.get('contract_type', ''),
                'full_analysis_result': analysis_data,
                'original_ai_response': original_ai_response,  # 원본 AI 응답 저장
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
    
    def _parse_gpt_response(self, response_text: str) -> dict:
        """GPT API 응답을 파싱하여 구조화된 데이터로 변환"""
        try:
            parsed = {
                'response_type': '해결안',
                'summary': '',
                'action_flow': '',
                'email_draft': '',
                'question': ''
            }
            
            # 응답 텍스트를 줄 단위로 분리
            lines = response_text.split('\n')
            current_section = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                # 섹션 헤더 확인
                if '[대응유형]' in line:
                    response_type = line.replace('[대응유형]', '').strip()
                    if response_type in ['해결안', '질문', '출동']:
                        parsed['response_type'] = response_type
                elif '[응답내용]' in line:
                    current_section = 'content'
                elif '- 요약:' in line:
                    current_section = 'summary'
                    # 요약 내용이 같은 줄에 있는 경우
                    summary_content = line.replace('- 요약:', '').strip()
                    if summary_content:
                        parsed['summary'] = summary_content
                    # 다음 줄에 요약 내용이 있는지 확인
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not any(keyword in next_line for keyword in ['- 조치 흐름:', '- 이메일 초안:', '[응답내용]', '[대응유형]']):
                            if parsed['summary']:
                                parsed['summary'] += ' ' + next_line
                            else:
                                parsed['summary'] = next_line
                elif '- 조치 흐름:' in line:
                    current_section = 'action_flow'
                elif '- 이메일 초안:' in line:
                    current_section = 'email_draft'
                elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                    # 조치 흐름 항목
                    if current_section == 'action_flow':
                        parsed['action_flow'] += line + '\n'
                elif current_section == 'summary':
                    if parsed['summary']:  # 이미 내용이 있으면 공백 추가
                        parsed['summary'] += ' ' + line
                    else:
                        parsed['summary'] = line
                elif current_section == 'action_flow':
                    # 조치 흐름에서 불필요한 텍스트 제거
                    if not any(unwanted in line for unwanted in [
                        '[응답내용]', '[대응유형]', '- 요약:', '- 조치 흐름:', '- 이메일 초안:',
                        '아래 형식을 참고하여', '실무자가 이해하기 쉽도록', '자연스럽고 정확하게 응답을 생성하십시오'
                    ]):
                        parsed['action_flow'] += line + '\n'
                elif current_section == 'email_draft':
                    # 이메일 초안에서 불필요한 텍스트 제거
                    if not any(unwanted in line for unwanted in [
                        '[응답내용]', '[대응유형]', '- 요약:', '- 조치 흐름:', '- 이메일 초안:',
                        '아래 형식을 참고하여', '실무자가 이해하기 쉽도록', '자연스럽고 정확하게 응답을 생성하십시오'
                    ]):
                        parsed['email_draft'] += line + '\n'
            
            # 요약에서 "- 요약:" 제거 (혹시 남아있을 경우)
            parsed['summary'] = parsed['summary'].replace('- 요약:', '').strip()
            
            # 파싱 실패 시 기본값 설정
            if not parsed['summary'] or len(parsed['summary'].strip()) < 5:
                parsed['summary'] = "AI 분석 결과를 파싱할 수 없습니다. 고객 문의 내용을 확인해주세요."
            if not parsed['action_flow'] or len(parsed['action_flow'].strip()) < 10:
                parsed['action_flow'] = "AI 분석 결과를 파싱할 수 없습니다. 단계별 조치 사항을 확인해주세요."
            if not parsed['email_draft'] or len(parsed['email_draft'].strip()) < 20:
                parsed['email_draft'] = "AI 분석 결과를 파싱할 수 없습니다. 이메일 초안을 확인해주세요."
            
            # 디버깅을 위한 로그 추가
            print(f"MongoDB GPT 파싱 결과 - 요약: {parsed['summary'][:50]}...")
            print(f"MongoDB GPT 파싱 결과 - 조치 흐름: {parsed['action_flow'][:50]}...")
            print(f"MongoDB GPT 파싱 결과 - 이메일 초안: {parsed['email_draft'][:50]}...")
            
            return parsed
            
        except Exception as e:
            print(f"GPT 응답 파싱 오류: {e}")
            return {
                'response_type': '해결안',
                'summary': '응답 파싱 중 오류가 발생했습니다.',
                'action_flow': '응답을 확인해주세요.',
                'email_draft': '응답을 확인해주세요.',
                'question': '',
                'full_response': response_text
            }
    
    def get_history(self, user_id: str = None, limit: int = 100, skip: int = 0, date_from: str = None, date_to: str = None, issue_type: str = None) -> List[Dict]:
        """이력 조회 (날짜 범위, 문제 유형, 담당자 필터링 지원)"""
        try:
            # 쿼리 조건 구성
            query = {}
            
            # 담당자 필터링
            if user_id:
                query['user_name'] = user_id
            
            # 날짜 범위 필터링
            if date_from or date_to:
                date_query = {}
                if date_from:
                    try:
                        start_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                        date_query['$gte'] = start_dt.isoformat()
                    except:
                        # 날짜 파싱 실패 시 원본 문자열로 검색
                        date_query['$gte'] = date_from
                
                if date_to:
                    try:
                        end_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                        date_query['$lte'] = end_dt.isoformat()
                    except:
                        # 날짜 파싱 실패 시 원본 문자열로 검색
                        date_query['$lte'] = date_to
                
                query['timestamp'] = date_query
            
            # 문제 유형 필터링
            if issue_type and issue_type != "전체":
                query['issue_type'] = issue_type
            
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
            
            print(f"✅ MongoDB에서 {len(results)}개 이력 조회 완료 (필터: {query})")
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
    
    def get_analysis_by_criteria(self, customer_name: str = None, issue_type: str = None, user_name: str = None, date: str = None) -> Dict:
        """특정 조건에 맞는 AI 분석 결과 조회"""
        try:
            # 쿼리 조건 구성
            query = {}
            
            if customer_name and customer_name.strip():
                query['customer_name'] = customer_name.strip()
            
            if issue_type and issue_type.strip():
                query['issue_type'] = issue_type.strip()
            
            if user_name and user_name.strip():
                query['user_name'] = user_name.strip()
            
            if date and date.strip():
                # 날짜 형식 변환 (YYYY-MM-DD -> YYYY-MM-DDTHH:MM:SS)
                try:
                    date_obj = datetime.strptime(date.strip(), '%Y-%m-%d')
                    start_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # ISO 형식으로 변환
                    query['timestamp'] = {
                        '$gte': start_date.isoformat(),
                        '$lte': end_date.isoformat()
                    }
                except ValueError:
                    # 날짜 파싱 실패 시 원본 문자열로 검색
                    query['timestamp'] = {'$regex': date.strip()}
            
            # MongoDB에서 데이터 조회
            cursor = self.history_collection.find(query).sort("timestamp", -1).limit(1)
            
            results = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                if 'created_at' in doc:
                    doc['created_at'] = doc['created_at'].isoformat()
                if 'updated_at' in doc:
                    doc['updated_at'] = doc['updated_at'].isoformat()
                results.append(doc)
            
            if results:
                print(f"✅ MongoDB에서 조건별 분석 결과 조회 완료: {len(results)}개")
                return {
                    "success": True,
                    "data": results[0],  # 가장 최근 결과 반환
                    "source": "mongodb"
                }
            else:
                print(f"⚠️ 조건에 맞는 분석 결과를 찾을 수 없습니다")
                return {
                    "success": False,
                    "error": "조건에 맞는 분석 결과를 찾을 수 없습니다",
                    "source": "mongodb"
                }
            
        except Exception as e:
            print(f"❌ MongoDB 조건별 분석 결과 조회 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "mongodb"
            }
    
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
