import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화 편수']

fig1 = px.pie(
    genre_counts,
    names='장르',
    values='영화 편수',
    hole=0.4,
    title="장르별 영화 편수 비율"
)

fig1.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("박스오피스 상위권 영화 중 특정 장르가 차지하는 비중과 주요 인기 장르의 분포를 한눈에 파악할 수 있습니다.")

st.write("\n\n")

# --- 두 번째 그래프 구역 ---
st.header("2. 장르 및 영화별 총 관객수 트리맵")

fig2 = px.treemap(
    df,
    path=[px.Constant("전체"), 'genre', 'movieNm'],
    values='total_audi',
    color='genre',
    title="장르 및 영화별 총 관객수 분포 (칸 크기: 총 관객수)"
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("장르별 흥행 규모와 함께 각 장르 내부에서 어떤 영화가 흥행을 주도했는지 관객수 크기를 통해 직관적으로 비교할 수 있습니다.")

st.write("\n\n")

# --- 세 번째 그래프 구역 ---
st.header("3. 총 관객수 분포 히스토그램")

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

st.plotly_chart(fig3, use_container_width=True)

top_movie = df.loc[df['total_audi'].idxmax()]
max_movie_name = top_movie['movieNm']
max_movie_audi = top_movie['total_audi']

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write(
    f"대부분의 영화가 총 관객수 100만~300만 명 이하의 하위 구간에 밀집되어 있는 치우친 분포를 보이며, "
    f"가장 관객 수가 많은 영화는 **{max_movie_name}** ({max_movie_audi:,}명)입니다."
)

st.write("\n\n")

# --- 네 번째 그래프 구역 ---
st.header("4. 개봉일 스크린수와 총 관객수의 관계")

fig4 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    title="개봉일 스크린수 vs 총 관객수 산점도",
    labels={
        'first_scrn': '개봉일 스크린수(개)',
        'total_audi': '총 관객수(명)',
        'genre': '장르'
    }
)

fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("개봉일 스크린수가 많을수록 대체로 총 관객수도 증가하는 양의 상관관계를 보이며, 초기 스크린 확보가 흥행의 주요 요소임을 알 수 있습니다.")

st.write("\n\n")

# --- 다섯 번째 그래프 구역 ---
st.header("5. 주요 장르별 총 관객수 박스플롯")

top_genres = df['genre'].value_counts()[lambda x: x >= 10].index
df_top_genres = df[df['genre'].isin(top_genres)]

fig5 = px.box(
    df_top_genres,
    x='genre',
    y='total_audi',
    color='genre',
    points="outliers",
    hover_name='movieNm',
    title="10편 이상 제작된 주요 장르별 총 관객수 분포 (박스플롯)",
    labels={
        'genre': '장르',
        'total_audi': '총 관객수(명)'
    }
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>장르: %{x}<br>총 관객수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("장르별 중간값과 관객수 변동 폭을 비교할 수 있으며, 박스 위쪽에 튀어나온 이상치 점들을 통해 특정 대히트 흥행작들의 위치를 확인할 수 있습니다.")

st.write("\n\n")

# --- 여섯 번째 그래프 구역 ---
st.header("6. 개봉일 스크린수, 첫 주 관객, 총 관객의 관계 (버블 그래프)")

fig6 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    size_max=40,
    color='genre',
    hover_name='movieNm',
    title="개봉일 스크린수 vs 총 관객수 vs 첫 주 관객수 (버블 크기: 첫 주 관객수)",
    labels={
        'first_scrn': '개봉일 스크린수(개)',
        'total_audi': '총 관객수(명)',
        'first_week_audi': '첫 주 관객수(명)',
        'genre': '장르'
    }
)

fig6.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<br>첫 주 관객수: %{marker.size:,}명<extra></extra>"
)

st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("초기 스크린 확보와 첫 주 흥행 실적이 최종 총 관객수와 밀접한 관계가 있음을 보여주며, 버블 크기를 통해 초기 흥행 폭발력을 직관적으로 파악할 수 있습니다.")

st.write("\n\n")

# --- 일곱 번째 그래프 구역 ---
st.header("7. 제작 국가 및 장르별 영화 편수 선버스트")

fig7 = px.sunburst(
    df,
    path=['nation', 'genre'],
    title="제작 국가별 장르 구성 분포 (선버스트)",
    color='nation'
)

fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percentRoot:.1%}<extra></extra>"
)

st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("각 제작 국가별 영화 편수의 비중과 국가별로 주력을 이루는 영화 장르의 세부 구성을 계층적으로 파악할 수 있습니다.")

st.write("\n\n")

# --- 여덟 번째 그래프 구역 ---
st.header("8. 영화들의 총 관람객 수")

# 1. 관객수 기준 오름차순 정렬 (아래에서 위로 오름차순 고정)
df_all_sorted = df.sort_values(by='total_audi', ascending=True).reset_index(drop=True)

max_audi = df_all_sorted['total_audi'].max()
min_audi = df_all_sorted['total_audi'].min()

# 2. 긴 제목 줄임 및 관객수 비율 기반 라벨 서식 생성
labels_formatted = []
for idx, row in df_all_sorted.iterrows():
    title = str(row['movieNm'])
    audi = row['total_audi']
    
    # 긴 제목 절반 수준 축소 (12자 초과 시 요약)
    if len(title) > 12:
        display_title = title[:10] + "..."
    else:
        display_title = title
        
    # 관객수 비율에 맞춘 폰트 크기 계산 (11px ~ 26px)
    ratio = (audi - min_audi) / (max_audi - min_audi) if max_audi != min_audi else 0.5
    font_size = int(11 + ratio * 15)
    
    # 상위 흥행작 굵게 처리
    if ratio >= 0.75:
        labels_formatted.append(f"<span style='font-size:{font_size}px; color:#000000;'><b>{display_title}</b></span>")
    else:
        labels_formatted.append(f"<span style='font-size:{font_size}px; color:#000000;'>{display_title}</span>")

# 3. 막대 그래프 생성 (하단 막대도 선명히 보이는 검은색 그라데이션)
fig8 = go.Figure(
    go.Bar(
        x=df_all_sorted['total_audi'],
        y=list(range(len(df_all_sorted))),
        orientation='h',
        marker=dict(
            color=df_all_sorted['total_audi'],
            colorscale=[[0, 'rgb(160,160,160)'], [1, 'rgb(0,0,0)']], # 적은 관객수 막대도 선명한 회색 처리
            showscale=False
        ),
        customdata=df_all_sorted['movieNm'],
        hovertemplate="<b>영화명</b>: %{customdata}<br><b>관람객 수</b>: %{x:,}명<extra></extra>"
    )
)

# 4. 레이아웃: 충분한 Y축 높이(4000px)와 좌측 여백(280px)으로 겹침/짤림 방지
fig8.update_layout(
    title="영화들의 총 관람객 수",
    height=4000,
    xaxis=dict(
        title="총 관객수(명)",
        type="log"
    ),
    yaxis=dict(
        tickmode='array',
        tickvals=list(range(len(df_all_sorted))),
        ticktext=labels_formatted,
        automargin=True
    ),
    margin=dict(l=280, r=20, t=50, b=40)
)

# 5. 500px 고정 스크롤 박스 내 배치
with st.container(height=500):
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("관객수가 적은 아래쪽 막대도 선명하게 잘 나타나며, 관객수가 많은 상위 흥행작은 큰 글씨와 볼드체로 강조되면서도 겹침 없이 순서대로 정렬됩니다.")
