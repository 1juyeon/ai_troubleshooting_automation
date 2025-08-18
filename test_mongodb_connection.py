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
    
    print("🚀 MongoDB Atlas 연결 테스트 시작")
    print("=" * 50)
    
    try:
        # MongoDB 핸들러 import 시도
        from mongodb_handler import MongoDBHandler
        print("✅ MongoDB 핸들러 import 성공")
        
        # MongoDB 연결 시도
        mongo_handler = MongoDBHandler()
        print("✅ MongoDB Atlas 연결 성공")
        
        # 테스트 데이터 생성
        test_analysis_data = {
            "issue_type": "테스트_문제",
            "classification": {
                "method": "테스트_분류",
                "confidence": 0.95
            },
            "gemini_result": {
                "parsed_response": {
                    "response_type": "해결안",
                    "summary": "MongoDB 연결 테스트를 위한 샘플 데이터입니다.",
                    "action_flow": "1. 연결 확인\n2. 데이터 저장\n3. 데이터 조회\n4. 연결 종료",
                    "email_draft": "안녕하세요,\n\nMongoDB 연결 테스트가 성공적으로 완료되었습니다.\n\n감사합니다."
                }
            }
        }
        
        test_inquiry_data = {
            "timestamp": datetime.now().isoformat(),
            "customer_name": "테스트_고객사",
            "customer_contact": "010-1234-5678",
            "customer_manager": "테스트_매니저",
            "inquiry_content": "MongoDB 연결 테스트 문의",
            "user_name": "테스트_사용자",
            "user_role": "관리자",
            "system_version": "1.0.0",
            "browser_info": "Chrome 120.0",
            "os_info": "Windows 10",
            "error_code": "TEST001",
            "priority": "낮음",
            "contract_type": "테스트"
        }
        
        print("\n📝 테스트 데이터 저장 시도...")
        
        # 데이터 저장 테스트
        save_result = mongo_handler.save_analysis(test_analysis_data, test_inquiry_data)
        
        if save_result["success"]:
            print(f"✅ 테스트 데이터 저장 성공 (ID: {save_result['id']})")
            
            # 저장된 데이터 조회 테스트
            print("\n🔍 저장된 데이터 조회 시도...")
            history = mongo_handler.get_history(limit=5)
            
            if history:
                print(f"✅ {len(history)}개 이력 조회 성공")
                latest_record = history[0]
                print(f"   - 최신 이력: {latest_record['customer_name']} - {latest_record['issue_type']}")
            else:
                print("⚠️ 이력 조회 실패")
            
            # 통계 정보 조회 테스트
            print("\n📊 통계 정보 조회 시도...")
            stats = mongo_handler.get_statistics()
            
            if stats:
                print(f"✅ 통계 조회 성공")
                print(f"   - 전체 이력 수: {stats.get('total_count', 0)}")
                print(f"   - 최근 7일 이력 수: {stats.get('recent_count', 0)}")
            else:
                print("⚠️ 통계 조회 실패")
            
            # 테스트 데이터 삭제 (선택사항)
            print("\n🗑️ 테스트 데이터 정리...")
            if 'id' in save_result:
                delete_result = mongo_handler.delete_history(save_result['id'])
                if delete_result["success"]:
                    print("✅ 테스트 데이터 삭제 완료")
                else:
                    print(f"⚠️ 테스트 데이터 삭제 실패: {delete_result.get('error', '알 수 없는 오류')}")
            
        else:
            print(f"❌ 테스트 데이터 저장 실패: {save_result.get('error', '알 수 없는 오류')}")
        
        # 연결 종료
        mongo_handler.close_connection()
        print("\n✅ MongoDB 연결 테스트 완료")
        
    except ImportError as e:
        print(f"❌ MongoDB 핸들러 import 실패: {e}")
        print("   mongodb_handler.py 파일이 현재 디렉토리에 있는지 확인하세요.")
        
    except KeyError as e:
        print(f"❌ 환경변수 설정 오류: {e}")
        print("   MONGODB_URI 환경변수가 설정되어 있는지 확인하세요.")
        print("   또는 .env 파일에 MONGODB_URI를 추가하세요.")
        
    except Exception as e:
        print(f"❌ MongoDB 연결 테스트 실패: {e}")
        print("   MongoDB Atlas 설정을 다시 확인하세요.")

def check_environment():
    """환경 설정 확인"""
    
    print("🔍 환경 설정 확인")
    print("=" * 30)
    
    # Python 버전 확인
    print(f"Python 버전: {sys.version}")
    
    # 필요한 패키지 확인
    required_packages = ['pymongo', 'streamlit']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 패키지 설치됨")
        except ImportError:
            print(f"❌ {package} 패키지가 설치되지 않음")
    
    # 환경변수 확인
    mongodb_uri = os.getenv('MONGODB_URI')
    if mongodb_uri:
        print("✅ MONGODB_URI 환경변수 설정됨")
        # 보안을 위해 URI의 일부만 표시
        if 'mongodb+srv://' in mongodb_uri:
            parts = mongodb_uri.split('@')
            if len(parts) > 1:
                print(f"   연결 대상: {parts[1].split('/')[0]}")
    else:
        print("❌ MONGODB_URI 환경변수가 설정되지 않음")
        print("   .env 파일에 MONGODB_URI를 추가하거나 환경변수로 설정하세요.")
    
    print()

def main():
    """메인 함수"""
    
    print("🔧 PrivKeeper P - MongoDB Atlas 연결 테스트")
    print("=" * 60)
    
    # 환경 설정 확인
    check_environment()
    
    # MongoDB 연결 테스트
    test_mongodb_connection()
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    
    print("\n📋 다음 단계:")
    print("1. MongoDB Atlas 대시보드에서 데이터 확인")
    print("2. Streamlit Cloud에 배포하여 실제 환경에서 테스트")
    print("3. 문제 발생 시 로그 확인 및 설정 재검토")

if __name__ == "__main__":
    main()
