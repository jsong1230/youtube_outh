# YouTube OAuth 인증 및 API 테스트

YouTube Data API와 YouTube Analytics API를 사용하여 채널 정보와 분석 데이터를 조회하는 Python 스크립트입니다.

## 기능

- YouTube OAuth2 인증 (자동 토큰 갱신 지원)
- 채널 통계 조회 (구독자 수, 총 조회수, 영상 개수)
- 지난 7일간 일별 분석 데이터 조회 (조회수, 시청 시간, 평균 시청 시간)

## 사전 요구사항

- Python 3.6 이상
- Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성 필요

## 설치

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

## 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. YouTube Data API v3 및 YouTube Analytics API 활성화
3. OAuth 2.0 클라이언트 ID 생성 (애플리케이션 유형: 데스크톱 앱)
4. 클라이언트 ID를 다운로드하여 `client_secret.json` 파일로 저장

## 사용 방법

```bash
python yt_auth.py
```

첫 실행 시:
- 브라우저가 자동으로 열리며 Google 계정 로그인 요청
- YouTube 데이터 접근 권한 승인
- 인증 완료 후 `token.json` 파일이 생성되어 이후 자동 인증

## 주요 기능 설명

### 채널 통계 조회
- 채널 이름, 구독자 수, 총 조회수, 영상 개수 출력

### 분석 데이터 조회
- 지난 7일간 일별 조회수, 시청 시간, 평균 시청 시간 출력

## 파일 구조

```
youtube_outh/
├── yt_auth.py           # 메인 스크립트
├── client_secret.json   # OAuth 클라이언트 정보 (Google Cloud Console에서 다운로드)
├── token.json          # 인증 토큰 (자동 생성)
├── requirements.txt    # Python 패키지 의존성
└── README.md           # 이 파일
```

## 주의사항

- `client_secret.json` 파일은 절대 공개 저장소에 업로드하지 마세요
- `token.json` 파일도 개인 정보이므로 보안에 주의하세요
- 수익 정보까지 조회하려면 `yt_auth.py`의 주석 처리된 스코프를 활성화하세요

## 참고 자료

- [YouTube Data API 문서](https://developers.google.com/youtube/v3)
- [YouTube Analytics API 문서](https://developers.google.com/youtube/analytics)

