from datetime import datetime, timedelta
import zoneinfo
import pandas as pd
import requests
import streamlit as st


# Streamlit 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(page_title="어제 박스오피스 순위", layout="wide")


# 1. 한국 시간(Asia/Seoul) 기준 '어제' 날짜 계산 함수
def get_korea_yesterday_str():
    # 배포 서버의 시계가 해외 기준이어도 한국 시간을 정확히 가져옵니다.
    tz_korea = zoneinfo.ZoneInfo("Asia/Seoul")
    now_korea = datetime.now(tz_korea)
    yesterday = now_korea - timedelta(days=1)

    # YYYYMMDD 형태로 변환 (예: 20260908)
    return yesterday.strftime("%Y%m%d")


# 2. KOBIS API 데이터 호출 함수 (한 시간 동안 결과 기억/캐싱)
@st.cache_data(ttl=3600)
def fetch_daily_box_office(api_key, target_date):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        response = requests.get(url, params=params, timeout=10)

        # HTTP status code 오류 체크
        if response.status_code != 200:
            return None, f"서버 응답 오류가 발생했습니다. (상태 코드: {response.status_code})"

        data = response.json()

        # 인증키 오류 등 KOBIS API 자체에서 faultInfo를 돌려준 경우
        if "faultInfo" in data:
            message = data["faultInfo"].get("message", "알 수 없는 오류가 발생했습니다.")
            return None, f"API 요청에 실패했습니다: {message}"

        # 정상 데이터 추출
        box_office_result = data.get("boxOfficeResult", {})
        movie_list = box_office_result.get("dailyBoxOfficeList", [])

        if not movie_list:
            return None, "영화 목록이 비어 있습니다. 해당 날짜의 데이터가 아직 없거나 집계 중일 수 있습니다."

        return movie_list, None

    except requests.exceptions.RequestException as e:
        return None, f"네트워크 요청 중 오류가 발생했습니다: {e}"


# --- 메인 화면 구성 ---

st.title("🎬 어제 일별 박스오피스 순위")

# secrets.toml에서 인증키 불러오기
if "KOBIS_KEY" not in st.secrets:
    st.error("💡 secrets 설정에 'KOBIS_KEY'가 없습니다.")
    st.info(
        "Streamlit Cloud의 App Settings > Secrets에서 `KOBIS_KEY = '발급받은키'`를 등록해야 합니다."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]
target_date = get_korea_yesterday_str()

# 날짜 표시 (YYYY년 MM월 DD일 형식으로 가독성 있게)
formatted_date = f"{target_date[:4]}년 {target_date[4:6]}월 {target_date[6:]}일"
st.caption(f"기준일: {formatted_date} (한국 시간 어제)")

# API 호출 실행
movies_data, error_message = fetch_daily_box_office(api_key, target_date)

# 에러가 있거나 데이터가 없는 경우 안내문 출력
if error_message:
    st.error(error_message)
    st.warning(
        """
    **확인해 보세요!**
    1. Streamlit Cloud 비밀 금고(Secrets)에 `KOBIS_KEY`가 바르게 입력되었는지 확인하세요.
    2. KOBIS API 키가 유효한지, 일일 요청 한도를 초과하지 않았는지 확인해 주세요.
    3. 네트워크 상태가 정상인지 확인해 주세요.
    """
    )
else:
    # 3. 데이터프레임 변환 및 숫자형 변환
    df = pd.DataFrame(movies_data)

    # 문자열 숫자를 정수형/실수형으로 변환
    numeric_cols = ["rank", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 순위 기준으로 정렬
    df = df.sort_values(by="rank")

    # --- 1위 영화 메트릭 카드 ---
    st.divider()
    top_movie = df.iloc[0]
    st.subheader(f"🥇 1위 영화: {top_movie['movieNm']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("어제 관객수", f"{top_movie['audiCnt']:,} 명")
    col2.metric("누적 관객수", f"{top_movie['audiAcc']:,} 명")
    col3.metric("스크린 수", f"{top_movie['scrnCnt']:,} 개")

    st.divider()

    # --- 관객수 상위 5편 막대그래프 ---
    st.subheader("📊 관객수 상위 5개 영화")

    top5_df = df.head(5).copy()
    # 그래프에 관객수가 직관적으로 보이도록 설정
    st.bar_chart(
        data=top5_df,
        x="movieNm",
        y="audiCnt",
        color="#FF4B4B",
        use_container_width=True,
    )

    st.divider()

    # --- 전체 순위 표 ---
    st.subheader("📋 박스오피스 전체 순위")

    # 보여줄 컬럼 선택 및 보기 좋은 한국어 이름으로 변경
    display_df = df[
        ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
    ].copy()
    display_df.columns = [
        "순위",
        "영화명",
        "개봉일",
        "어제 관객수",
        "누적 관객수",
        "스크린수",
    ]

    # 숫자에 천 단위 쉼표 적용해서 표로 출력
    st.dataframe(
        display_df,
        column_config={
            "어제 관객수": st.column_config.NumberColumn(format="%d명"),
            "누적 관객수": st.column_config.NumberColumn(format="%d명"),
            "스크린수": st.column_config.NumberColumn(format="%d개"),
        },
        use_container_width=True,
        hide_index=True,
    )
