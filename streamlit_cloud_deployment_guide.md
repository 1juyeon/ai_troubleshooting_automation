# 🚀 Streamlit Cloud 배포 가이드

## 📋 개요

이 문서는 PrivKeeper P 장애 대응 자동화 시스템을 Streamlit Cloud에 배포하기 위한 가이드입니다.

## ☁️ Streamlit Cloud 환경 특징

### **제한사항**
- **읽기 전용 파일 시스템**: `user_data/` 디렉토리에 파일 저장 불가
- **임시 저장소**: 세션 기반 임시 데이터 저장만 가능
- **재시작 시 데이터 손실**: 앱 재시작 시 모든 데이터 초기화
- **메모리 제한**: 대용량 데이터 처리 시 메모리 부족 가능

### **장점**
- **무료 호스팅**: 개인 프로젝트 무료 배포 가능
- **자동 HTTPS**: SSL 인증서 자동 적용
- **Git 연동**: GitHub 저장소와 자동 동기화
- **확장성**: 트래픽 증가 시 자동 스케일링

## 🔧 배포 준비

### 1. **GitHub 저장소 설정**
```bash
# 로컬 저장소를 GitHub에 푸시
git add .
git commit -m "Streamlit Cloud 배포 준비"
git push origin main
```

### 2. **Streamlit Cloud Secrets 설정**
Streamlit Cloud 대시보드에서 다음 환경변수 설정:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_actual_api_key_here"
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority"
```

**중요**: MongoDB URI는 반드시 Streamlit Secrets에 설정해야 합니다.

### 3. **requirements.txt 확인**
```txt
streamlit>=1.32.0
pandas>=2.2.0
google-generativeai>=0.8.0
python-dotenv>=1.0.0
scikit-learn>=1.4.0
numpy>=1.26.0
pymongo>=4.6.0
dnspython>=2.6.0
pytz>=2024.1
requests>=2.31.0
```

## 🚀 배포 단계

### 1. **Streamlit Cloud 접속**
- [share.streamlit.io](https://share.streamlit.io) 접속
- GitHub 계정으로 로그인

### 2. **새 앱 생성**
- "New app" 버튼 클릭
- GitHub 저장소 선택
- 메인 파일 경로: `app.py`
- Python 버전: 3.9 이상

### 3. **Secrets 설정**
- "Secrets" 탭에서 환경변수 설정
- `GEMINI_API_KEY` 값 입력
- `MONGODB_URI` 값 입력 (MongoDB Atlas 연결 문자열)

### 4. **배포 실행**
- "Deploy!" 버튼 클릭
- 배포 완료까지 대기 (약 2-3분)

## 🔍 배포 후 확인사항

### 1. **환경 감지 확인**
사이드바에 "☁️ Streamlit Cloud 환경" 메시지 표시 확인

### 2. **데이터 저장 테스트**
- 새로운 고객 문의 입력
- AI 분석 실행
- 이력 조회에서 데이터 확인

### 3. **오류 로그 확인**
Streamlit Cloud 대시보드의 "Logs" 탭에서 오류 확인

## ⚠️ 주의사항

### **데이터 지속성**
- **중요**: Streamlit Cloud는 앱 재시작 시 모든 데이터가 손실됩니다
- 프로덕션 환경에서는 외부 데이터베이스 사용 권장
- MongoDB Atlas, PostgreSQL 등 클라우드 데이터베이스 연동 고려

### **MongoDB Atlas 연결**
- **네트워크 접근**: IP 화이트리스트에 `0.0.0.0/0` 추가 (모든 IP 허용)
- **사용자 권한**: 데이터베이스 사용자에게 `readWrite` 권한 부여
- **연결 문자열**: Streamlit Secrets에 `MONGODB_URI`로 설정

### **API 키 보안**
- `GEMINI_API_KEY`는 반드시 Streamlit Secrets에 설정
- 코드에 직접 API 키 입력 금지
- API 키 사용량 모니터링 필요

### **성능 최적화**
- 대용량 데이터 처리 시 메모리 사용량 주의
- 캐싱 전략 활용으로 API 호출 최소화
- 이미지나 파일 업로드 시 크기 제한 고려

## 🛠️ 문제 해결

### **일반적인 오류**

#### 1. **ImportError: No module named 'xxx'**
```bash
# requirements.txt에 누락된 패키지 추가
pip install package_name
```

#### 2. **API 키 인증 실패**
- Streamlit Secrets에서 `GEMINI_API_KEY` 확인
- API 키 유효성 및 사용량 확인

#### 3. **메모리 부족 오류**
- 데이터 처리 로직 최적화
- 대용량 데이터 청크 단위 처리

### **디버깅 팁**
- 사이드바의 "🔍 시스템 정보" 섹션 활용
- "📊 저장된 데이터" 개수 확인
- 오류 발생 시 "🗑️ 모든 데이터 초기화" 버튼으로 상태 리셋

## 📈 모니터링 및 유지보수

### **정기 확인사항**
- API 키 사용량 및 만료일
- 앱 성능 및 응답 시간
- 오류 로그 및 사용자 피드백

### **업데이트 방법**
```bash
# 로컬에서 코드 수정 후
git add .
git commit -m "업데이트 내용"
git push origin main

# Streamlit Cloud에서 자동 재배포
```

## 🔗 유용한 링크

- [Streamlit Cloud 공식 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets 관리](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [GitHub 연동 가이드](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/github)

## 📞 지원

문제 발생 시:
1. Streamlit Cloud 로그 확인
2. GitHub Issues에 버그 리포트
3. 개발팀에 문의

---

**⚠️ 중요**: 이 시스템은 Streamlit Cloud 환경에서 임시 데이터 저장소를 사용합니다. 프로덕션 환경에서는 지속적인 데이터 저장을 위한 외부 데이터베이스 연동을 권장합니다.
