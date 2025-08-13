# 🔧 PrivKeeper P 장애 대응 자동화 시스템

Gemini AI 기반 고객 문의 자동 분석 및 응답 도구

## ✨ 주요 기능

- **AI 기반 문제 유형 자동 분류**
- **시나리오 기반 대응 방안 제시**
- **유사 사례 검색 및 참고 정보 제공**
- **고객 응답 이메일 초안 자동 생성**
- **다중 사용자 이력 관리**
- **벡터 검색 기반 지식 베이스**
- **🔒 데이터 지속성 및 백업 시스템**
- **☁️ Streamlit Cloud 완벽 지원**

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd streamlit_pratice
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Streamlit Secrets 설정 (권장)
`.streamlit/secrets.toml` 파일을 생성하고 API 키를 설정하세요:

```toml
# Gemini API 키 (필수)
GEMINI_API_KEY = "your-actual-gemini-api-key"

# 기존 호환성 유지 (선택사항)
GOOGLE_API_KEY = "your-google-api-key"
```

### 4. 앱 실행
```bash
streamlit run app.py
```

## ☁️ Streamlit Cloud 배포

### 자동 데이터 지속성
- **서버 재부팅 시에도 데이터 유지**: 이력 데이터가 자동으로 영구 저장소에 백업됩니다
- **실시간 백업**: 모든 분석 결과가 즉시 파일 시스템에 저장됩니다
- **자동 복구**: 서버 재시작 시 이전 데이터를 자동으로 복원합니다

### 배포 방법
1. GitHub에 코드 푸시
2. Streamlit Cloud에서 새 앱 생성
3. GitHub 저장소 연결
4. `GEMINI_API_KEY`를 Streamlit Secrets에 설정
5. 배포 완료!

## 📊 사용 방법

### 1. 고객 문의 입력
- 고객 정보 및 문의 내용 입력
- 시스템이 자동으로 문제 유형 분류

### 2. AI 분석
- "AI 분석 요청" 버튼 클릭
- Gemini AI가 자동으로 분석 수행

### 3. 결과 확인
- AI 분석 결과 탭에서 상세 결과 확인
- 이메일 초안 복사 및 발송

### 4. 데이터 관리
- **자동 백업**: 모든 데이터가 자동으로 백업됩니다
- **수동 백업**: "데이터 백업 및 복구" 섹션에서 수동 백업 가능
- **데이터 복구**: 백업 파일에서 데이터 복구 가능

## 🔒 데이터 지속성 시스템

### 로컬 환경
- 파일 시스템 기반 저장
- `user_data/` 디렉토리에 JSON 파일로 저장

### Streamlit Cloud 환경
- `/tmp/streamlit_cloud_data` 디렉토리에 영구 저장
- 세션 상태와 파일 시스템 이중 저장
- 서버 재부팅 시에도 데이터 유지

### 백업 및 복구
- **자동 백업**: 모든 데이터 변경 시 자동 백업
- **수동 백업**: 사용자가 원하는 시점에 백업 생성
- **백업 목록**: 생성된 백업 파일들의 목록 확인
- **데이터 복구**: 백업 파일에서 데이터 복원

## 🔍 문제 해결

### API 키 관련 문제
- **API 키 설정**: Streamlit Secrets 또는 환경변수 설정
- **권한 확인**: Gemini API 사용 권한 확인

### 데이터 지속성 문제
- **서버 재부팅 후 데이터 사라짐**: 자동 복구 기능이 작동하는지 확인
- **백업 파일 없음**: "데이터 백업" 버튼으로 수동 백업 생성
- **복구 실패**: 백업 파일의 무결성 확인

### 디버깅 도구
시스템 상태 탭에서 각 모듈의 상태를 확인할 수 있습니다.

## 📁 프로젝트 구조

```
streamlit_pratice/
├── app.py                    # 메인 애플리케이션 (데이터 지속성 기능 포함)
├── classify_issue.py         # 문제 유형 분류 모듈
├── scenario_db.py            # 시나리오 데이터베이스
├── vector_search.py          # 벡터 검색 래퍼
├── gpt_handler.py            # Gemini AI 핸들러
├── database.py               # 기본 데이터베이스
├── multi_user_database.py    # 다중 사용자 데이터베이스 (클라우드 지원)
├── vector_db.py              # 벡터 데이터베이스
├── requirements.txt           # 의존성 목록
├── README.md                 # 프로젝트 문서
├── safe_deployment_guide.md  # 배포 가이드
├── streamlit_cloud_deployment_guide.md  # Streamlit Cloud 배포 가이드
├── 프롬프트.txt              # AI 프롬프트 템플릿
├── user_data/                # 사용자 데이터 (로컬 환경)
├── user_sessions/            # 사용자 세션
├── vector_data/              # 벡터 데이터
└── persistent_data/          # 영구 데이터 저장소 (클라우드 환경)
```

## 🔧 기술 스택

- **AI 모델**: Google Gemini 1.5 Pro
- **웹 프레임워크**: Streamlit
- **벡터 데이터베이스**: ChromaDB
- **데이터 처리**: Pandas, NumPy
- **API 통신**: Requests
- **데이터 지속성**: Streamlit Cache + 파일 시스템

## 🆕 최신 업데이트

### v2.0 - 데이터 지속성 시스템
- ✅ Streamlit Cloud에서 서버 재부팅 시에도 데이터 유지
- ✅ 자동 백업 및 복구 시스템
- ✅ 이중 저장 (세션 상태 + 파일 시스템)
- ✅ 데이터 백업 및 복구 UI 추가
- ✅ "전체 AI 응답" 표시 기능 개선

## 📝 라이선스

이 프로젝트는 PrivKeeper P 내부 사용을 위한 것입니다.

## 🤝 기여

프로젝트 개선을 위한 제안이나 버그 리포트는 언제든 환영합니다.
