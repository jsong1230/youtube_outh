from __future__ import print_function
import os.path
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 1) 필요한 스코프 설정
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    # 수익까지 보고 싶으면 아래 주석 해제
    # "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
]

TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"


def get_credentials():
    creds = None

    # 이미 토큰이 있으면 그걸 사용 (자동 갱신 포함)
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # 없거나 만료되었는데 refresh도 안되면 새로 로그인
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 토큰 갱신 중...")
            creds.refresh(Request())
        else:
            print("🧩 브라우저로 구글 로그인 창을 띄울게요.")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            # run_local_server: 로컬에서 포트 하나 열고 자동으로 redirect 받아주는 함수
            creds = flow.run_local_server(port=0)

        # 새 토큰 저장
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
            print(f"✅ 토큰 저장 완료: {TOKEN_FILE}")

    return creds


def test_youtube_data_api(creds):
    """내 채널 통계 (구독자 수, 총 조회수 등) 테스트"""
    youtube = build("youtube", "v3", credentials=creds)

    # mine=True 로 내 채널 정보 가져오기
    response = youtube.channels().list(
        part="snippet,statistics",
        mine=True,
    ).execute()

    for item in response.get("items", []):
        title = item["snippet"]["title"]
        stats = item["statistics"]
        print("📺 채널 이름:", title)
        print("👥 구독자:", stats.get("subscriberCount"))
        print("▶️ 총 조회수:", stats.get("viewCount"))
        print("🎬 영상 개수:", stats.get("videoCount"))
        print("-" * 40)


def test_youtube_analytics_api(creds):
    """지난 7일간 일별 조회수/시청시간 분석 테스트"""
    analytics = build("youtubeAnalytics", "v2", credentials=creds)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)

    response = analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date.isoformat(),
        endDate=end_date.isoformat(),
        metrics="views,estimatedMinutesWatched,averageViewDuration",
        dimensions="day",
        sort="day",
    ).execute()

    print("📊 지난 7일간 일별 성과")
    column_headers = [h["name"] for h in response.get("columnHeaders", [])]
    print(" | ".join(column_headers))
    for row in response.get("rows", []):
        print(" | ".join(str(v) for v in row))


def main():
    creds = get_credentials()

    print("\n=== YouTube Data API 테스트 ===")
    test_youtube_data_api(creds)

    print("\n=== YouTube Analytics API 테스트 ===")
    test_youtube_analytics_api(creds)


if __name__ == "__main__":
    main()

