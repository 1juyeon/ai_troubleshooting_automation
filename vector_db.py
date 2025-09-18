import numpy as np
import json
import pickle
from typing import List, Dict, Any, Optional
import os
import re

class VectorDB:
    def __init__(self, data_dir: str = "vector_data"):
        """벡터 DB 초기화 (간단한 텍스트 유사도 기반)"""
        self.data_dir = data_dir
        self.documents = []
        self.metadata = []
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        
        # 기존 데이터 로드
        self._load_existing_data()
        
        print("✅ 벡터 DB 초기화 완료")
    
    def _load_existing_data(self):
        """기존 데이터 로드"""
        try:
            # 문서 데이터 로드
            docs_path = os.path.join(self.data_dir, "documents.json")
            if os.path.exists(docs_path):
                with open(docs_path, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
            
            # 메타데이터 로드
            metadata_path = os.path.join(self.data_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    
            print(f"✅ 기존 데이터 로드 완료: {len(self.documents)}개 문서")
            
        except Exception as e:
            print(f"⚠️ 기존 데이터 로드 실패: {e}")
            self.documents = []
            self.metadata = []
    
    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """간단한 텍스트 유사도 계산 (단어 겹침 기반)"""
        try:
            # 텍스트를 단어로 분리하고 정규화
            words1 = set(re.findall(r'\w+', text1.lower()))
            words2 = set(re.findall(r'\w+', text2.lower()))
            
            if not words1 or not words2:
                return 0.0
            
            # Jaccard 유사도 계산
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            print(f"⚠️ 유사도 계산 실패: {e}")
            return 0.0
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """문서 추가"""
        try:
            # 문서 및 메타데이터 업데이트
            self.documents.extend(documents)
            self.metadata.extend([
                {
                    'id': len(self.metadata) + i,
                    'timestamp': doc.get('timestamp', ''),
                    'issue_type': doc.get('issue_type', ''),
                    'customer_name': doc.get('customer_name', '')
                }
                for i, doc in enumerate(documents)
            ])
            
            # 데이터 저장
            self._save_data()
            
            print(f"✅ {len(documents)}개 문서 추가 완료")
            return True
            
        except Exception as e:
            print(f"❌ 문서 추가 실패: {e}")
            return False
    
    def _save_data(self):
        """데이터 저장"""
        try:
            # 문서 저장
            with open(os.path.join(self.data_dir, "documents.json"), 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            
            # 메타데이터 저장
            with open(os.path.join(self.data_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
            print("✅ 벡터 DB 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """유사 문서 검색"""
        try:
            if len(self.documents) == 0:
                print("⚠️ 벡터 DB가 비어있습니다.")
                return []
            
            # 각 문서와의 유사도 계산
            similarities = []
            for doc in self.documents:
                # 문서 텍스트 구성
                text_parts = []
                if 'customer_input' in doc:
                    text_parts.append(doc['customer_input'])
                if 'issue_type' in doc:
                    text_parts.append(doc['issue_type'])
                if 'summary' in doc:
                    text_parts.append(doc['summary'])
                if 'action_flow' in doc:
                    text_parts.append(doc['action_flow'])
                
                doc_text = " ".join(text_parts)
                similarity = self._simple_text_similarity(query, doc_text)
                similarities.append(similarity)
            
            # 상위 k개 결과 추출
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity = similarities[idx]
                if similarity >= threshold:
                    results.append({
                        'document': self.documents[idx],
                        'metadata': self.metadata[idx],
                        'similarity_score': float(similarity)
                    })
            
            print(f"✅ 검색 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """벡터 DB 통계"""
        try:
            return {
                'total_documents': len(self.documents),
                'vector_dimensions': 0,  # 간단한 텍스트 유사도는 차원이 없음
                'issue_types': list(set([doc.get('issue_type', '') for doc in self.documents])),
                'data_dir': self.data_dir
            }
        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")
            return {
                'total_documents': 0,
                'vector_dimensions': 0,
                'issue_types': [],
                'data_dir': self.data_dir
            }
    
    def clear(self):
        """벡터 DB 초기화"""
        try:
            self.documents = []
            self.metadata = []
            
            # 파일 삭제
            for filename in ["documents.json", "metadata.json"]:
                filepath = os.path.join(self.data_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            print("✅ 벡터 DB 초기화 완료")
            
        except Exception as e:
            print(f"❌ 벡터 DB 초기화 실패: {e}")

# 벡터 검색 래퍼 클래스 (기존 vector_search.py와 호환)
class VectorSearch:
    def __init__(self):
        """벡터 검색 초기화"""
        self.vector_db = VectorDB()
        print("✅ 벡터 검색 초기화 완료")
    
    def add_case(self, customer_input: str, issue_type: str, summary: str = "", 
                 action_flow: str = "", customer_name: str = "", timestamp: str = ""):
        """사례 추가"""
        document = {
            'customer_input': customer_input,
            'issue_type': issue_type,
            'summary': summary,
            'action_flow': action_flow,
            'customer_name': customer_name,
            'timestamp': timestamp
        }
        
        return self.vector_db.add_documents([document])
    
    def search_similar_cases(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """유사 사례 검색"""
        results = self.vector_db.search(query, top_k)
        
        # 기존 형식으로 변환
        formatted_results = []
        for result in results:
            doc = result['document']
            formatted_results.append({
                'customer_input': doc.get('customer_input', ''),
                'issue_type': doc.get('issue_type', ''),
                'summary': doc.get('summary', ''),
                'action_flow': doc.get('action_flow', ''),
                'similarity_score': result['similarity_score']
            })
        
        return formatted_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 조회"""
        return self.vector_db.get_statistics() 