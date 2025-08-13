# ☁️ Streamlit Cloud 배포 가이드

PrivKeeper P 장애 대응 자동화 시스템을 Streamlit Cloud에 배포하는 방법을 안내합니다.

## 🚀 배포 전 준비사항

### 1. GitHub 저장소 준비
- 모든 코드가 GitHub에 푸시되어 있어야 합니다
- `requirements.txt` 파일이 포함되어 있어야 합니다
- `.streamlit/` 디렉토리와 설정 파일들이 포함되어 있어야 합니다

### 2. API 키 준비
- Gemini API 키가 필요합니다
- [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키를 발급받으세요

## 📋 배포 단계

### 1단계: Streamlit Cloud 접속
1. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
2. GitHub 계정으로 로그인
3. "New app" 버튼 클릭

### 2단계: 앱 설정
```
Repository: your-username/streamlit_pratice
Branch: main (또는 원하는 브랜치)
Main file path: app.py
```

### 3단계: 고급 설정
- **Python version**: 3.9 이상
- **Requirements file**: `requirements.txt`
- **Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

### 4단계: Secrets 설정
`.streamlit/secrets.toml` 파일을 생성하거나 Streamlit Cloud의 Secrets 관리에서 설정:

```toml
GEMINI_API_KEY = "your-actual-gemini-api-key"
```

### 5단계: 배포
- "Deploy!" 버튼 클릭
- 배포 완료까지 대기 (보통 2-5분 소요)

## 🔒 데이터 지속성 설정

### 자동 백업 시스템
- 모든 데이터가 자동으로 `/tmp/streamlit_cloud_data` 디렉토리에 저장됩니다
- 서버 재부팅 시에도 데이터가 유지됩니다
- 별도의 설정이 필요하지 않습니다

### 수동 백업
1. 앱 실행 후 "이력 관리" 탭으로 이동
2. "🔒 데이터 백업 및 복구" 섹션 확장
3. "💾 데이터 백업" 버튼으로 수동 백업 생성

## 🛠️ 문제 해결

### 일반적인 배포 문제

#### 1. 의존성 설치 실패
```
Error: Could not find a version that satisfies the requirement
```
**해결방법:**
- `requirements.txt`의 버전을 더 유연하게 설정
- 예: `streamlit>=1.32.0` → `streamlit>=1.30.0`

#### 2. 메모리 부족
```
Error: Process killed due to memory limit
```
**해결방법:**
- 앱의 메모리 사용량 최적화
- 불필요한 데이터 로딩 제거
- Streamlit Cloud의 더 높은 티어 사용 고려

#### 3. API 키 인증 실패
```
Error: Invalid API key
```
**해결방법:**
- Streamlit Secrets에서 API 키 재설정
- API 키의 유효성 확인
- Gemini API 사용 권한 확인

### 데이터 지속성 문제

#### 1. 서버 재부팅 후 데이터 사라짐
**확인사항:**
- "이력 관리" 탭에서 환경 정보 확인
- "☁️ Streamlit Cloud 환경" 메시지가 표시되는지 확인
- 백업 파일이 생성되었는지 확인

**해결방법:**
- "🔄 데이터 복구" 버튼으로 최신 백업에서 복구
- 수동으로 "💾 데이터 백업" 생성

#### 2. 백업 파일 생성 실패
**확인사항:**
- 파일 쓰기 권한 확인
- 디스크 공간 확인
- 에러 메시지 상세 내용 확인

**해결방법:**
- 앱 재시작
- 다른 백업 경로 시도
- Streamlit Cloud 지원팀 문의

## 📊 모니터링 및 유지보수

### 1. 앱 상태 모니터링
- Streamlit Cloud 대시보드에서 앱 상태 확인
- 로그 확인 및 오류 모니터링
- 사용량 통계 확인

### 2. 정기적인 백업
- 주기적으로 수동 백업 생성
- 백업 파일의 무결성 확인
- 오래된 백업 파일 정리

### 3. 성능 최적화
- 메모리 사용량 모니터링
- 응답 시간 확인
- 사용자 피드백 수집

## 🔄 업데이트 및 배포

### 1. 코드 업데이트
```bash
# 로컬에서 코드 수정
git add .
git commit -m "Update: 새로운 기능 추가"
git push origin main
```

### 2. 자동 배포
- GitHub에 푸시하면 Streamlit Cloud에서 자동으로 재배포
- 배포 상태는 Streamlit Cloud 대시보드에서 확인 가능

### 3. 롤백
- 이전 버전으로 되돌리려면 GitHub에서 이전 커밋으로 체크아웃
- 또는 Streamlit Cloud에서 이전 배포 버전 선택

## 📞 지원 및 문의

### Streamlit Cloud 지원
- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Community 포럼](https://discuss.streamlit.io/)

### PrivKeeper P 내부 지원
- 개발팀 문의
- 시스템 관리자 문의

## 📝 체크리스트

배포 전 확인사항:
- [ ] GitHub에 모든 코드 푸시 완료
- [ ] `requirements.txt` 파일 포함
- [ ] `.streamlit/` 설정 파일 포함
- [ ] Gemini API 키 준비 완료
- [ ] Streamlit Cloud 계정 생성 완료

배포 후 확인사항:
- [ ] 앱 정상 실행 확인
- [ ] API 키 인증 확인
- [ ] 데이터 지속성 테스트
- [ ] 백업 기능 테스트
- [ ] 사용자 접근 테스트

---

**⚠️ 주의사항**: 이 가이드는 PrivKeeper P 내부 사용을 위한 것입니다. 외부 공개 시 보안에 주의하세요.
