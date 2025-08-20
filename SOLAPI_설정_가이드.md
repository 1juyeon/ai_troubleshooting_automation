# SOLAPI 설정 가이드

## 📱 SOLAPI란?
SOLAPI는 국내 최고의 SMS/MMS 발송 서비스로, 안정적이고 빠른 문자 발송이 가능합니다.

## 🔐 인증 방식

SOLAPI는 HMAC-SHA256 기반 인증 방식을 사용합니다:

### HMAC-SHA256 인증
- **방식**: API Key와 Secret을 사용한 HMAC-SHA256 서명
- **헤더**: `Authorization: hmac-sha256 {API_KEY}:{SIGNATURE}`
- **타임스탬프**: `X-Timestamp` 헤더에 Unix timestamp 포함
- **보안**: 높은 보안성을 제공하는 서명 기반 인증

### 기존 인증 방식 (지원 중단)
- Basic Authentication
- Bearer Token
- Query Parameters
- Custom Headers

### HMAC 인증 작동 원리
1. **타임스탬프 생성**: 현재 Unix timestamp 생성
2. **메시지 구성**: `{METHOD} {PATH}\n{TIMESTAMP}\n{BODY}` 형식
3. **서명 생성**: HMAC-SHA256으로 메시지 서명
4. **헤더 전송**: Authorization과 X-Timestamp 헤더에 포함

### 보안 장점
- **재생 공격 방지**: 타임스탬프로 요청 유효성 검증
- **무결성 보장**: HMAC 서명으로 데이터 변조 방지
- **인증 강화**: API Key와 Secret의 조합으로 이중 인증

## 🔑 API 키 발급 방법

### 1. SOLAPI 계정 생성
- [SOLAPI 공식 사이트](https://solapi.com)에서 회원가입
- 본인인증 및 사업자등록증 등록 (필수)

### 2. 프로젝트 생성
- 대시보드 → "프로젝트" → "새 프로젝트 생성"
- 프로젝트명 입력 (예: "PrivKeeper SMS")

### 3. API 키 생성
- 프로젝트 선택 → "API 키 관리" → "새 API 키 생성"
- **API 키 형식**: `NCSBUQGP66BV505E` (20자리) 또는 `NCSFMJ9TRVXACUIW` (20자리 영문자+숫자)
- **API Secret 형식**: `OM6ZS1QYIRXCW8YOWWV7OS1Q1BUF4QAX` (32자리 영문자+숫자)
- **참고**: SOLAPI는 다양한 길이의 API 키를 지원합니다 (최소 16자리 이상)

### 4. 발신자 번호 등록
- "발신번호 관리" → "새 발신번호 등록"
- 사용할 휴대폰 번호 입력 (예: 010-1234-5678)
- 인증번호 확인 후 등록 완료

## ⚠️ 중요 설정 사항

### API 키 보안
- **IP 제한 설정**: 프로덕션 환경에서는 허용 IP 주소 제한 권장
- **권한 설정**: SMS 발송 및 계정 조회 권한 확인
- **사용량 모니터링**: 월 사용량 및 비용 확인

### 발신자 번호
- **사전 등록 필수**: SOLAPI에 등록된 발신자 번호만 사용 가능
- **인증 완료**: 본인인증이 완료된 번호만 사용 가능
- **형식**: 010-1234-5678 또는 01012345678

## �� PrivKeeper 연동 설정

### 1. Streamlit Cloud Secrets 설정
```toml
# .streamlit/secrets.toml
SOLAPI_API_KEY = "NCSFMJ9TRVXACUIW"
SOLAPI_API_SECRET = "HQGV2DZ4CC0UV7LZ2TWLW0O3VSHX53VO"
```

### 2. 사이드바 설정
- "SOLAPI API Key" 입력란에 API 키 입력
- "SOLAPI API Secret" 입력란에 API Secret 입력
- "발신자 번호" 입력란에 등록된 발신자 번호 입력

### 3. 연결 테스트
- "🔗 SOLAPI 연결 테스트" 버튼 클릭
- 성공 시: "✅ SOLAPI 연결 성공 (잔액: X,XXX원)" 메시지 표시
- 실패 시: 구체적인 오류 메시지와 해결 방법 제시

## 🚨 HTTP 400 오류 해결 방법

### 일반적인 원인과 해결책

#### 1. 잘못된 API 키 형식
- **증상**: HTTP 400 오류
- **원인**: API 키가 16자리 미만이거나 특수문자 포함
- **해결**: SOLAPI 대시보드에서 새로운 API 키 재생성
- **참고**: SOLAPI는 다양한 길이의 API 키를 지원합니다 (최소 16자리 이상)

#### 2. 인증 방식 오류
- **증상**: HTTP 400 또는 401 오류
- **원인**: HMAC-SHA256 인증 실패
- **해결 방법**:
  - API Key와 Secret이 정확한지 확인
  - 시스템 시간이 정확한지 확인
  - SOLAPI 대시보드에서 API 키 상태 확인

#### 3. 발신자 번호 미등록
- **증상**: SMS 발송 시 HTTP 400 오류
- **원인**: SOLAPI에 등록되지 않은 발신자 번호 사용
- **해결**: SOLAPI 대시보드에서 발신자 번호 등록

#### 4. API 권한 부족
- **증상**: HTTP 403 오류
- **원인**: API 키에 필요한 권한이 없음
- **해결**: SOLAPI 대시보드에서 API 키 권한 확인 및 수정

#### 5. HMAC 인증 관련 오류
- **증상**: HTTP 400 ValidationError
- **원인**: 타임스탬프 오차 또는 서명 생성 실패
- **해결 방법**:
  - 시스템 시간 동기화 확인
  - API Key와 Secret 재입력
  - SOLAPI 대시보드에서 API 키 재생성

## 📱 SMS 발송 방법

### 1. AI 분석 결과에서 발송
- "AI 분석 결과" 탭에서 분석 완료 후
- "수신자 이름"과 "수신자 전화번호" 입력
- "메시지 내용" 확인 및 수정
- "📱 SMS 발송" 버튼 클릭

### 2. 이력 관리에서 발송
- "이력 관리" 탭에서 특정 이력 선택
- "상세 보기" 클릭
- 모달에서 SMS 발송 정보 입력
- "📱 SMS 발송" 버튼 클릭

## 💰 요금 및 제한사항

### SMS 요금
- **국내 SMS**: 건당 약 20원 (사용량에 따라 할인)
- **MMS**: 건당 약 300원
- **월 사용량**: 무제한 (잔액 한도 내)

### 발송 제한
- **시간 제한**: 24시간 발송 가능
- **수량 제한**: 일일 발송 한도 없음
- **내용 제한**: 불법/스팸 내용 금지

## 🔍 문제 해결

### 연결 테스트 실패 시
1. **API 키 확인**: 32자리 영문자+숫자 형식인지 확인
2. **인터넷 연결**: 네트워크 상태 확인
3. **SOLAPI 서버**: SOLAPI 서비스 상태 확인
4. **방화벽**: 회사/기관 방화벽 설정 확인

### SMS 발송 실패 시
1. **잔액 확인**: SOLAPI 계정 잔액 확인
2. **발신자 번호**: 등록된 발신자 번호인지 확인
3. **수신자 번호**: 올바른 휴대폰 번호 형식인지 확인
4. **메시지 내용**: 특수문자나 이모지 사용 제한

## 📞 고객 지원

### SOLAPI 고객센터
- **전화**: 1544-0708
- **이메일**: support@solapi.com
- **운영시간**: 평일 09:00-18:00

### PrivKeeper 지원
- **이메일**: support@privkeeper.com
- **문의**: GitHub Issues 또는 이메일

## 📚 추가 자료

- [SOLAPI 공식 문서](https://docs.solapi.com)
- [SOLAPI API 레퍼런스](https://docs.solapi.com/reference)
- [SOLAPI 개발자 가이드](https://docs.solapi.com/guides)
- [SOLAPI FAQ](https://solapi.com/faq)
