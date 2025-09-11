# 🔧 PrivKeeper P 장애 대응 자동화 시스템

Gemini AI & GPT 기반 고객 문의 자동 분석 및 응답 도구

## ✨ 주요 기능

- **AI 기반 문제 유형 자동 분류**
- **시나리오 기반 대응 방안 제시**
- **유사 사례 검색 및 참고 정보 제공**
- **고객 응답 이메일 초안 자동 생성**
- **다중 사용자 이력 관리**
- **벡터 검색 기반 지식 베이스**
- **다중 AI 모델 지원** (Gemini 1.5/2.0, GPT 3.5/4)
- **모델별 최적화된 응답 품질**

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
# Gemini API 키 (필수 - 모든 Gemini 모델 사용 가능)
GEMINI_API_KEY = "your-actual-gemini-api-key"

# OpenAI API 키 (선택사항 - GPT 모델 사용)
OPENAI_API_KEY = "your-openai-api-key"

# 기존 호환성 유지 (선택사항)
GOOGLE_API_KEY = "your-google-api-key"
```

**지원하는 AI 모델:**
- **Gemini 모델**: 1.5 Pro, 1.5 Flash, 2.0 Flash (실험적)
- **GPT 모델**: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo

### 4. 앱 실행
```bash
streamlit run app.py
```

## 📊 사용 방법

### 1. 고객 문의 입력
- 고객 정보 및 문의 내용 입력
- 시스템이 자동으로 문제 유형 분류

### 2. AI 분석
- "AI 분석 요청" 버튼 클릭
- **AI 모델 선택**: 사이드바에서 원하는 AI 모델 선택
  - Gemini 1.5 Pro: 가장 정확하고 상세한 분석
  - Gemini 1.5 Flash: 빠른 응답, 기본 분석
  - Gemini 2.0 Flash: 최신 기술, 빠른 응답 (실험적)
  - GPT-4o: OpenAI 최신 모델, 고품질 분석
  - GPT-4 Turbo: 빠른 응답, 고품질
  - GPT-3.5 Turbo: 빠른 응답, 기본 분석
- 선택된 AI 모델이 자동으로 분석 수행

### 3. 결과 확인
- AI 분석 결과 탭에서 상세 결과 확인
- 이메일 초안 복사 및 발송

## 🔍 문제 해결

### API 키 관련 문제
- **Gemini API 키**: Streamlit Secrets 또는 환경변수 설정
- **OpenAI API 키**: GPT 모델 사용 시 필요
- **권한 확인**: 각 API 서비스의 사용 권한 확인
- **모델별 지원**: 일부 모델은 API 키 설정 후에만 사용 가능

### 디버깅 도구
시스템 상태 탭에서 각 모듈의 상태를 확인할 수 있습니다.

## 📁 프로젝트 구조

```
streamlit_pratice/
├── app.py                    # 메인 애플리케이션
├── classify_issue.py         # 문제 유형 분류 모듈
├── scenario_db.py            # 시나리오 데이터베이스
├── vector_search.py          # 벡터 검색 래퍼
├── gemini_handler.py         # Gemini AI 핸들러 (다중 모델 지원)
├── openai_handler.py         # OpenAI GPT 핸들러
├── gpt_handler.py            # GPT 핸들러 (호환성)
├── database.py               # 기본 데이터베이스 (JSON)
├── multi_user_database.py    # 다중 사용자 데이터베이스
├── mongodb_handler.py        # MongoDB Atlas 핸들러
├── vector_db.py              # 벡터 데이터베이스
├── solapi_handler.py         # SOLAPI SMS 핸들러
├── requirements.txt           # 의존성 목록
├── README.md                 # 프로젝트 문서
├── mongodb_atlas_setup_guide.md  # MongoDB 설정 가이드
├── safe_deployment_guide.md  # 안전 배포 가이드
├── streamlit_cloud_deployment_guide.md  # Streamlit Cloud 배포 가이드
├── SOLAPI_설정_가이드.md     # SOLAPI 설정 가이드
├── 프롬프트.txt              # AI 프롬프트 템플릿
├── user_data/                # 사용자 데이터
├── user_sessions/            # 사용자 세션
└── vector_data/              # 벡터 데이터
```

## 🔧 기술 스택

- **AI 모델**: 
  - **Gemini 모델**: 1.5 Pro, 1.5 Flash, 2.0 Flash (실험적)
  - **GPT 모델**: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo
- **웹 프레임워크**: Streamlit
- **데이터베이스**: 
  - **로컬**: JSON 파일 기반
  - **클라우드**: MongoDB Atlas
- **벡터 검색**: scikit-learn 기반 텍스트 유사도
- **데이터 처리**: Pandas, NumPy
- **API 통신**: Requests
- **SMS 발송**: SOLAPI

## 📝 라이선스

이 프로젝트는 PrivKeeper P 내부 사용을 위한 것입니다.

## 🤝 기여

프로젝트 개선을 위한 제안이나 버그 리포트는 언제든 환영합니다.
