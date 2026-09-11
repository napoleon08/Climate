import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# 1. НАСТРОЙКА СТРАНИЦЫ
# ============================================================

st.set_page_config(
    page_title="Shanghai Climate 2000-2025",
    page_icon="🌏",
    layout="wide"
)

st.title("🌏 상하이 기후 데이터 그래프")
st.subheader("Shanghai Climate Change — 2000–2025")

st.write(
    "2000년부터 2025년까지 중국 상하이의 "
    "기온과 강수량 변화를 데이터로 분석합니다."
)


# ============================================================
# 2. ДАННЫЕ METEOSTAT
# ============================================================

DATA_URL = (
    "https://data.meteostat.net/monthly/58362.csv.gz"
)


@st.cache_data
def load_data():

    # Meteostat 월별 데이터를 불러옵니다.
    df = pd.read_csv(
        DATA_URL,
        compression="gzip"
    )

    # 날짜를 날짜 형식으로 변환합니다.
    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    # 필요한 숫자 데이터를 숫자형으로 변환합니다.
    number_columns = [
        "tavg",
        "tmin",
        "tmax",
        "prcp"
    ]

    for column in number_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# 3. ДАННЫЕ ЗАГРУЗКА
# ============================================================

try:

    df = load_data()

except Exception as e:

    st.error(
        "기후 데이터를 불러오지 못했습니다."
    )

    st.write(
        "인터넷 연결 또는 Meteostat 데이터 주소를 확인해 주세요."
    )

    st.stop()


# ============================================================
# 4. 2000–2025 ДАННЫЕ
# ============================================================

df = df[
    (df["time"].dt.year >= 2000) &
    (df["time"].dt.year <= 2025)
].copy()


# ============================================================
# 5. ГОДОВЫЕ ДАННЫЕ
# ============================================================

df["year"] = df["time"].dt.year


annual = (
    df.groupby("year")
    .agg(
        평균기온=("tavg", "mean"),
        평균최저기온=("tmin", "mean"),
        평균최고기온=("tmax", "mean"),
        강수량=("prcp", "sum")
    )
    .reset_index()
)


annual = annual.sort_values("year")


# ============================================================
# 6. ЗАГОЛОВОК
# ============================================================

st.divider()

st.header(
    "📈 그래프 1 — 상하이 평균기온 변화"
)

st.write(
    "2000년부터 2025년까지 상하이의 "
    "연평균 기온 변화를 보여줍니다."
)


# ============================================================
# 7. ГРАФИК СРЕДНЕЙ ТЕМПЕРАТУРЫ
# ============================================================

fig1 = px.line(
    annual,
    x="year",
    y="평균기온",
    markers=True,
    title="Shanghai Average Temperature — 2000–2025",
    labels={
        "year": "연도",
        "평균기온": "평균기온 (°C)"
    }
)


fig1.update_traces(
    mode="lines+markers",
    hovertemplate=(
        "연도: %{x}<br>"
        "평균기온: %{y:.2f} °C"
        "<extra></extra>"
    )
)


fig1.update_layout(
    height=600,
    xaxis=dict(
        title="연도",
        dtick=1
    ),
    yaxis=dict(
        title="평균기온 (°C)"
    )
)


st.plotly_chart(
    fig1,
    use_container_width=True
)


# ============================================================
# 8. ЧТО МОЖНО УЗНАТЬ
# ============================================================

st.subheader(
    "💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "직접 설명을 작성하세요.",
    placeholder=(
        "예: 2000년 이후 상하이의 평균기온은 "
        "장기적으로 상승하는 경향을 보인다."
    ),
    height=120
)


# ============================================================
# 9. ГРАФИК 2 — МИНИМАЛЬНАЯ И МАКСИМАЛЬНАЯ
# ============================================================

st.divider()

st.header(
    "🌡️ 그래프 2 — 최저기온과 최고기온 변화"
)

st.write(
    "연도별 평균 최저기온과 평균 최고기온을 비교합니다."
)


fig2 = px.line(
    annual,
    x="year",
    y=[
        "평균최저기온",
        "평균최고기온"
    ],
    markers=True,
    title="Shanghai Minimum and Maximum Temperature",
    labels={
        "year": "연도",
        "value": "기온 (°C)",
        "variable": "기온"
    }
)


fig2.update_traces(
    mode="lines+markers",
    hovertemplate=(
        "연도: %{x}<br>"
        "기온: %{y:.2f} °C"
        "<extra></extra>"
    )
)


fig2.update_layout(
    height=600,
    xaxis=dict(
        title="연도",
        dtick=1
    ),
    yaxis=dict(
        title="기온 (°C)"
    )
)


st.plotly_chart(
    fig2,
    use_container_width=True
)


# ============================================================
# 10. ГРАФИК 3 — ОСАДКИ
# ============================================================

st.divider()

st.header(
    "🌧️ 그래프 3 — 연간 강수량 변화"
)

st.write(
    "2000년부터 2025년까지 상하이의 "
    "연간 총 강수량 변화를 보여줍니다."
)


fig3 = px.line(
    annual,
    x="year",
    y="강수량",
    markers=True,
    title="Shanghai Annual Precipitation — 2000–2025",
    labels={
        "year": "연도",
        "강수량": "강수량 (mm)"
    }
)


fig3.update_traces(
    mode="lines+markers",
    hovertemplate=(
        "연도: %{x}<br>"
        "강수량: %{y:.1f} mm"
        "<extra></extra>"
    )
)


fig3.update_layout(
    height=600,
    xaxis=dict(
        title="연도",
        dtick=1
    ),
    yaxis=dict(
        title="강수량 (mm)"
    )
)


st.plotly_chart(
    fig3,
    use_container_width=True
)


# ============================================================
# 11. ОБЩИЙ АНАЛИЗ
# ============================================================

st.subheader(
    "💡 기후 변화에 대해 알 수 있는 것"
)

st.text_area(
    "직접 분석을 작성하세요.",
    placeholder=(
        "예: 상하이의 기온과 강수량이 "
        "2000년 이후 어떻게 변화했는지 설명하세요."
    ),
    height=150
)


# ============================================================
# 12. ОСНОВНЫЕ ПОКАЗАТЕЛИ
# ============================================================

st.divider()

st.header(
    "📊 주요 기후 지표"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "2000년 평균기온",
        f"{annual.iloc[0]['평균기온']:.2f} °C"
    )


with col2:

    st.metric(
        "2025년 평균기온",
        f"{annual.iloc[-1]['평균기온']:.2f} °C"
    )


with col3:

    temperature_change = (
        annual.iloc[-1]["평균기온"]
        - annual.iloc[0]["평균기온"]
    )

    st.metric(
        "2000→2025 변화",
        f"{temperature_change:+.2f} °C"
    )


with col4:

    max_year = annual.loc[
        annual["평균기온"].idxmax(),
        "year"
    ]

    st.metric(
        "가장 따뜻한 해",
        f"{int(max_year)}년"
    )


# ============================================================
# 13. ДАННЫЕ
# ============================================================

st.divider()

st.header(
    "📋 연도별 기후 데이터"
)


display_df = annual.copy()


display_df["평균기온"] = (
    display_df["평균기온"].round(2)
)

display_df["평균최저기온"] = (
    display_df["평균최저기온"].round(2)
)

display_df["평균최고기온"] = (
    display_df["평균최고기온"].round(2)
)

display_df["강수량"] = (
    display_df["강수량"].round(1)
)


st.dataframe(
    display_df,
    use_container_width=True
)


# ============================================================
# 14. ИНФОРМАЦИЯ ОБ ИСТОЧНИКЕ
# ============================================================

st.divider()

st.subheader(
    "📚 데이터 출처"
)

st.write(
    "Meteostat — Shanghai weather station 58362"
)

st.write(
    "분석 기간: 2000–2025"
)

st.write(
    "주요 변수: 평균기온, 최저기온, 최고기온, 강수량"
)


# ============================================================
# 15. КОНЕЦ
# ============================================================

st.success(
    "2000년부터 2025년까지 상하이 기후 데이터 분석이 완료되었습니다."
)
