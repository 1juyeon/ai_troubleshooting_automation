# 🚀 MongoDB Atlas 설정 가이드

## 📋 개요

이 문서는 PrivKeeper P 장애 대응 자동화 시스템을 Streamlit Cloud에 배포할 때 MongoDB Atlas를 사용하여 데이터를 영구적으로 저장하는 방법을 설명합니다.

## ☁️ MongoDB Atlas란?

MongoDB Atlas는 MongoDB의 클라우드 기반 데이터베이스 서비스로, 다음과 같은 장점이 있습니다:

- **무료 티어**: 월 512MB까지 무료 사용 가능
- **자동 백업**: 데이터 자동 백업 및 복구
- **확장성**: 필요에 따라 용량 확장 가능
- **보안**: 네트워크 보안, 암호화 등 강력한 보안 기능
- **모니터링**: 실시간 성능 모니터링 및 알림

## 🔧 1단계: MongoDB Atlas 계정 생성

### **A. 계정 생성**
1. [MongoDB Atlas](https://www.mongodb.com/atlas) 접속
2. "Try Free" 버튼 클릭
3. 계정 정보 입력:
   - Email: 사용할 이메일 주소
   - Password: 강력한 비밀번호 (8자 이상, 특수문자 포함)
   - Account Name: 계정명 (예: `privkeeper-company`)

### **B. 조직 및 프로젝트 설정**
1. **Organization Name**: 회사명 또는 팀명 입력
2. **Project Name**: `PrivKeeper-P-System` 입력
3. "Next" 클릭

## 🏗️ 2단계: 데이터베이스 클러스터 생성

### **A. 클러스터 설정**
1. "Build a Database" 클릭
2. **Deployment Option**: "FREE" 선택 (M0 Sandbox)
3. **Cloud Provider & Region**: 
   - AWS 선택 (권장)
   - Region: `Asia Pacific (Tokyo) ap-northeast-1` 선택
4. **Cluster Name**: `privkeeper-cluster` (기본값 유지)
5. "Create" 클릭

### **B. 클러스터 생성 완료**
- 클러스터 생성에는 약 2-3분 소요
- "Cluster is being created" 메시지가 사라질 때까지 대기

## 👤 3단계: 데이터베이스 사용자 생성

### **A. 사용자 생성**
1. 왼쪽 메뉴에서 "Database Access" 클릭
2. "Add New Database User" 클릭
3. **Authentication Method**: "Password" 선택
4. **Username**: `privkeeper_user`
5. **Password**: 강력한 비밀번호 생성 (예: `PrivKeeper2024!`)
6. **Database User Privileges**: "Built-in Role" 선택
7. **Built-in Role**: "Read and write to any database" 선택
8. "Add User" 클릭

### **B. 사용자 생성 확인**
- 사용자 목록에 `privkeeper_user`가 표시되는지 확인

## 🌐 4단계: 네트워크 액세스 설정

### **A. IP 주소 허용**
1. 왼쪽 메뉴에서 "Network Access" 클릭
2. "Add IP Address" 클릭
3. **IP Address**: "Allow Access from Anywhere" 선택 (0.0.0.0/0)
4. **Comment**: `Streamlit Cloud Access`
5. "Confirm" 클릭

### **B. 보안 주의사항**
- 프로덕션 환경에서는 특정 IP 주소만 허용하는 것을 권장
- 개발/테스트 단계에서는 0.0.0.0/0 사용 가능

## 🔗 5단계: 연결 문자열 획득

### **A. 연결 정보 확인**
1. 왼쪽 메뉴에서 "Database" 클릭
2. "Connect" 버튼 클릭
3. **Choose a connection method**: "Connect your application" 선택
4. **Driver**: "Python" 선택
5. **Version**: "4.6 or later" 선택

### **B. 연결 문자열 복사**
```
mongodb+srv://privkeeper_user:<password>@privkeeper-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

⚠️ **중요**: `<password>` 부분을 실제 비밀번호로 교체해야 합니다.

## ⚙️ 6단계: Streamlit Cloud Secrets 설정

### **A. Streamlit Cloud 대시보드 접속**
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. PrivKeeper 앱 선택

### **B. Secrets 설정**
1. "Settings" 탭 클릭
2. "Secrets" 섹션에서 편집 모드 활성화
3. 다음 내용 추가:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_gemini_api_key_here"
MONGODB_URI = "mongodb+srv://privkeeper_user:PrivKeeper2024!@privkeeper-cluster.xxxxx.mongodb.net/privkeeper_db?retryWrites=true&w=majority"
```

⚠️ **주의사항**:
- `MONGODB_URI`의 비밀번호를 실제 설정한 비밀번호로 교체
- `privkeeper_db`는 데이터베이스 이름 (자동 생성됨)

### **C. 저장 및 재배포**
1. "Save" 버튼 클릭
2. "Deploy" 버튼 클릭하여 앱 재배포

## 🧪 7단계: 연결 테스트

### **A. 앱 접속 확인**
1. Streamlit 앱 접속
2. 사이드바에 "✅ MongoDB Atlas 연결 성공" 메시지 확인

### **B. 데이터 저장 테스트**
1. 새로운 고객 문의 입력
2. AI 분석 실행
3. 이력 조회에서 데이터 확인

### **C. MongoDB Atlas에서 데이터 확인**
1. MongoDB Atlas 대시보드에서 "Browse Collections" 클릭
2. `privkeeper_db` → `analysis_history` 컬렉션 확인
3. 저장된 데이터 확인

## 📊 8단계: 데이터베이스 모니터링

### **A. 성능 모니터링**
1. MongoDB Atlas 대시보드에서 "Metrics" 탭 확인
2. 연결 수, 쿼리 성능, 저장소 사용량 모니터링

### **B. 백업 확인**
1. "Backup" 탭에서 자동 백업 상태 확인
2. 필요시 수동 백업 생성

### **C. 알림 설정**
1. "Alerts" 탭에서 성능 임계값 설정
2. 이메일 알림 설정

## 🔒 9단계: 보안 강화 (선택사항)

### **A. VPC 피어링**
- AWS VPC와 MongoDB Atlas 연결
- 네트워크 보안 강화

### **B. 암호화**
- 데이터 암호화 설정 확인
- 전송 중 암호화 (TLS) 활성화

### **C. 감사 로그**
- 데이터베이스 액세스 로그 활성화
- 보안 이벤트 모니터링

## 🚨 문제 해결

### **A. 연결 실패 시**
1. **비밀번호 확인**: MongoDB URI의 비밀번호가 정확한지 확인
2. **네트워크 설정**: IP 주소가 올바르게 허용되었는지 확인
3. **사용자 권한**: 데이터베이스 사용자 권한이 올바른지 확인

### **B. 성능 문제 시**
1. **인덱스 확인**: 자동 생성된 인덱스 상태 확인
2. **쿼리 최적화**: 복잡한 쿼리 최적화
3. **클러스터 크기**: 필요시 클러스터 크기 증가

### **C. 데이터 손실 방지**
1. **정기 백업**: 자동 백업 설정 확인
2. **복구 테스트**: 백업에서 데이터 복구 테스트
3. **모니터링**: 데이터베이스 상태 지속적 모니터링

## 💰 비용 관리

### **A. 무료 티어 제한**
- **저장소**: 512MB
- **데이터 전송**: 500MB/일
- **연결**: 최대 500개

### **B. 유료 플랜 업그레이드**
- **M2**: $9/월 (2GB 저장소)
- **M5**: $25/월 (5GB 저장소)
- **M10**: $57/월 (10GB 저장소)

### **C. 비용 최적화 팁**
1. 불필요한 데이터 정리
2. 인덱스 최적화
3. 쿼리 효율성 개선

## 📚 추가 리소스

### **A. 공식 문서**
- [MongoDB Atlas 문서](https://docs.atlas.mongodb.com/)
- [Python 드라이버 문서](https://pymongo.readthedocs.io/)

### **B. 커뮤니티**
- [MongoDB 포럼](https://developer.mongodb.com/community/forums/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/mongodb)

### **C. 학습 자료**
- [MongoDB University](https://university.mongodb.com/)
- [YouTube 채널](https://www.youtube.com/user/MongoDB)

## ✅ 체크리스트

- [ ] MongoDB Atlas 계정 생성
- [ ] 클러스터 생성 (M0 Free)
- [ ] 데이터베이스 사용자 생성
- [ ] 네트워크 액세스 설정
- [ ] 연결 문자열 획득
- [ ] Streamlit Secrets 설정
- [ ] 연결 테스트
- [ ] 데이터 저장 테스트
- [ ] 모니터링 설정
- [ ] 백업 확인

## 🎯 다음 단계

MongoDB Atlas 설정이 완료되면:

1. **데이터 모니터링** 설정
2. **백업 정책** 수립
3. **성능 최적화** 진행
4. **보안 강화** 적용

---

**⚠️ 중요**: 이 가이드를 따라 설정한 후에도 문제가 발생하면 MongoDB Atlas 지원팀에 문의하거나, Streamlit Cloud 로그를 확인하여 오류 메시지를 파악하세요.
