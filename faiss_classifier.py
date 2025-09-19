#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import json
import os
from typing import List, Dict, Any, Optional

# FAISS 임포트 (Streamlit Cloud 호환)
try:
    import faiss
    FAISS_AVAILABLE = True
    print("✅ FAISS 사용 가능")
except ImportError as e:
    print(f"❌ FAISS 설치 필요: pip install faiss-cpu")
    FAISS_AVAILABLE = False

# Streamlit Cloud 환경 확인
import os
if os.getenv('STREAMLIT_CLOUD'):
    print("🌐 Streamlit Cloud 환경 감지")
    if not FAISS_AVAILABLE:
        print("⚠️ Streamlit Cloud에서 FAISS 사용 불가, 키워드 기반 분류로 폴백")

# sentence-transformers 임포트
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    print("✅ sentence-transformers 사용 가능")
except ImportError as e:
    print(f"❌ sentence-transformers 설치 필요: pip install sentence-transformers")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class FaissVectorClassifier:
    def __init__(self, persist_directory: str = "faiss_issue_classification"):
        """FAISS 기반 벡터 분류기 초기화"""
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
        
        # 키워드 매핑 (폴백용)
        self.keyword_mapping = {
            "현재 비밀번호가 맞지 않습니다": [
                "비밀번호", "패스워드", "password", "인증", "로그인", "접속", "웹", "cctv",
                "맞지 않", "틀렸", "실패", "오류", "인증 실패", "접속 실패", "로그인 실패"
            ],
            "VMS와의 통신에 실패했습니다": [
                "vms", "VMS", "통신", "연결", "서버", "svms", "nvr", "영상", "카메라",
                "실패", "오류", "연결 안", "통신 실패", "서버 연결"
            ],
            "Ping 테스트에 실패했습니다": [
                "ping", "Ping", "네트워크", "연결", "통신", "테스트", "응답", "네트워크 연결",
                "실패", "안됨", "오류", "ping 실패", "네트워크 실패"
            ],
            "Onvif 응답이 없습니다": [
                "onvif", "Onvif", "ONVIF", "프로토콜", "카메라", "설정", "통신", "응답",
                "없", "실패", "오류", "onvif 응답", "프로토콜 응답"
            ],
            "로그인 차단 상태입니다": [
                "차단", "잠금", "로그인", "계정", "cctv", "접속", "차단 상태", "잠금 상태",
                "안됨", "실패", "오류", "로그인 차단", "계정 차단"
            ],
            "비밀번호 변경에 실패했습니다": [
                "비밀번호 변경", "패스워드 변경", "변경", "수정", "업데이트", "비밀번호 수정",
                "실패", "안됨", "오류", "변경 실패", "수정 실패"
            ],
            "PK P 계정 로그인 안됨": [
                "pk p", "PK P", "계정", "로그인", "30일", "미접속", "잠금", "잠겼",
                "안됨", "실패", "오류", "계정 로그인", "pk p 계정"
            ],
            "PK P 웹 접속 안됨": [
                "pk p", "PK P", "웹", "접속", "웹사이트", "톰캣", "tomcat", "서비스",
                "안됨", "실패", "오류", "웹 접속", "페이지", "로드"
            ]
        }
        
        # FAISS 인덱스와 메타데이터
        self.index = None
        self.documents = []
        self.metadatas = []
        self.embedding_model = None
        
        # 초기화
        self._initialize_embedding_model()
        self._load_or_create_index()
    
    def _initialize_embedding_model(self):
        """임베딩 모델 초기화"""
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # 경량 모델 사용 (Windows에서 더 안정적)
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ sentence-transformers 모델 로드 성공")
            else:
                print("⚠️ sentence-transformers 없음, 키워드 기반 분류만 사용")
                self.embedding_model = None
        except Exception as e:
            print(f"❌ 임베딩 모델 초기화 실패: {e}")
            self.embedding_model = None
    
    def _load_or_create_index(self):
        """FAISS 인덱스 로드 또는 생성"""
        try:
            if not FAISS_AVAILABLE or not self.embedding_model:
                print("⚠️ FAISS 또는 임베딩 모델 없음, 키워드 기반 분류만 사용")
                return
            
            # 저장된 인덱스 로드 시도
            index_path = os.path.join(self.persist_directory, "faiss_index.bin")
            metadata_path = os.path.join(self.persist_directory, "metadata.json")
            
            if os.path.exists(index_path) and os.path.exists(metadata_path):
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data['documents']
                    self.metadatas = data['metadatas']
            else:
                self._create_index()
                
        except Exception as e:
            print(f"❌ FAISS 인덱스 로드/생성 실패: {e}")
            self.index = None
    
    def _create_index(self):
        """새로운 FAISS 인덱스 생성"""
        try:
            # 샘플 데이터 로드
            sample_data = self._load_sample_data()
            
            if not sample_data:
                print("❌ 샘플 데이터 없음")
                return
            
            # 문서와 메타데이터 준비
            documents = []
            metadatas = []
            
            for issue_type, samples in sample_data.items():
                for i, sample in enumerate(samples):
                    documents.append(sample)
                    metadatas.append({
                        "issue_type": issue_type,
                        "sample_index": i,
                        "is_sample": True
                    })
            
            # 임베딩 생성
            embeddings = self.embedding_model.encode(documents)
            embeddings = embeddings.astype('float32')
            
            # FAISS 인덱스 생성 (내적 기반 유사도)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(embeddings)
            
            # 메타데이터 저장
            self.documents = documents
            self.metadatas = metadatas
            
            # 디렉토리 생성
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # 인덱스 저장
            faiss.write_index(self.index, os.path.join(self.persist_directory, "faiss_index.bin"))
            with open(os.path.join(self.persist_directory, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump({
                    'documents': self.documents,
                    'metadatas': self.metadatas
                }, f, ensure_ascii=False, indent=2)
            
            
        except Exception as e:
            print(f"❌ FAISS 인덱스 생성 실패: {e}")
            self.index = None
    
    def _load_sample_data(self):
        """샘플 데이터 로드 (Streamlit Cloud 호환)"""
        try:
            # Streamlit resource를 통한 파일 읽기 시도
            try:
                import streamlit as st
                # Streamlit Cloud에서 파일 읽기
                with open("vector_data/sample_issues.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("sample_issues", {})
            except:
                pass
            
            # 여러 경로 시도 (로컬 환경 호환)
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "vector_data", "sample_issues.json"),
                os.path.join("vector_data", "sample_issues.json"),
                "vector_data/sample_issues.json",
                os.path.join(os.getcwd(), "vector_data", "sample_issues.json")
            ]
            
            for json_path in possible_paths:
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return data.get("sample_issues", {})
            
            print("⚠️ 샘플 데이터 파일을 찾을 수 없음, 기본 데이터 사용")
            # 기본 데이터 (sample_issues.json과 동일)
            return {
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
                    "카메라 Onvif 서비스가 응답하지 않습니다",
                    "Onvif 프로토콜로 카메라 접속이 안됩니다",
                    "Onvif 통신 테스트에 실패했습니다"
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
                    "웹 서비스 연결에 실패했습니다"
                ],
                "기타": [
                    "알 수 없는 오류가 발생했습니다",
                    "시스템 오류로 인해 문제가 발생했습니다",
                    "예상치 못한 오류가 발생했습니다",
                    "기술적 문제로 인해 서비스가 중단되었습니다",
                    "시스템 점검 중입니다",
                    "일시적인 오류가 발생했습니다"
                    ]
                }
        except Exception as e:
            print(f"❌ 샘플 데이터 로드 실패: {e}")
            return {}
    
    def _classify_by_keywords(self, customer_input: str) -> Dict[str, Any]:
        """키워드 기반 분류 (폴백)"""
        try:
            normalized_input = customer_input.lower().strip()
            issue_scores = {}
            
            for issue_type, keywords in self.keyword_mapping.items():
                score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    if keyword.lower() in normalized_input:
                        score += 1
                        matched_keywords.append(keyword)
                
                if score > 0:
                    issue_scores[issue_type] = {
                        'score': score,
                        'matched_keywords': matched_keywords,
                        'confidence': min(score / len(keywords), 1.0)
                    }
            
            if issue_scores:
                best_issue = max(issue_scores.items(), key=lambda x: x[1]['score'])
                best_issue_type = best_issue[0]
                best_score = best_issue[1]['score']
                best_confidence = best_issue[1]['confidence']
                matched_keywords = best_issue[1]['matched_keywords']
                
                confidence_level = 'high' if best_confidence >= 0.5 else 'medium' if best_confidence >= 0.3 else 'low'
                
                return {
                    'issue_type': best_issue_type,
                    'method': 'keyword_based',
                    'confidence': confidence_level,
                    'score': best_score,
                    'matched_keywords': matched_keywords,
                    'all_scores': {k: v['score'] for k, v in issue_scores.items()}
                }
            else:
                return {
                    'issue_type': '기타',
                    'method': 'keyword_based',
                    'confidence': 'low',
                    'score': 0,
                    'matched_keywords': [],
                    'all_scores': {}
                }
                
        except Exception as e:
            return {
                'issue_type': '기타',
                'method': 'keyword_based',
                'confidence': 'low',
                'error': str(e)
            }
    
    def classify_issue(self, customer_input: str, top_k: int = 3) -> Dict[str, Any]:
        """벡터 기반 문제 유형 분류 (FAISS + 키워드 폴백)"""
        try:
            
            # FAISS 벡터 분류 시도
            if self.index is not None and self.embedding_model is not None:
                
                # 쿼리 임베딩 생성
                query_embedding = self.embedding_model.encode([customer_input]).astype('float32')
                
                # FAISS 검색
                scores, indices = self.index.search(query_embedding, top_k)
                
                if len(indices[0]) > 0:
                    # 결과 분석
                    issue_scores = {}
                    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                        if idx < len(self.metadatas):
                            issue_type = self.metadatas[idx]['issue_type']
                            if issue_type not in issue_scores:
                                issue_scores[issue_type] = []
                            issue_scores[issue_type].append(float(score))
                    
                    # 최고 점수 문제 유형 선택
                    best_issue_type = '기타'
                    best_score = 0
                    
                    for issue_type, scores_list in issue_scores.items():
                        max_score = max(scores_list)
                        if max_score > best_score:
                            best_score = max_score
                            best_issue_type = issue_type
                    
                    # 신뢰도 결정
                    if best_score >= 0.7:
                        confidence = 'high'
                    elif best_score >= 0.5:
                        confidence = 'medium'
                    else:
                        confidence = 'low'
                    
                    
                    return {
                        'issue_type': best_issue_type,
                        'method': 'faiss_vector',
                        'confidence': confidence,
                        'similarity_score': best_score,
                        'all_scores': {k: max(v) for k, v in issue_scores.items()}
                    }
            
            # FAISS 실패 시 키워드 기반 분류로 폴백
            return self._classify_by_keywords(customer_input)
            
        except Exception as e:
            print(f"❌ 분류 실패: {e}")
            return self._classify_by_keywords(customer_input)
    
    def get_statistics(self) -> Dict[str, Any]:
        """분류기 통계"""
        try:
            if self.index is not None:
                # 문제 유형별 통계
                issue_type_counts = {}
                for metadata in self.metadatas:
                    issue_type = metadata.get('issue_type', '기타')
                    issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
                
                return {
                    'total_documents': len(self.documents),
                    'issue_types': list(issue_type_counts.keys()),
                    'issue_type_counts': issue_type_counts,
                    'index_size': self.index.ntotal if self.index else 0,
                    'method': 'faiss_vector',
                    'embedding_model': 'all-MiniLM-L6-v2' if self.embedding_model else 'None',
                    'collection_name': 'FAISS Vector DB'
                }
            else:
                # 키워드 기반 분류기 통계
                sample_data = self._load_sample_data()
                total_samples = sum(len(samples) for samples in sample_data.values())
                issue_type_counts = {issue_type: len(samples) for issue_type, samples in sample_data.items()}
                
                return {
                    'total_documents': total_samples,
                    'issue_types': list(issue_type_counts.keys()),
                    'issue_type_counts': issue_type_counts,
                    'index_size': 0,
                    'method': 'keyword_only',
                    'embedding_model': 'None',
                    'collection_name': 'N/A'
                }
        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")
            return {
                'total_documents': 0,
                'issue_types': self.issue_types,
                'issue_type_counts': {},
                'index_size': 0,
                'method': 'keyword_only',
                'embedding_model': 'None',
                'collection_name': 'N/A'
            }

# 테스트 코드
if __name__ == "__main__":
    classifier = FaissVectorClassifier()
    
    test_cases = [
        "비밀번호가 맞지 않습니다",
        "VMS 통신 실패",
        "Ping 테스트 실패",
        "웹 접속 안됨"
    ]
    
    for test_input in test_cases:
        result = classifier.classify_issue(test_input)
        print(f"테스트: {test_input} -> {result['issue_type']} ({result['method']}, {result['confidence']})")
    
    # 통계
    stats = classifier.get_statistics()
    print(f"총 문서 수: {stats['total_documents']}, 방법: {stats['method']}, 인덱스: {stats['index_size']}")
