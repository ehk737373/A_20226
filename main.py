import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
# 전체 영화 목록을 누적관객수 내림차순으로 정렬
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에서 개별 분석할 영화 선택
st.sidebar.header("🔍 검색 설정")
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요 (누적관객수 순)", movie_order
)

# 선택한 개별 영화 데이터 필터링
filtered_df = df[df["영화명"] == selected_movie]


# ---------------------------------------------------------
# [개별 영화 분석 구역]
# ---------------------------------------------------------
st.header(f"📊 '{selected_movie}' 데이터 시각화")

# 구역 1: 해당일관객수 추이 선그래프
with st.container():
    st.subheader("1. 일별 관객수 변화 추이")

    fig1 = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"'{selected_movie}'의 일별 관객수 변화",
        labels={"기준일자": "날짜", "해당일관객수": "해당일 관객수(명)"},
        markers=True,  # 데이터 포인트에 점 표시
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 개봉 이후 날짜가 경과함에 따라 해당일 관객수가 어떻게 변화하고 증가/감소하는지 흐름을 파악할 수 있습니다."
    )

st.divider()

# 구역 2: 누적관객수 영역 차트 (Area Chart)
with st.container():
    st.subheader("2. 누적 관객수 증가 추이")

    fig2 = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"'{selected_movie}'의 누적 관객수 변화",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
    )

    fig2.update_traces(line_color="#2E86C1", fillcolor="rgba(46, 134, 193, 0.3)")

    st.plotly_chart(fig2, use_container_width=True)

    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 전체 총 관객수가 얼마나 빠르게 누적되고 완만해지는지 전체적인 성과 규모를 파악할 수 있습니다."
    )

st.divider()


# ---------------------------------------------------------
# [전체 비교 분석 구역]
# ---------------------------------------------------------
st.header("🏆 박스오피스 전체 트렌드 비교 분석")

# 구역 3: 장기 흥행(20일 이상 TOP10 차트인) 상위 5개 영화 다중 선그래프
with st.container():
    st.subheader("3. TOP10 차트인 20일 이상 영화 중 누적관객수 TOP 5 비교")

    # 1. 영화별 등장 일수 계산
    movie_counts = df["영화명"].value_counts()

    # 2. 등장 일수가 20일 이상인 영화 목록 필터링
    movies_over_20days = movie_counts[movie_counts >= 20].index.tolist()

    # 3. 조건에 맞는 영화 중 누적관객수 상위 5개 선택
    top5_long_run_movies = (
        df[df["영화명"].isin(movies_over_20days)]
        .groupby("영화명")["누적관객수"]
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    # 4. 상위 5개 영화 데이터 추출
    top5_df = df[df["영화명"].isin(top5_long_run_movies)]

    # 5. Plotly 다중 선그래프 생성
    fig3 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="20일 이상 TOP10을 유지한 대표 흥행작 5편의 누적관객수 추이",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)", "영화명": "영화 제목"},
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 최소 20일 이상 순위권을 유지하며 장기 흥행에 성공한 상위 5개 영화들의 최종 흥행 규모와 관객 모객 페이스를 비교할 수 있습니다."
    )

st.divider()

# 구역 4: 전체 박스오피스 총 관객수 및 7일 이동평균선
with st.container():
    st.subheader("4. 전체 박스오피스 관객수 추이 및 7일 이동평균선")

    # 1. 기준일자별 전체 TOP10 영화의 해당일관객수 합계 계산
    daily_total = (
        df.groupby("기준일자")["해당일관객수"].sum().reset_index()
    )

    # 2. 7일 이동평균(Rolling Mean) 컬럼 생성
    daily_total["7일_이동평균"] = daily_total["해당일관객수"].rolling(window=7).mean()

    # 3. Plotly graph_objects를 사용하여 두 개의 선을 하나의 그래프에 중첩 표현
    fig4 = go.Figure()

    # (1) 원본 데이터 선: 연한 색상, 얇은 두께로 지정하여 요일별 변동 폭을 시각화
    fig4.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일별 총 관객수 (일일)",
            line=dict(color="rgba(180, 180, 180, 0.5)", width=1.5),
        )
    )

    # (2) 7일 이동평균 선: 진한 색상, 두꺼운 선으로 지정하여 추세를 강조
    fig4.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#E74C3C", width=3),
        )
    )

    # 레이아웃 및 축 설정
    fig4.update_layout(
        title="전체 박스오피스 총 관객수 변화 (일일 변동 vs 7일 이동평균)",
        xaxis_title="날짜",
        yaxis_title="총 관객수(명)",
        hovermode="x unified",
    )

    # 그래프 출력
    st.plotly_chart(fig4, use_container_width=True)

    # 그래프 설명 문구 자리
    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 주말과 평일 간의 극심한 일별 관객수 변동(연한 선)을 노이즈 없이 다듬어, 전체 영화 시장의 시즌별 성수기/비수기 관객 흐름 추세(진한 빨간 선)를 명확히 파악할 수 있습니다."
    )
