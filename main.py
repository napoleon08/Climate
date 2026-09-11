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

st.subheader(
    "Shanghai Climate Change — 2000–2025"
)

st.write(
    "2000년부터 2025년까지 중국 상하이의 "
    "기온과 강수량 변화를 데이터로 분석합니다."
)


# ============================================================
# 2. METEOSTAT ДАННЫЕ
# ============================================================

DATA_URL = (
    "https://data.meteostat.net/monthly/58362.csv.gz"
)


@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        compression="gzip"
    )

    return df


# ============================================================
# 3. ЗАГРУЗКА
# ============================================================

try:

    df = load_data()

except Exception as e:

    st.error(
        "기후 데이터를 불러오지 못했습니다."
    )

    st.write(
        "Meteostat 데이터 연결에 문제가 발생했습니다."
    )

    st.code(str(e))

    st.stop()


# ============================================================
# 4. ПРОВЕРКА НУЖНЫХ КОЛОНОК
# ============================================================

required_columns = [
    "year",
    "month",
    "temp",
    "tmin",
    "tmax",
    "prcp"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "필요한 데이터 열을 찾을 수 없습니다."
    )

    st.write(
        "찾을 수 없는 열:",
        missing_columns
    )

    st.write(
        "현재 데이터 열:",
        list(df.columns)
    )

    st.stop()


# ============================================================
# 5. ПРЕОБРАЗОВАНИЕ ДАННЫХ
# ============================================================

df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce"
)

df["month"] = pd.to_numeric(
    df["month"],
    errors="coerce"
)


for column in [
    "temp",
    "tmin",
    "tmax",
    "prcp"
]:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 6. ОСТАВЛЯЕМ 2000–2025
# ============================================================

df = df[
    (df["year"] >= 2000) &
    (df["year"] <= 2025)
].copy()


if df.empty:

    st.error(
        "2000–2025년 데이터가 없습니다."
    )

    st.stop()


# ============================================================
# 7. ГОДОВОЙ АНАЛИЗ
# ============================================================

annual = (
    df.groupby("year")
    .agg(
        평균기온=("temp", "mean"),
        평균최저기온=("tmin", "mean"),
        평균최고기온=("tmax", "mean"),
        강수량=("prcp", "sum")
    )
    .reset_index()
)


annual = annual.sort_values(
    "year"
)


# ============================================================
# 8. ОСНОВНОЙ ГРАФИК — СРЕДНЯЯ ТЕМПЕРАТУРА
# ============================================================

st.divider()

st.header(
    "📈 그래프 1 — 상하이 평균기온 변화"
)

st.write(
    "2000년부터 2025년까지 상하이의 "
    "연평균 기온 변화를 보여줍니다."
)


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
        dtick=2
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
# 9. ОБЪЯСНЕНИЕ ГРАФИКА
# ============================================================

st.subheader(
    "💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "직접 설명을 작성하세요.",
    placeholder=(
        "예: 2000년부터 2025년까지 "
        "상하이의 평균기온은 장기적으로 "
        "상승 또는 하락하는 경향을 보인다."
    ),
    height=120
)


# ============================================================
# 10. ГРАФИК — МИНИМАЛЬНАЯ И МАКСИМАЛЬНАЯ
# ============================================================

st.divider()

st.header(
    "🌡️ 그래프 2 — 최저기온과 최고기온 변화"
)

st.write(
    "연도별 평균 최저기온과 평균 최고기온을 비교합니다."
)


temperature_long = annual.melt(
    id_vars="year",
    value_vars=[
        "평균최저기온",
        "평균최고기온"
    ],
    var_name="기온종류",
    value_name="기온"
)


fig2 = px.line(
    temperature_long,
    x="year",
    y="기온",
    color="기온종류",
    markers=True,
    title="Shanghai Minimum and Maximum Temperature",
    labels={
        "year": "연도",
        "기온": "기온 (°C)",
        "기온종류": "기온 종류"
    }
)


fig2.update_traces(
    mode="lines+markers"
)


fig2.update_layout(
    height=600,

    xaxis=dict(
        title="연도",
        dtick=2
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
# 11. ГРАФИК — ОСАДКИ
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
        dtick=2
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
# 12. ОБЩИЙ АНАЛИЗ
# ============================================================

st.subheader(
    "💡 기후 변화에 대해 알 수 있는 것"
)

st.text_area(
    "직접 분석을 작성하세요.",
    placeholder=(
        "예: 2000년부터 2025년까지 "
        "상하이의 기온과 강수량이 "
        "어떻게 변화했는지 설명하세요."
    ),
    height=150
)


# ============================================================
# 13. ОСНОВНЫЕ ПОКАЗАТЕЛИ
# ============================================================

st.divider()

st.header(
    "📊 주요 기후 지표"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    first_temp = annual.iloc[0]["평균기온"]

    st.metric(
        "2000년 평균기온",
        f"{first_temp:.2f} °C"
    )


with col2:

    last_temp = annual.iloc[-1]["평균기온"]

    st.metric(
        "2025년 평균기온",
        f"{last_temp:.2f} °C"
    )


with col3:

    temperature_change = (
        last_temp - first_temp
    )

    st.metric(
        "2000→2025 변화",
        f"{temperature_change:+.2f} °C"
    )


with col4:

    warmest_year = annual.loc[
        annual["평균기온"].idxmax(),
        "year"
    ]

    st.metric(
        "가장 따뜻한 해",
        f"{int(warmest_year)}년"
    )


# ============================================================
# 14. ТАБЛИЦА
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
# 15. ИСТОЧНИК
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
    "평균기온 / 최저기온 / 최고기온 / 강수량"
)


# ============================================================
# 16. ЗАВЕРШЕНИЕ
# ============================================================

st.success(
    "2000년부터 2025년까지 상하이 기후 데이터 분석 완료!"
)
