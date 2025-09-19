#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== ChromaDB 디버깅 테스트 ===")

# 1. 기본 Python 확인
print("✅ Python 작동 확인")

# 2. ChromaDB 임포트 테스트
try:
    import chromadb
    print("✅ ChromaDB 임포트 성공")
    print(f"   ChromaDB 버전: {chromadb.__version__}")
except Exception as e:
    print(f"❌ ChromaDB 임포트 실패: {e}")

# 3. 임베딩 함수 테스트
try:
    from chromadb.utils import embedding_functions
    print("✅ ChromaDB 임베딩 함수 임포트 성공")
    
    # 기본 임베딩 함수 테스트
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    print("✅ 기본 임베딩 함수 생성 성공")
    
    # 임베딩 테스트
    test_embedding = embedding_func.encode(["테스트 문장"])
    print(f"✅ 임베딩 테스트 성공: {len(test_embedding[0])}차원")
    
except Exception as e:
    print(f"❌ 임베딩 함수 테스트 실패: {e}")

# 4. sentence-transformers 테스트
try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers 임포트 성공")
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("✅ sentence-transformers 모델 로드 성공")
    
    test_embedding = model.encode(["테스트 문장"])
    print(f"✅ sentence-transformers 임베딩 테스트 성공: {len(test_embedding[0])}차원")
    
except Exception as e:
    print(f"❌ sentence-transformers 테스트 실패: {e}")

# 5. ChromaDB 클라이언트 테스트
try:
    client = chromadb.Client()
    print("✅ ChromaDB 클라이언트 생성 성공")
    
    # 컬렉션 생성 테스트
    collection = client.create_collection("test_collection")
    print("✅ ChromaDB 컬렉션 생성 성공")
    
    # 데이터 추가 테스트
    collection.add(
        documents=["테스트 문서"],
        metadatas=[{"type": "test"}],
        ids=["test_1"]
    )
    print("✅ ChromaDB 데이터 추가 성공")
    
    # 쿼리 테스트
    results = collection.query(
        query_texts=["테스트"],
        n_results=1
    )
    print(f"✅ ChromaDB 쿼리 성공: {len(results['documents'][0])}개 결과")
    
except Exception as e:
    print(f"❌ ChromaDB 클라이언트 테스트 실패: {e}")

print("\n=== 디버깅 완료 ===")
