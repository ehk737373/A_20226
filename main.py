import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre 열 전처리: 세로막대 기호(|)로 분리하여 첫 번째 장르만 추출
    df['genre'] = df['genre'].fillna('').astype(str).apply(lambda x: x.split('|')[0] if x else '기타')
    return df

df = load_data()

# --- 첫 번째 그래프 구역 ---
st.header("1. 장르별 영화 편수 분포")

# 장르별 영화 편수 집계
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화 편수']

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    names='장르',
    values='영화 편수',
    hole=0.4,
    title="장르별 영화 편수 비율"
)

# 마우스오버 시 편수와 비율이 함께 표시되도록 설정
fig1.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

# 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# 구분선 및 알 수 있는 것 섹션
st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("박스오피스 상위권 영화 중 특정 장르가 차지하는 비중과 주요 인기 장르의 분포를 한눈에 파악할 수 있습니다.")

st.write("\n\n")

# --- 두 번째 그래프 구역 ---
st.header("2. 장르 및 영화별 총 관객수 트리맵")

# Plotly 트리맵 생성 (계층 구조: 장르 -> 영화명, 칸 크기: total_audi)
fig2 = px.treemap(
    df,
    path=[px.Constant("전체"), 'genre', 'movieNm'],
    values='total_audi',
    color='genre',
    title="장르 및 영화별 총 관객수 분포 (칸 크기: 총 관객수)"
)

# 마우스오버 시 영화명(라벨)과 총 관객수가 표시되도록 설정
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
)

# 그래프 출력
st.plotly_chart(fig2, use_container_width=True)

# 구분선 및 알 수 있는 것 섹션
st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("장르별 흥행 규모와 함께 각 장르 내부에서 어떤 영화가 흥행을 주도했는지 관객수 크기를 통해 직관적으로 비교할 수 있습니다.")

st.write("\n\n")

# --- 세 번째 그래프 구역 ---
st.header("3. 총 관객수 분포 히스토그램")

# Plotly 히스토그램 생성
fig3 = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    title="총 관객수 분포",
    labels={'total_audi': '총 관객수(명)'}
)

fig3.update_layout(
    yaxis_title="영화 수(편)",
    bargap=0.1
)

fig3.update_traces(
    hovertemplate="<b>관객수 구간</b>: %{x:,}명대<br><b>영화 수</b>: %{y}편<extra></extra>"
)

# 그래프 출력
st.plotly_chart(fig3, use_container_width=True)

# 데이터에서 최다 관객 영화 정보 추출
top_movie = df.loc[df['total_audi'].idxmax()]
max_movie_name = top_movie['movieNm']
max_movie_audi = top_movie['total_audi']

# 구분선 및 알 수 있는 것 섹션
st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write(
    f"대부분의 영화가 총 관객수 100만~300만 명 이하의 하위 구간에 밀집되어 있는 치우친 분포를 보이며, "
    f"가장 관객 수가 많은 영화는 **{max_movie_name}** ({max_movie_audi:,}명)입니다."
)    
