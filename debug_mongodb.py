#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB 연결 디버깅 스크립트

이 스크립트는 MongoDB 연결 상태와 데이터 저장/조회를 테스트합니다.
Streamlit Cloud에서 실행하여 문제를 진단할 수 있습니다.
"""

import streamlit as st
import os
from datetime import datetime

def debug_mongodb_connection():
    """MongoDB 연결 상태 디버깅"""
    
    st.header("🔍 MongoDB 연결 디버깅")
    
    # 1. 환경변수 확인
    st.subheader("1. 환경변수 확인")
    
    # Streamlit Secrets 확인
    try:
        mongodb_uri = st.secrets.get("MONGODB_URI")
        if mongodb_uri:
            st.success(f"✅ MONGODB_URI 설정됨")
            # 보안을 위해 URI의 일부만 표시
            if 'mongodb+srv://' in mongodb_uri:
                parts = mongodb_uri.split('@')
                if len(parts) > 1:
                    cluster_info = parts[1].split('/')[0]
                    st.info(f"클러스터: {cluster_info}")
                    
                    # 데이터베이스 이름 추출
                    if '/sample_mflix' in mongodb_uri:
                        st.info("데이터베이스: sample_mflix")
                    elif '/privkeeper_db' in mongodb_uri:
                        st.info("데이터베이스: privkeeper_db")
                    else:
                        st.warning("⚠️ 데이터베이스 이름을 찾을 수 없습니다")
        else:
            st.error("❌ MONGODB_URI가 설정되지 않았습니다")
            return
    except Exception as e:
        st.error(f"❌ Secrets 접근 오류: {e}")
        return
    
    # 2. MongoDB 핸들러 테스트
    st.subheader("2. MongoDB 핸들러 테스트")
    
    try:
        from mongodb_handler import MongoDBHandler
        st.success("✅ MongoDB 핸들러 import 성공")
        
        # MongoDB 연결 시도
        mongo_handler = MongoDBHandler()
        st.success("✅ MongoDB Atlas 연결 성공")
        
        # 3. 데이터 저장 테스트
        st.subheader("3. 데이터 저장 테스트")
        
        if st.button("테스트 데이터 저장"):
            test_analysis_data = {
                "issue_type": "디버깅_테스트",
                "classification": {
                    "method": "테스트_분류",
                    "confidence": 0.95
                },
                "gemini_result": {
                    "parsed_response": {
                        "response_type": "해결안",
                        "summary": "MongoDB 디버깅을 위한 테스트 데이터입니다.",
                        "action_flow": "1. 연결 확인\n2. 데이터 저장\n3. 데이터 조회",
                        "email_draft": "안녕하세요,\n\nMongoDB 디버깅 테스트가 완료되었습니다.\n\n감사합니다."
                    }
                }
            }
            
            test_inquiry_data = {
                "timestamp": datetime.now().isoformat(),
                "customer_name": "디버깅_고객사",
                "customer_contact": "010-1234-5678",
                "customer_manager": "디버깅_매니저",
                "inquiry_content": "MongoDB 디버깅 테스트 문의",
                "user_name": "디버깅_사용자",
                "user_role": "관리자",
                "system_version": "1.0.0",
                "browser_info": "Chrome 120.0",
                "os_info": "Windows 10",
                "error_code": "DEBUG001",
                "priority": "낮음",
                "contract_type": "테스트"
            }
            
            # 데이터 저장
            save_result = mongo_handler.save_analysis(test_analysis_data, test_inquiry_data)
            
            if save_result["success"]:
                st.success(f"✅ 테스트 데이터 저장 성공 (ID: {save_result['id']})")
                st.session_state['last_saved_id'] = save_result['id']
            else:
                st.error(f"❌ 테스트 데이터 저장 실패: {save_result.get('error', '알 수 없는 오류')}")
        
        # 4. 데이터 조회 테스트
        st.subheader("4. 데이터 조회 테스트")
        
        if st.button("저장된 데이터 조회"):
            try:
                # 최근 10개 이력 조회
                history = mongo_handler.get_history(limit=10)
                
                if history:
                    st.success(f"✅ {len(history)}개 이력 조회 성공")
                    
                    # 데이터 표시
                    for i, record in enumerate(history):
                        with st.expander(f"이력 {i+1}: {record.get('customer_name', 'N/A')} - {record.get('issue_type', 'N/A')}"):
                            st.json(record)
                else:
                    st.warning("⚠️ 조회된 이력이 없습니다")
                    
            except Exception as e:
                st.error(f"❌ 데이터 조회 실패: {e}")
        
        # 5. 통계 정보 조회
        st.subheader("5. 통계 정보 조회")
        
        if st.button("통계 정보 조회"):
            try:
                stats = mongo_handler.get_statistics()
                
                if stats:
                    st.success("✅ 통계 조회 성공")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("전체 이력 수", stats.get('total_count', 0))
                        st.metric("최근 7일 이력 수", stats.get('recent_count', 0))
                    
                    with col2:
                        if stats.get('user_stats'):
                            st.write("**사용자별 통계:**")
                            for user_stat in stats['user_stats'][:5]:  # 상위 5개만
                                st.write(f"- {user_stat['_id']}: {user_stat['count']}개")
                        
                        if stats.get('issue_stats'):
                            st.write("**문제 유형별 통계:**")
                            for issue_stat in stats['issue_stats'][:5]:  # 상위 5개만
                                st.write(f"- {issue_stat['_id']}: {issue_stat['count']}개")
                else:
                    st.warning("⚠️ 통계 정보를 가져올 수 없습니다")
                    
            except Exception as e:
                st.error(f"❌ 통계 조회 실패: {e}")
        
        # 6. 연결 종료
        st.subheader("6. 연결 종료")
        
        if st.button("MongoDB 연결 종료"):
            try:
                mongo_handler.close_connection()
                st.success("✅ MongoDB 연결 종료 완료")
            except Exception as e:
                st.error(f"❌ 연결 종료 실패: {e}")
        
    except ImportError as e:
        st.error(f"❌ MongoDB 핸들러 import 실패: {e}")
        st.info("mongodb_handler.py 파일이 현재 디렉토리에 있는지 확인하세요.")
        
    except Exception as e:
        st.error(f"❌ MongoDB 테스트 실패: {e}")
        st.info("MongoDB Atlas 설정을 다시 확인하세요.")

def main():
    """메인 함수"""
    st.title("🔧 MongoDB 디버깅 도구")
    
    st.info("이 도구는 MongoDB 연결 상태와 데이터 저장/조회를 테스트합니다.")
    
    # 디버깅 실행
    debug_mongodb_connection()
    
    st.markdown("---")
    st.markdown("### 📋 문제 해결 체크리스트")
    
    checklist = [
        "✅ MONGODB_URI 환경변수 설정",
        "✅ MongoDB Atlas 클러스터 연결",
        "✅ 데이터베이스 사용자 권한 확인",
        "✅ 네트워크 액세스 설정",
        "✅ 데이터 저장 테스트",
        "✅ 데이터 조회 테스트"
    ]
    
    for item in checklist:
        st.write(item)

if __name__ == "__main__":
    main()
