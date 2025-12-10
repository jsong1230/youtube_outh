"""
YouTube Data API 및 Analytics API 정상 동작 여부 확인 테스트 코드
token.json 파일을 사용하여 API 연결 및 동작을 검증합니다.
"""
from __future__ import print_function
import os
import sys
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 필요한 스코프 설정
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

TOKEN_FILE = "token.json"
# 대파 채널 핸들 (변경 가능)
CHANNEL_HANDLE = "Daepa_ai"  # @ 없이 입력


def get_channel_id_from_handle(youtube, handle):
    """채널 핸들로부터 채널 ID를 가져옵니다"""
    try:
        # 방법 1: 채널 핸들로 직접 검색 (더 정확)
        # @ 기호 제거
        handle_clean = handle.replace("@", "").strip()
        
        # 채널 검색
        response = youtube.search().list(
            part="snippet",
            q=f"@{handle_clean}",
            type="channel",
            maxResults=10
        ).execute()
        
        if response.get("items"):
            # 검색 결과에서 정확한 핸들 매칭
            for item in response.get("items", []):
                channel_id = item["id"]["channelId"]
                # 채널 정보를 다시 가져와서 핸들 확인
                channel_info = youtube.channels().list(
                    part="snippet",
                    id=channel_id
                ).execute()
                
                if channel_info.get("items"):
                    snippet = channel_info["items"][0]["snippet"]
                    custom_url = snippet.get("customUrl", "")
                    title = snippet.get("title", "")
                    
                    # customUrl에서 핸들 확인 (예: @Daepa_ai)
                    if custom_url and handle_clean.lower() in custom_url.lower():
                        print(f"   ✅ 채널 발견: {title} ({custom_url})")
                        return channel_id
                    
                    # 제목으로도 확인
                    if handle_clean.lower() in title.lower():
                        print(f"   ✅ 채널 발견: {title}")
                        return channel_id
            
            # 정확한 매칭이 안되면 첫 번째 결과 반환
            if response.get("items"):
                channel_id = response["items"][0]["id"]["channelId"]
                channel_info = youtube.channels().list(
                    part="snippet",
                    id=channel_id
                ).execute()
                if channel_info.get("items"):
                    title = channel_info["items"][0]["snippet"].get("title", "")
                    print(f"   ⚠️ 정확한 매칭 실패, 첫 번째 결과 사용: {title}")
                    return channel_id
        
        # 방법 2: forUsername 시도 (구식 방법)
        response = youtube.channels().list(
            part="id,snippet",
            forUsername=handle_clean
        ).execute()
        
        if response.get("items"):
            return response["items"][0]["id"]
        
        return None
    except Exception as e:
        print(f"   ⚠️ 채널 ID 조회 중 오류: {e}")
        return None


def load_credentials():
    """token.json에서 인증 정보 로드"""
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ {TOKEN_FILE} 파일이 존재하지 않습니다.")
        sys.exit(1)

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # 토큰이 만료되었고 refresh_token이 있으면 갱신 시도
        if creds.expired and creds.refresh_token:
            print("🔄 토큰이 만료되었습니다. 갱신 시도 중...")
            try:
                creds.refresh(Request())
                print("✅ 토큰 갱신 성공")
                # 갱신된 토큰 저장
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"❌ 토큰 갱신 실패: {e}")
                sys.exit(1)
        
        if not creds.valid:
            print("❌ 유효하지 않은 인증 정보입니다.")
            sys.exit(1)
        
        return creds
    except Exception as e:
        print(f"❌ 인증 정보 로드 실패: {e}")
        sys.exit(1)


def test_youtube_data_api(creds, channel_id=None):
    """YouTube Data API 정상 동작 여부 테스트"""
    print("\n" + "=" * 50)
    print("📺 YouTube Data API 테스트")
    print("=" * 50)
    
    try:
        youtube = build("youtube", "v3", credentials=creds)
        
        # 채널 ID가 없으면 핸들로부터 가져오기
        if not channel_id:
            print(f"\n1️⃣ 채널 핸들(@{CHANNEL_HANDLE})로부터 채널 ID 조회...")
            channel_id = get_channel_id_from_handle(youtube, CHANNEL_HANDLE)
            if not channel_id:
                print("   ❌ 채널 ID를 찾을 수 없습니다. mine=True로 시도합니다...")
                # fallback: mine=True 사용
                response = youtube.channels().list(
                    part="snippet,statistics",
                    mine=True,
                ).execute()
                if response.get("items"):
                    channel_id = response["items"][0]["id"]
                else:
                    print("   ❌ 채널 정보를 가져올 수 없습니다.")
                    return False
            else:
                print(f"   ✅ 채널 ID: {channel_id}")
        
        # 채널 정보 조회
        print("\n2️⃣ 채널 정보 조회 테스트...")
        response = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id,
        ).execute()
        
        if not response.get("items"):
            print("❌ 채널 정보를 가져올 수 없습니다.")
            return False
        
        # 채널 정보 출력
        for item in response.get("items", []):
            title = item["snippet"]["title"]
            stats = item["statistics"]
            print(f"   ✅ 채널 이름: {title}")
            print(f"   ✅ 구독자 수: {stats.get('subscriberCount', 'N/A')}")
            print(f"   ✅ 총 조회수: {stats.get('viewCount', 'N/A')}")
            print(f"   ✅ 영상 개수: {stats.get('videoCount', 'N/A')}")
        
        # 영상 목록 조회 테스트
        print("\n3️⃣ 최근 영상 목록 조회 테스트...")
        videos_response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            maxResults=5,
            order="date"
        ).execute()
        
        video_count = len(videos_response.get("items", []))
        print(f"   ✅ 최근 영상 {video_count}개 조회 성공")
        
        print("\n✅ YouTube Data API 정상 동작 확인!")
        return channel_id
        
    except HttpError as e:
        print(f"\n❌ YouTube Data API 오류: {e}")
        if e.resp.status == 403:
            print("   → API 권한이 없거나 할당량을 초과했습니다.")
        elif e.resp.status == 401:
            print("   → 인증에 실패했습니다. token.json을 다시 생성해주세요.")
        return None
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return None
        
    except HttpError as e:
        print(f"\n❌ YouTube Data API 오류: {e}")
        if e.resp.status == 403:
            print("   → API 권한이 없거나 할당량을 초과했습니다.")
        elif e.resp.status == 401:
            print("   → 인증에 실패했습니다. token.json을 다시 생성해주세요.")
        return False
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return False


def test_youtube_analytics_api(creds, channel_id=None):
    """YouTube Analytics API 정상 동작 여부 테스트"""
    print("\n" + "=" * 50)
    print("📊 YouTube Analytics API 테스트")
    print("=" * 50)
    
    try:
        analytics = build("youtubeAnalytics", "v2", credentials=creds)
        
        # 채널 ID 설정 (없으면 MINE 사용)
        channel_param = f"channel=={channel_id}" if channel_id else "channel==MINE"
        
        # 최근 7일간 데이터 조회
        print("\n1️⃣ 최근 7일간 통계 조회 테스트...")
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        
        response = analytics.reports().query(
            ids=channel_param,
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            metrics="views,estimatedMinutesWatched,averageViewDuration",
            dimensions="day",
            sort="day",
        ).execute()
        
        column_headers = [h["name"] for h in response.get("columnHeaders", [])]
        rows = response.get("rows", [])
        
        if not rows:
            print("   ⚠️ 조회된 데이터가 없습니다.")
        else:
            print(f"   ✅ {len(rows)}일치 데이터 조회 성공")
            print(f"\n   📋 컬럼: {' | '.join(column_headers)}")
            print("   " + "-" * 60)
            for row in rows[:5]:  # 최대 5개만 출력
                print("   " + " | ".join(str(v) for v in row))
            if len(rows) > 5:
                print(f"   ... 외 {len(rows) - 5}개 행")
        
        # 전체 통계 조회 테스트
        print("\n2️⃣ 전체 통계 조회 테스트...")
        overall_response = analytics.reports().query(
            ids=channel_param,
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            metrics="views,estimatedMinutesWatched,subscribersGained",
        ).execute()
        
        if overall_response.get("rows"):
            overall_data = overall_response["rows"][0]
            print(f"   ✅ 전체 조회수: {overall_data[0]:,}")
            watch_time_hours = overall_data[1] / 60 if len(overall_data) > 1 else 0
            print(f"   ✅ 총 시청 시간: {watch_time_hours:.2f}시간 ({overall_data[1] if len(overall_data) > 1 else 0}분)")
            print(f"   ✅ 신규 구독자: {overall_data[2] if len(overall_data) > 2 else 'N/A'}")
        
        print("\n✅ YouTube Analytics API 정상 동작 확인!")
        return True
        
    except HttpError as e:
        print(f"\n❌ YouTube Analytics API 오류: {e}")
        if e.resp.status == 403:
            print("   → Analytics API 권한이 없거나 할당량을 초과했습니다.")
        elif e.resp.status == 401:
            print("   → 인증에 실패했습니다. token.json을 다시 생성해주세요.")
        return False
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 YouTube API 동작 여부 확인 테스트 시작\n")
    
    # 인증 정보 로드
    print("1️⃣ 인증 정보 로드 중...")
    creds = load_credentials()
    print("   ✅ 인증 정보 로드 완료\n")
    
    # API 테스트 실행
    channel_id = test_youtube_data_api(creds)
    data_api_result = channel_id is not None
    if channel_id:
        print(f"\n📌 조회할 채널 ID: {channel_id}")
    analytics_api_result = test_youtube_analytics_api(creds, channel_id)
    
    # 최종 결과 출력
    print("\n" + "=" * 50)
    print("📋 최종 테스트 결과")
    print("=" * 50)
    print(f"YouTube Data API:      {'✅ 정상' if data_api_result else '❌ 실패'}")
    print(f"YouTube Analytics API: {'✅ 정상' if analytics_api_result else '❌ 실패'}")
    
    if data_api_result and analytics_api_result:
        print("\n🎉 모든 API가 정상적으로 동작합니다!")
        return 0
    else:
        print("\n⚠️ 일부 API에 문제가 있습니다. 위의 오류 메시지를 확인해주세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

