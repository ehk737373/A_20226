import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정 (넓은 레이아웃 적용)
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")

st.title("🎬 영화 박스오피스 데이터 분석 앱")


# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 데이터를 매번 다시 로드하지 않고 캐싱합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치가 포함된 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 datetime 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 기준일자 순서대로 데이터 정렬 (오름차순)
    df = df.sort_values(by="기준일자", ascending=True)

    return df


# 데이터 로드
df = load_data()


# [3. 영화 선택 기능]
# 누적관객수가 가장 높은 순으로 영화 목록을 정렬하기 위해 처리합니다.
# 영화별 최대 누적관객수를 구해 내림차순 정렬
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에서 영화 선택
st.sidebar.header("🔍 검색 설정")
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요 (누적관객수 순)", movie_order
)

# 선택한 영화의 데이터만 필터링
filtered_df = df[df["영화명"] == selected_movie]


# [5. 기타 - 구역 나누기]
st.header(f"📊 '{selected_movie}' 데이터 시각화")

# 구역 1: 해당일관객수 추이 선그래프
with st.container():
    st.subheader("1. 일별 관객수 변화 추이")

    # [4. 선그래프 그리기]
    # Plotly를 사용하여 기준일자별 해당일관객수 선그래프 생성
    fig1 = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}'의 일별 관객수 변화",
        labels={"기준일자": "날짜", "해당일관객수": "해당일 관객수(명)"},
        markers=True,  # 데이터 포인트에 점 표시
    )

    # 그래프 출력
    st.plotly_chart(fig1, use_container_width=True)

    # 그래프 설명 문구 자리
    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 개봉 이후 날짜가 경과함에 따라 해당일 관객수가 어떻게 변화하고 증가/감소하는지 흐름을 파악할 수 있습니다."
    )

st.divider()  # 구역 구분을 위한 줄 바꿈

# 구역 2: 누적관객수 영역 차트 (Area Chart)
with st.container():
    st.subheader("2. 누적 관객수 증가 추이")

    # Plotly를 사용하여 기준일자별 누적관객수 영역 차트 생성
    fig2 = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"'{selected_movie}'의 누적 관객수 변화",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
    )

    # 영역차트 디자인 커스텀 (선 색상 및 면적 채우기 강조)
    fig2.update_traces(line_color="#2E86C1", fillcolor="rgba(46, 134, 193, 0.3)")

    # 그래프 출력
    st.plotly_chart(fig2, use_container_width=True)

    # 그래프 설명 문구 자리
    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 전체 총 관객수가 얼마나 빠르게 누적되고 완만해지는지 전체적인 성과 규모를 파악할 수 있습니다."
    )
