# PrivKeeper P 장애 대응 자동화 시스템

Gemini AI 기반 고객 문의 자동 분석 및 응답 도구입니다.

## 🎯 주요 기능

- **자동 문제 분류**: Gemini AI를 사용한 고객 문의 자동 분류
- **시나리오 기반 대응**: JSON/Excel 기반 시나리오 DB 활용
- **유사 사례 검색**: ChromaDB 벡터 검색을 통한 유사 사례 제공
- **자동 응답 생성**: 구조화된 고객 응답 이메일 초안 생성
- **웹 기반 인터페이스**: Streamlit을 통한 직관적인 UI

## 🏗️ 시스템 구조

```
streamlit_pratice/
├── app.py                 # 메인 Streamlit 애플리케이션
├── classify_issue.py      # 문제 유형 자동 분류 모듈
├── scenario_db.py         # 시나리오 데이터베이스 모듈
├── vector_search.py       # ChromaDB 벡터 검색 모듈
├── gpt_handler.py         # Gemini API 핸들러
├── requirements.txt       # Python 패키지 의존성
├── README.md             # 프로젝트 문서
├── 프롬프트.txt           # AI 프롬프트 템플릿
├── PK P DB.json          # 시나리오 데이터 (JSON)
├── 수정된_대응_시나리오표.xlsx  # 시나리오 데이터 (Excel)
└── privkeeper-p-d85579598b32.json  # Gemini API 인증 키
```

## 🚀 설치 및 실행

### 1. 필수 요구사항

- Python 3.8 이상
- Google Cloud 프로젝트 설정
- Gemini API 키

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 설정

1. Google Cloud 프로젝트에서 Gemini API 활성화
2. 서비스 계정 키 파일 (`privkeeper-p-d85579598b32.json`)을 프로젝트 루트에 배치
3. 필요한 데이터 파일들이 올바른 위치에 있는지 확인

### 4. 애플리케이션 실행

```bash
streamlit run app.py
```

## 📋 사용 방법

### 1. 고객 문의 입력
- 고객사 정보와 문의 내용을 상세히 입력
- 시스템이 자동으로 문제 유형을 분류합니다

### 2. AI 분석
- Gemini AI가 자동으로 증상 분석, 원인 추정, 조치 방향 제시
- 유사 사례 검색을 통한 참고 정보 제공
- 고객 응답 이메일 초안 자동 생성

### 3. 검토 및 발송
- 엔지니어가 AI 분석 결과 검토
- 필요시 수정 후 고객에게 응답

## 🔧 기술 스택

- **AI 모델**: Google Gemini 1.5 Pro
- **벡터 검색**: ChromaDB
- **웹 프레임워크**: Streamlit
- **데이터 소스**: JSON + Excel
- **언어**: Python 3.8+

## 📊 주요 모듈

### classify_issue.py
- Gemini API를 사용한 문제 유형 자동 분류
- 키워드 기반 백업 분류 로직
- 7-10개 문제 유형 지원

### scenario_db.py
- JSON/Excel 기반 시나리오 데이터 로딩
- 문제 유형별 조건과 해결책 조회
- 매뉴얼 참조 정보 제공

### vector_search.py
- ChromaDB를 사용한 유사 사례 검색
- 벡터 기반 유사도 계산
- 프롬프트용 사례 포맷팅

### gpt_handler.py
- Gemini API 호출 및 응답 생성
- 프롬프트 템플릿 조립
- 응답 구조화 및 파싱

## ⚠️ 주의사항

- AI 분석 결과는 참고용이며, 최종 검토 후 발송
- 민감한 정보는 입력하지 않도록 주의
- 긴급한 경우 즉시 담당 엔지니어에게 연락
- API 키 파일은 절대 GitHub에 업로드하지 마세요

## 📞 지원 연락처

- 기술지원: 02-678-1234
- 이메일: support@privkeeper.com
- 긴급상황: 010-3456-7890

## 📄 라이선스

©2024 PrivKeeper P 장애 대응 자동화 시스템
