#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB Atlas 연결 테스트 스크립트

이 스크립트는 MongoDB Atlas 연결을 테스트하고 기본적인 CRUD 작업을 수행합니다.
로컬 환경에서 실행하여 연결 상태를 확인할 수 있습니다.
"""

import os
import sys
from datetime import datetime
import json

def test_mongodb_connection():
    """MongoDB 연결 테스트"""
    print("🔧 PrivKeeper P - MongoDB Atlas 연결 테스트")
    print("=" * 60)
    
    # 환경 설정 확인
    print("🔍 환경 설정 확인")
    print("=" * 30)
    
    # Python 버전 확인
    python_version = sys.version
    print(f"Python 버전: {python_version}")
    
    # 필수 패키지 확인
    try:
        import pymongo
        print("✅ pymongo 패키지 설치됨")
    except ImportError:
        print("❌ pymongo 패키지가 설치되지 않음")
        print("   pip install pymongo 명령으로 설치하세요.")
        return False
    
    try:
        import streamlit
        print("✅ streamlit 패키지 설치됨")
    except ImportError:
        print("❌ streamlit 패키지가 설치되지 않음")
    
    # MongoDB URI 확인
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ MONGODB_URI 환경변수가 설정되지 않음")
        print("   .env 파일에 MONGODB_URI를 추가하거나 환경변수로 설정하세요.")
        
        # 테스트용 연결 문자열 제공
        print("\n💡 테스트를 위한 MongoDB 연결 문자열 예시:")
        print("mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority")
        print("\n⚠️  실제 사용 시에는 보안을 위해 환경변수나 .env 파일을 사용하세요.")
        
        # 테스트용 더미 URI 설정 (실제 연결은 안됨)
        mongodb_uri = "mongodb+srv://test:test@test.mongodb.net/test?retryWrites=true&w=majority"
        print(f"\n🔧 테스트용 더미 URI 설정: {mongodb_uri[:50]}...")
        print("💡 실제 MongoDB Atlas URI는 Streamlit Cloud Secrets에서 설정하세요.")
    else:
        print("✅ MONGODB_URI 환경변수 설정됨")
    
    print("\n🚀 MongoDB Atlas 연결 테스트 시작")
    print("=" * 50)
    
    # MongoDB 핸들러 import 테스트
    try:
        from mongodb_handler import MongoDBHandler
        print("✅ MongoDB 핸들러 import 성공")
    except ImportError as e:
        print(f"❌ MongoDB 핸들러 import 실패: {e}")
        print("   mongodb_handler.py 파일이 현재 디렉토리에 있는지 확인하세요.")
        return False
    
    # MongoDB 핸들러 초기화 테스트
    try:
        mongo_handler = MongoDBHandler()
        print("✅ MongoDB 핸들러 초기화 성공")
    except Exception as e:
        print(f"❌ MongoDB 핸들러 초기화 오류: {e}")
        print("💡 연결 문자열 형식과 인증 정보를 확인해주세요.")
        return False
    
    # MongoDB 연결 테스트
    try:
        connection_result = mongo_handler.test_connection()
        if connection_result.get('success'):
            print("✅ MongoDB 연결 성공")
            print(f"   데이터베이스: {connection_result.get('current_db', 'Unknown')}")
            print(f"   컬렉션: {', '.join(connection_result.get('collections', []))}")
        else:
            print(f"❌ MongoDB 연결 실패: {connection_result.get('message', '알 수 없는 오류')}")
            return False
    except Exception as e:
        print(f"❌ MongoDB 연결 테스트 실패: {e}")
        print("   MongoDB Atlas 설정을 다시 확인하세요.")
        return False
    
    # 테스트 데이터 저장 테스트
    try:
        print("\n🧪 테스트 데이터 저장 테스트")
        test_analysis_data = {
            'issue_type': 'VMS와의 통신에 실패했습니다',
            'classification': {
                'method': 'keyword_based',
                'confidence': 'high'
            },
            'ai_result': {
                'parsed_response': {
                    'response_type': '해결안',
                    'summary': 'VMS와 PK P 간 통신 실패 문제입니다.',
                    'action_flow': '1. PKP 웹 설정 > NVR/VMS 항목 확인\n2. VMS 패스워드 일치 여부 확인\n3. 네트워크 연결 상태 확인',
                    'email_draft': '테스트 이메일 초안입니다.'
                }
            }
        }
        
        test_inquiry_data = {
            'timestamp': datetime.now().isoformat(),
            'customer_name': '테스트 고객사',
            'customer_contact': '010-1234-5678',
            'customer_manager': '테스트 담당자',
            'inquiry_content': 'VMS와의 통신이 실패합니다.',
            'user_name': '테스트 사용자',
            'user_role': '영업',
            'priority': '보통',
            'contract_type': '무상 유지보수'
        }
        
        save_result = mongo_handler.save_analysis(test_analysis_data, test_inquiry_data)
        if save_result.get('success'):
            print("✅ 테스트 데이터 저장 성공")
            print(f"   저장된 ID: {save_result.get('id', 'Unknown')}")
        else:
            print(f"❌ 테스트 데이터 저장 실패: {save_result.get('error', '알 수 없는 오류')}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 데이터 저장 테스트 실패: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    
    print("\n📋 다음 단계:")
    print("1. MongoDB Atlas 대시보드에서 데이터 확인")
    print("2. Streamlit Cloud에 배포하여 실제 환경에서 테스트")
    print("3. 문제 발생 시 로그 확인 및 설정 재검토")
    
    return True

if __name__ == "__main__":
    test_mongodb_connection()
