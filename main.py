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

    # (1) 원본 데이터 선
    fig4.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일별 총 관객수 (일일)",
            line=dict(color="rgba(180, 180, 180, 0.5)", width=1.5),
        )
    )

    # (2) 7일 이동평균 선
    fig4.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#E74C3C", width=3),
        )
    )

    fig4.update_layout(
        title="전체 박스오피스 총 관객수 변화 (일일 변동 vs 7일 이동평균)",
        xaxis_title="날짜",
        yaxis_title="총 관객수(명)",
        hovermode="x unified",
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 주말과 평일 간의 극심한 일별 관객수 변동(연한 선)을 노이즈 없이 다듬어, 전체 영화 시장의 시즌별 성수기/비수기 관객 흐름 추세(진한 빨간 선)를 명확히 파악할 수 있습니다."
    )

st.divider()

# 구역 5: 월별 전체 관객수 합계 막대그래프
with st.container():
    st.subheader("5. 월별 전체 관객수 합계")

    # 1. '기준일자'에서 '연-월(YYYY-MM)' 형태의 문자열 추출하여 컬럼 생성
    daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

    # 2. 연-월 단위로 그룹화하여 일별 관객수 합계를 월 단위로 재합산
    monthly_total = (
        daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
    )

    # 3. Plotly 막대그래프(Bar Chart) 생성
    fig5 = px.bar(
        monthly_total,
        x="연월",
        y="해당일관객수",
        title="월별 극장가 총 관객수 집계",
        labels={"연월": "년-월", "해당일관객수": "월 총 관객수(명)"},
        text_auto=".2s",
    )

    fig5.update_traces(
        marker_color="#3498DB",
        textposition="outside",
    )

    fig5.update_layout(xaxis_type="category")

    st.plotly_chart(fig5, use_container_width=True)

    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 월 단위 총 관객수를 비교하여 연중 어떤 달(여름 방학/추석/겨울 방학 등)이 극장가의 가장 큰 성수기인지 한눈에 파악할 수 있습니다."
    )

st.divider()

# 구역 6: 캘린더 히트맵 (월 x 요일 관객수 집계) - px.imshow 활용으로 오류 해결
with st.container():
    st.subheader("6. 월별/요일별 캘린더 관객수 히트맵")

    # 1. 데이터에 월, 요일, 날짜 문자열 컬럼 추가
    daily_heatmap = daily_total.copy()
    daily_heatmap["월"] = daily_heatmap["기준일자"].dt.strftime("%Y-%m")

    # 요일 영문 -> 한글 매핑 및 순서 지정
    day_names = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    day_map = {
        "Monday": "월요일", "Tuesday": "화요일", "Wednesday": "수요일",
        "Thursday": "목요일", "Friday": "금요일", "Saturday": "토요일", "Sunday": "일요일"
    }
    daily_heatmap["요일"] = daily_heatmap["기준일자"].dt.day_name().map(day_map)
    daily_heatmap["날짜문자열"] = daily_heatmap["기준일자"].dt.strftime("%Y-%m-%d")

    # 2. 관객수 집계 피벗 테이블 생성
    heatmap_pivot = daily_heatmap.pivot_table(
        index="요일", 
        columns="월", 
        values="해당일관객수", 
        aggfunc="sum"
    ).reindex(day_names)

    # 3. 호버 표기용 날짜 피벗 테이블 생성
    date_pivot = daily_heatmap.pivot_table(
        index="요일", 
        columns="월", 
        values="날짜문자열", 
        aggfunc=lambda x: ", ".join(x)
    ).reindex(day_names)

    # 4. px.imshow 함수를 사용하여 안정적인 히트맵 생성
    fig6 = px.imshow(
        heatmap_pivot,
        labels=dict(x="연-월", y="요일", color="총 관객수(명)"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="YlOrRd",
        aspect="auto"
    )

    # 호버 템플릿 커스텀 적용 (날짜 문자열 표시)
    fig6.update_traces(
        customdata=date_pivot.values,
        hovertemplate=(
            "<b>날짜:</b> %{customdata}<br>" +
            "<b>연-월:</b> %{x}<br>" +
            "<b>요일:</b> %{y}<br>" +
            "<b>총 관객수:</b> %{z:,.0f}명<extra></extra>"
        )
    )

    fig6.update_layout(
        title="월별/요일별 박스오피스 관객수 분포 (진할수록 관객 많음)",
    )

    st.plotly_chart(fig6, use_container_width=True)

    # 그래프 설명 문구 자리
    st.caption(
        "💡 **이 그래프로 알 수 있는 것:** 각 월별로 특정 요일(예: 주말/공휴일)에 관객이 얼마나 집중되는지 패턴을 한눈에 확인할 수 있으며, 마우스를 올려 해당 날짜(yyyy-mm-dd)와 상세 관객 수를 직접 확인할 수 있습니다."
    )
