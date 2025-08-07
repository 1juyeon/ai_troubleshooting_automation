import pandas as pd
import os
from typing import List, Dict, Any, Optional
import json
import numpy as np
from vector_db import VectorSearch
from typing import List, Dict, Any

class VectorSearchWrapper:
    def __init__(self):
        """벡터 검색 래퍼 초기화"""
        try:
            self.vector_search = VectorSearch()
            print("✅ 벡터 검색 초기화 성공")
        except Exception as e:
            print(f"❌ 벡터 검색 초기화 실패: {e}")
            self.vector_search = None
    
    def add_case(self, customer_input: str, issue_type: str, summary: str = "", 
                 action_flow: str = "", customer_name: str = "", timestamp: str = ""):
        """사례 추가"""
        if self.vector_search:
            return self.vector_search.add_case(
                customer_input, issue_type, summary, action_flow, customer_name, timestamp
            )
        return False
    
    def search_similar_cases(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """유사 사례 검색"""
        if self.vector_search:
            return self.vector_search.search_similar_cases(query, top_k)
        return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 조회"""
        if self.vector_search:
            return self.vector_search.get_statistics()
        return {
            'total_documents': 0,
            'vector_dimensions': 0,
            'issue_types': [],
            'data_dir': 'vector_data'
        }
    
    def add_initial_sample_data(self):
        """초기 샘플 데이터 추가"""
        if self.vector_search:
            return self.vector_search.add_initial_sample_data()
        return False 