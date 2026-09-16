# --- 여덟 번째 그래프 구역 ---
st.header("8. 영화들의 총 관람객 수")

# 216개 전체 영화를 관객수 기준 오름차순 정렬
df_all_sorted = df.sort_values(by='total_audi', ascending=True)

# 가로 막대 그래프 생성
fig8 = px.bar(
    df_all_sorted,
    x='total_audi',
    y='movieNm',
    orientation='h',
    title="영화들의 총 관람객 수",
    labels={
        'movieNm': '영화명',
        'total_audi': '총 관객수(명)'
    },
    color='total_audi',
    color_continuous_scale='Blues'
)

fig8.update_traces(
    hovertemplate="<b>영화명</b>: %{y}<br><b>관람객 수</b>: %{x:,}명<extra></extra>"
)

# 내부 스크롤이 가능하도록 높이와 레이아웃 설정
fig8.update_layout(
    height=3500,  # 내부 전체 높이
    coloraxis_showscale=False,
    yaxis=dict(dtick=1),
    margin=dict(l=10, r=10, t=40, b=10)
)

# st.container를 사용해 높이를 500px로 고정하고 내부 스크롤(scroll) 생성
with st.container(height=500):
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.write("스크롤 상자 내부에서 216편 전체 영화의 관람객 수를 겹침 없이 명확하게 파악할 수 있으며, 전체 페이지 길이 부담 없이 직관적으로 비교할 수 있습니다.")
