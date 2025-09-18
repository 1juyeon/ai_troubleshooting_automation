import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np

# ChromaDB 안전하게 임포트
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
    print("✅ ChromaDB 임포트 성공")
except ImportError as e:
    print(f"⚠️ ChromaDB 임포트 실패: {e}")
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None
except Exception as e:
    print(f"⚠️ ChromaDB 임포트 오류 (무시됨): {e}")
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

# sentence-transformers 의존성 제거 - ChromaDB 기본 임베딩 함수 사용
SENTENCE_TRANSFORMERS_AVAILABLE = False
SentenceTransformer = None

# ChromaDB 기본 임베딩 함수만 사용
try:
    from chromadb.utils import embedding_functions
    CHROMADB_EMBEDDING_AVAILABLE = True
    print("✅ ChromaDB 임베딩 함수 사용 가능")
except ImportError as e:
    print(f"⚠️ ChromaDB 임베딩 함수 사용 불가: {e}")
    CHROMADB_EMBEDDING_AVAILABLE = False

class ChromaVectorClassifier:
    def __init__(self, persist_directory: str = "chroma_issue_classification"):
        """Chroma 기반 벡터 분류기 초기화"""
        self.persist_directory = persist_directory
        self.issue_types = [
            "현재 비밀번호가 맞지 않습니다",
            "VMS와의 통신에 실패했습니다", 
            "Ping 테스트에 실패했습니다",
            "Onvif 응답이 없습니다",
            "로그인 차단 상태입니다",
            "비밀번호 변경에 실패했습니다",
            "PK P 계정 로그인 안됨",
            "PK P 웹 접속 안됨",
            "기타"
        ]
        
        # 의존성 확인 (ChromaDB만 필요)
        if not CHROMADB_AVAILABLE:
            print("❌ ChromaDB가 없어 벡터 분류기를 초기화할 수 없습니다.")
            self.client = None
            self.embedding_model = None
            self.collection = None
            return
        
        # Chroma 클라이언트 초기화 (의존성 문제 해결)
        try:
            # 의존성 문제 해결을 위한 환경 변수 설정
            import os
            os.environ["CHROMA_DISABLE_ONNXRUNTIME"] = "1"
            os.environ["CHROMA_DISABLE_IMPORT_ONNXRUNTIME"] = "1"
            os.environ["CHROMA_DISABLE_TELEMETRY"] = "1"
            os.environ["CHROMA_DISABLE_IMPORT_ONNXRUNTIME"] = "1"
            
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            print("✅ Chroma 클라이언트 초기화 성공 (onnxruntime 비활성화)")
        except Exception as e:
            print(f"❌ Chroma 클라이언트 초기화 실패: {e}")
            self.client = None
        
        # 임베딩 모델 초기화 (ChromaDB 기본 임베딩 함수 사용)
        try:
            from chromadb.utils import embedding_functions
            self.embedding_model = embedding_functions.DefaultEmbeddingFunction()
            print("✅ ChromaDB 기본 임베딩 함수 사용")
        except Exception as e:
            print(f"❌ ChromaDB 기본 임베딩 함수 초기화 실패: {e}")
            # 임베딩 함수 없이도 ChromaDB 사용 가능
            self.embedding_model = None
            print("⚠️ 임베딩 함수 없이 ChromaDB 사용")
        
        # 컬렉션 초기화
        self.collection = None
        self._initialize_collection()
        
        # 초기 데이터가 없으면 샘플 데이터 추가
        if self.collection and self.collection.count() == 0:
            self._add_sample_data()
    
    def _initialize_collection(self):
        """컬렉션 초기화 (ChromaDB 기본 임베딩 함수 사용)"""
        try:
            if self.client:
                if self.embedding_model:
                    # ChromaDB 기본 임베딩 함수 사용
                    self.collection = self.client.get_or_create_collection(
                        name="issue_classification",
                        metadata={"description": "문제 유형 분류를 위한 벡터 데이터베이스"},
                        embedding_function=self.embedding_model
                    )
                    print("✅ Chroma 컬렉션 초기화 성공 (기본 임베딩 함수)")
                else:
                    # 임베딩 모델이 없는 경우 기본 설정 사용
                    self.collection = self.client.get_or_create_collection(
                        name="issue_classification",
                        metadata={"description": "문제 유형 분류를 위한 벡터 데이터베이스"}
                    )
                    print("✅ Chroma 컬렉션 초기화 성공 (기본 설정)")
            else:
                print("❌ Chroma 클라이언트가 없어 컬렉션을 초기화할 수 없습니다.")
        except Exception as e:
            print(f"❌ 컬렉션 초기화 실패: {e}")
            self.collection = None
    
    def _add_sample_data(self):
        """문제 유형별 샘플 데이터 추가"""
        sample_data = {
            "현재 비밀번호가 맞지 않습니다": [
                "CCTV 웹 접속 시 비밀번호 인증 실패",
                "저장된 비밀번호로 로그인이 안됩니다",
                "비밀번호를 정확히 입력했는데도 인증 오류가 발생합니다",
                "CCTV 웹 로그인 시 접속 실패",
                "패스워드가 맞지 않아 로그인할 수 없습니다",
                "웹 접속 시 인증 실패가 계속 발생합니다"
            ],
            "VMS와의 통신에 실패했습니다": [
                "VMS 서버와의 연결이 안됩니다",
                "VMS 패스워드가 맞지 않습니다",
                "SVMS 통신 오류가 발생합니다",
                "NVR과 VMS 간 통신 실패",
                "VMS 설정에서 연결 오류가 발생합니다",
                "VMS 서버 연결이 끊어졌습니다"
            ],
            "Ping 테스트에 실패했습니다": [
                "네트워크 연결이 안됩니다",
                "Ping 테스트에서 응답이 없습니다",
                "네트워크 통신이 불안정합니다",
                "연결 상태를 확인할 수 없습니다",
                "네트워크 점검에서 실패가 발생합니다",
                "통신 테스트에 실패했습니다"
            ],
            "Onvif 응답이 없습니다": [
                "Onvif 프로토콜 응답이 없습니다",
                "카메라와 Onvif 통신이 안됩니다",
                "Onvif 설정에서 연결 오류가 발생합니다",
                "HTTP/HTTPS 프로토콜 응답이 없습니다",
                "카메라 통신 프로토콜 오류",
                "Onvif 서비스가 응답하지 않습니다"
            ],
            "로그인 차단 상태입니다": [
                "CCTV 로그인이 차단되었습니다",
                "비밀번호 변경 후 로그인 차단 상태입니다",
                "계정이 차단되어 로그인할 수 없습니다",
                "CCTV 차단 상태로 접속이 안됩니다",
                "로그인 시도가 차단되었습니다",
                "비밀번호 변경으로 인한 차단 상태입니다"
            ],
            "비밀번호 변경에 실패했습니다": [
                "비밀번호 변경이 안됩니다",
                "패스워드 수정에 실패했습니다",
                "비밀번호 업데이트 오류가 발생합니다",
                "비밀번호 변경 시 오류가 발생합니다",
                "패스워드 변경 프로세스가 실패했습니다",
                "비밀번호 수정이 제대로 되지 않습니다"
            ],
            "PK P 계정 로그인 안됨": [
                "PK P 계정으로 로그인이 안됩니다",
                "30일 미접속으로 계정이 잠겼습니다",
                "PK P 계정이 잠겨있습니다",
                "계정 로그인에 실패합니다",
                "PK P 계정 인증이 안됩니다",
                "계정 접속이 차단되었습니다"
            ],
            "PK P 웹 접속 안됨": [
                "PK P 웹사이트에 접속이 안됩니다",
                "톰캣 서비스가 중단되었습니다",
                "PK P 웹 서비스가 응답하지 않습니다",
                "웹 접속 시 연결 오류가 발생합니다",
                "PK P 웹 페이지가 로드되지 않습니다",
                "웹 서비스 접속에 실패합니다"
            ],
            "기타": [
                "알 수 없는 오류가 발생했습니다",
                "기타 문제가 발생했습니다",
                "예상치 못한 오류가 발생했습니다",
                "문제를 파악할 수 없습니다",
                "기타 기술적 문제가 발생했습니다",
                "분류되지 않는 문제입니다"
            ]
        }
        
        try:
            if self.collection and self.embedding_model:
                documents = []
                metadatas = []
                ids = []
                
                for issue_type, samples in sample_data.items():
                    for i, sample in enumerate(samples):
                        documents.append(sample)
                        metadatas.append({
                            "issue_type": issue_type,
                            "sample_index": i,
                            "is_sample": True
                        })
                        ids.append(f"{issue_type}_{i}")
                
                # 벡터 임베딩 생성
                embeddings = self.embedding_model.encode(documents).tolist()
                
                # Chroma에 추가
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
                
                print(f"✅ 샘플 데이터 추가 완료: {len(documents)}개 문서")
                return True
                
        except Exception as e:
            print(f"❌ 샘플 데이터 추가 실패: {e}")
            return False
    
    def classify_issue(self, customer_input: str, top_k: int = 3) -> Dict[str, Any]:
        """벡터 기반 문제 유형 분류"""
        try:
            if not self.collection or not self.embedding_model:
                return {
                    'issue_type': '기타',
                    'method': 'vector_based',
                    'confidence': 'low',
                    'error': '벡터 분류 시스템이 초기화되지 않았습니다.'
                }
            
            # 입력 텍스트 임베딩
            query_embedding = self.embedding_model.encode([customer_input]).tolist()[0]
            
            # 유사한 문서 검색
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['metadatas', 'distances', 'documents']
            )
            
            if not results['metadatas'] or not results['metadatas'][0]:
                return {
                    'issue_type': '기타',
                    'method': 'vector_based',
                    'confidence': 'low',
                    'error': '검색 결과가 없습니다.'
                }
            
            # 결과 분석
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            documents = results['documents'][0]
            
            # 거리를 유사도 점수로 변환 (거리가 작을수록 유사도 높음)
            similarities = [1 - distance for distance in distances]
            
            # 문제 유형별 점수 집계
            issue_scores = {}
            for i, metadata in enumerate(metadatas):
                issue_type = metadata['issue_type']
                similarity = similarities[i]
                
                if issue_type not in issue_scores:
                    issue_scores[issue_type] = []
                issue_scores[issue_type].append(similarity)
            
            # 각 문제 유형의 최고 점수 계산
            best_issue_type = '기타'
            best_score = 0
            
            for issue_type, scores in issue_scores.items():
                max_score = max(scores)
                if max_score > best_score:
                    best_score = max_score
                    best_issue_type = issue_type
            
            # 신뢰도 결정
            if best_score >= 0.8:
                confidence = 'high'
            elif best_score >= 0.6:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return {
                'issue_type': best_issue_type,
                'method': 'vector_based',
                'confidence': confidence,
                'similarity_score': best_score,
                'all_scores': issue_scores,
                'top_matches': [
                    {
                        'document': documents[i],
                        'issue_type': metadatas[i]['issue_type'],
                        'similarity': similarities[i]
                    }
                    for i in range(len(metadatas))
                ]
            }
            
        except Exception as e:
            print(f"❌ 벡터 분류 실패: {e}")
            return {
                'issue_type': '기타',
                'method': 'vector_based',
                'confidence': 'low',
                'error': str(e)
            }
    
    def add_training_data(self, customer_input: str, issue_type: str, metadata: Dict[str, Any] = None):
        """새로운 학습 데이터 추가"""
        try:
            if not self.collection or not self.embedding_model:
                return False
            
            # 메타데이터 구성
            if metadata is None:
                metadata = {}
            metadata.update({
                'issue_type': issue_type,
                'is_sample': False,
                'added_timestamp': str(pd.Timestamp.now())
            })
            
            # 임베딩 생성
            embedding = self.embedding_model.encode([customer_input]).tolist()[0]
            
            # 고유 ID 생성
            doc_id = f"training_{len(self.collection.get()['ids'])}"
            
            # Chroma에 추가
            self.collection.add(
                documents=[customer_input],
                metadatas=[metadata],
                ids=[doc_id],
                embeddings=[embedding]
            )
            
            print(f"✅ 학습 데이터 추가 완료: {issue_type}")
            return True
            
        except Exception as e:
            print(f"❌ 학습 데이터 추가 실패: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """벡터 DB 통계"""
        try:
            if not self.collection:
                return {
                    'total_documents': 0,
                    'issue_types': [],
                    'collection_name': 'issue_classification'
                }
            
            # 전체 문서 수
            total_docs = self.collection.count()
            
            # 문제 유형별 통계
            all_data = self.collection.get()
            issue_type_counts = {}
            
            if all_data['metadatas']:
                for metadata in all_data['metadatas']:
                    issue_type = metadata.get('issue_type', '기타')
                    issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
            
            return {
                'total_documents': total_docs,
                'issue_types': list(issue_type_counts.keys()),
                'issue_type_counts': issue_type_counts,
                'collection_name': 'issue_classification',
                'embedding_model': 'ko-sroberta-multitask' if self.embedding_model else 'None'
            }
            
        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")
            return {
                'total_documents': 0,
                'issue_types': [],
                'collection_name': 'issue_classification',
                'error': str(e)
            }
    
    def clear_database(self):
        """벡터 DB 초기화"""
        try:
            if self.collection:
                # 컬렉션 삭제
                self.client.delete_collection("issue_classification")
                # 컬렉션 재생성
                self._initialize_collection()
                print("✅ 벡터 DB 초기화 완료")
                return True
        except Exception as e:
            print(f"❌ 벡터 DB 초기화 실패: {e}")
            return False

# 테스트 코드
if __name__ == "__main__":
    # 벡터 분류기 초기화
    classifier = ChromaVectorClassifier()
    
    # 테스트 케이스들
    test_cases = [
        "PK P에 저장된 비밀번호로 CCTV 웹 접속이 안됩니다. 비밀번호는 정확히 입력했는데도 인증 실패가 발생합니다.",
        "VMS와의 통신에 실패했습니다. VMS 패스워드가 맞지 않는 것 같습니다.",
        "Ping 테스트에 실패했습니다. 네트워크 연결이 안되는 것 같습니다.",
        "Onvif 프로토콜로 카메라와 통신이 안됩니다.",
        "PK P 계정이 30일 미접속으로 잠겼습니다."
    ]
    
    print("\n=== 벡터 기반 문제 유형 분류 테스트 ===")
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"입력: {test_input}")
        
        result = classifier.classify_issue(test_input)
        print(f"분류 결과: {result['issue_type']}")
        print(f"신뢰도: {result['confidence']}")
        print(f"유사도 점수: {result.get('similarity_score', 'N/A'):.3f}")
        
        if 'top_matches' in result:
            print("상위 매칭 결과:")
            for match in result['top_matches'][:2]:
                print(f"  - {match['issue_type']}: {match['similarity']:.3f}")
    
    # 통계 출력
    print("\n=== 벡터 DB 통계 ===")
    stats = classifier.get_statistics()
    print(f"총 문서 수: {stats['total_documents']}")
    print(f"문제 유형: {stats['issue_types']}")
    if 'issue_type_counts' in stats:
        print("문제 유형별 문서 수:")
        for issue_type, count in stats['issue_type_counts'].items():
            print(f"  - {issue_type}: {count}개")
