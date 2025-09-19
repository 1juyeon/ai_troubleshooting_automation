print("Python 작동 확인")

try:
    from chroma_vector_classifier import ChromaVectorClassifier
    print("✅ ChromaVectorClassifier 임포트 성공")
    
    classifier = ChromaVectorClassifier()
    print("✅ 분류기 초기화 성공")
    
    result = classifier.classify_issue("비밀번호가 맞지 않습니다")
    print(f"분류 결과: {result}")
    
except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()
