from datetime import datetime, timedelta
import zoneinfo
import pandas as pd
import requests
import streamlit as st

# Streamlit 페이지 기본 설정
st.set_page_config(page_title="일별 박스오피스 순위", layout="wide")


# 1. 한국 시간(Asia/Seoul) 기준 오늘 및 어제 날짜 계산 함수
def get_korea_dates():
    tz_korea = zoneinfo.ZoneInfo("Asia/Seoul")
    now_korea = datetime.now(tz_korea)

    today = now_korea.date()
    yesterday = today - timedelta(days=1)

    return today, yesterday


# 2. KOBIS API 데이터 호출 함수 (날짜별 결과를 한 시간 동안 캐싱)
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

        # API 자체에서 faultInfo를 돌려준 경우 (키 오류 등)
        if "faultInfo" in data:
            message = data["faultInfo"].get(
                "message", "알 수 없는 오류가 발생했습니다."
            )
            return None, f"API 요청에 실패했습니다: {message}"

        # 정상 데이터 추출
        box_office_result = data.get("boxOfficeResult", {})
        movie_list = box_office_result.get("dailyBoxOfficeList", [])

        # 영화 목록이 비어 있는 경우
        if not movie_list:
            return None, "그날은 아직 집계 전입니다"

        return movie_list, None

    except requests.exceptions.RequestException as e:
        return None, f"네트워크 요청 중 오류가 발생했습니다: {e}"


# --- 메인 화면 구성 ---

st.title("🎬 일별 박스오피스 순위")

# secrets.toml에서 인증키 불러오기
if "KOBIS_KEY" not in st.secrets:
    st.error("💡 secrets 설정에 'KOBIS_KEY'가 없습니다.")
    st.info(
        "Streamlit Cloud의 App Settings > Secrets에서 `KOBIS_KEY = '발급받은키'`를 등록해야 합니다."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# 한국 시간 기준 오늘/어제 날짜 구하기
today_korea, max_selectable_date = get_korea_dates()

# --- 사이드바: 달력 날짜 선택 ---
st.sidebar.header("🗓️ 날짜 선택")
selected_date = st.sidebar.date_input(
    label="조회할 날짜를 선택하세요",
    value=max_selectable_date,  # 기본값: 어제
    max_value=max_selectable_date,  # 선택 가능한 가장 늦은 날짜: 어제
    min_value=datetime(2004, 1, 1).date(),  # KOBIS 데이터 제공 범위
)

# KOBIS API 형식(YYYYMMDD)으로 변환
target_date_str = selected_date.strftime("%Y%m%d")

# 날짜 가독성 표시
formatted_date = selected_date.strftime("%Y년 %m월 %d일")
st.subheader(f"📌 {formatted_date} 박스오피스")

# API 호출
movies_data, error_message = fetch_daily_box_office(api_key, target_date_str)

# 에러가 있거나 데이터가 없는 경우 처리
if error_message:
    if error_message == "그날은 아직 집계 전입니다":
        st.warning("⚠️ 그날은 아직 집계 전입니다.")
    else:
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
    # 3. 데이터프레임 변환 및 타입 전처리
    df = pd.DataFrame(movies_data)

    # 문자열 숫자들을 정수형으로 변환
    numeric_cols = [
        "rank",
        "rankInten",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
        "showCnt",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 순위 기준 정렬
    df = df.sort_values(by="rank")

    # --- 데이터 가공 ---

    # 1. 순위 변동(rankInten) 화살표 표시
    # 양수: 🔺 (빨간 위 화살표), 음수: 🔹 (파란 아래 화살표), 0: -
    def format_rank_change(change):
        if change > 0:
            return f"🔺 {change}"
        elif change < 0:
            return f"🔹 {abs(change)}"
        else:
            return "-"

    df["rank_change"] = df["rankInten"].apply(format_rank_change)

    # 2. 누적관객 100만 명(1,000,000명) 이상시 트로피 이모지 붙이기
    def format_movie_title(row):
        title = row["movieNm"]
        if row["audiAcc"] >= 1_000_000:
            return f"🏆 {title}"
        return title

    df["display_movieNm"] = df.apply(format_movie_title, axis=1)

    # --- 1위 영화 메트릭 카드 ---
    st.divider()
    top_movie = df.iloc[0]
    st.subheader(f"🥇 1위 영화: {top_movie['display_movieNm']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("해당 일자 관객수", f"{top_movie['audiCnt']:,} 명")
    col2.metric("누적 관객수", f"{top_movie['audiAcc']:,} 명")
    col3.metric("스크린 수", f"{top_movie['scrnCnt']:,} 개")

    st.divider()

    # --- 관객수 상위 5편 막대그래프 ---
    st.subheader("📊 관객수 상위 5개 영화")

    top5_df = df.head(5).copy()
    # 그래프 X축에는 기존 원본 영화명(movieNm)을 전달
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

    # 표시할 데이터 가공
    display_df = df[
        [
            "rank",
            "rank_change",
            "display_movieNm",
            "openDt",
            "audiCnt",
            "audiAcc",
            "scrnCnt",
        ]
    ].copy()

    display_df.columns = [
        "순위",
        "순위 변동",
        "영화명",
        "개봉일",
        "일일 관객수",
        "누적 관객수",
        "스크린수",
    ]

    # 표로 출력
    st.dataframe(
        display_df,
        column_config={
            "일일 관객수": st.column_config.NumberColumn(format="%d명"),
            "누적 관객수": st.column_config.NumberColumn(format="%d명"),
            "스크린수": st.column_config.NumberColumn(format="%d개"),
        },
        use_container_width=True,
        hide_index=True,
    )
