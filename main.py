import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Shanghai Climate Observatory",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. MODERN CSS
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background: #f5f7fb;
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        .hero {
            padding: 1.5rem 1.7rem;
            border-radius: 22px;
            background:
                linear-gradient(135deg, rgba(255,255,255,.98), rgba(237,243,250,.96));
            border: 1px solid rgba(80,100,130,.12);
            box-shadow: 0 10px 35px rgba(40,60,90,.08);
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: 2.35rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin-bottom: .2rem;
        }

        .hero-subtitle {
            color: #596579;
            font-size: 1.03rem;
        }

        .section-title {
            font-size: 1.45rem;
            font-weight: 750;
            margin-top: 1.3rem;
            margin-bottom: .45rem;
        }

        .small-muted {
            color: #68758a;
            font-size: .9rem;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid rgba(80,100,130,.12);
            padding: .8rem;
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(40,60,90,.05);
        }

        .source-box {
            background: white;
            border-left: 5px solid #4c78a8;
            padding: .9rem 1rem;
            border-radius: 10px;
            color: #536174;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🌏 Shanghai Climate Observatory</div>
        <div class="hero-subtitle">
            Интерактивное исследование климата Шанхая и его динамики
            за 2000–2025 годы
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Shanghai • Climate • Temperature • Precipitation • Trends • Map"
)


# ============================================================
# 4. DATA SOURCE
# ============================================================

DATA_URL = (
    "https://data.meteostat.net/monthly/58362.csv.gz"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # Оставляем реальные поля месячного набора Meteostat
    needed = [
        "year",
        "month",
        "temp",
        "tmin",
        "tmax",
        "prcp"
    ]

    missing = [c for c in needed if c not in df.columns]

    if missing:
        raise ValueError(
            "В файле отсутствуют ожидаемые колонки: "
            + ", ".join(missing)
        )

    for c in needed:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df[
        (df["year"] >= 2000) &
        (df["year"] <= 2025)
    ].copy()

    df["date"] = pd.to_datetime(
        dict(
            year=df["year"].astype(int),
            month=df["month"].astype(int),
            day=1
        ),
        errors="coerce"
    )

    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)

    return df.sort_values("date")


try:
    df = load_data()
except Exception as e:
    st.error("Не удалось загрузить климатические данные.")
    st.code(str(e))
    st.stop()


if df.empty:
    st.error("Нет данных за 2000–2025 годы.")
    st.stop()


# ============================================================
# 5. SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("⚙️ Управление")

metric_choice = st.sidebar.selectbox(
    "Главный показатель",
    [
        "Средняя температура",
        "Средняя минимальная температура",
        "Средняя максимальная температура",
        "Осадки"
    ]
)

year_range = st.sidebar.slider(
    "Период анализа",
    min_value=2000,
    max_value=2025,
    value=(2000, 2025)
)

selected_years = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
].copy()

show_monthly = st.sidebar.checkbox(
    "Показывать месячный профиль",
    value=True
)

show_map = st.sidebar.checkbox(
    "Показывать карту",
    value=True
)


# ============================================================
# 6. ANNUAL AGGREGATION
# ============================================================

annual = (
    selected_years
    .groupby("year")
    .agg(
        avg_temp=("temp", "mean"),
        avg_tmin=("tmin", "mean"),
        avg_tmax=("tmax", "mean"),
        precipitation=("prcp", "sum")
    )
    .reset_index()
)

annual["temperature_range"] = (
    annual["avg_tmax"] - annual["avg_tmin"]
)


# ============================================================
# 7. KPI DASHBOARD
# ============================================================

latest_year = int(annual["year"].max())
first_year = int(annual["year"].min())

latest = annual.iloc[-1]

warming = np.nan
if len(annual) >= 2:
    warming = (
        annual.iloc[-1]["avg_temp"]
        - annual.iloc[0]["avg_temp"]
    )

trend_per_decade = np.nan
if len(annual) >= 2:
    x = annual["year"].to_numpy()
    y = annual["avg_temp"].to_numpy()

    slope = np.polyfit(x, y, 1)[0]
    trend_per_decade = slope * 10


st.markdown(
    '<div class="section-title">📊 Climate dashboard</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Средняя температура",
        f"{latest['avg_temp']:.1f} °C"
    )

with c2:
    st.metric(
        "Осадки",
        f"{latest['precipitation']:,.0f} mm"
    )

with c3:
    if pd.notna(trend_per_decade):
        st.metric(
            "Тренд температуры",
            f"{trend_per_decade:+.2f} °C / 10 лет"
        )
    else:
        st.metric("Тренд температуры", "—")

with c4:
    st.metric(
        "Амплитуда",
        f"{latest['temperature_range']:.1f} °C"
    )


st.caption(
    f"Текущий dashboard рассчитан для {latest_year} года "
    f"в выбранном диапазоне {first_year}–{latest_year}."
)


# ============================================================
# 8. GRAPH 1 — ANNUAL TEMPERATURE
# ============================================================

st.markdown(
    '<div class="section-title">🌡️ 1. Изменение средней температуры</div>',
    unsafe_allow_html=True
)

fig1 = px.line(
    annual,
    x="year",
    y="avg_temp",
    markers=True,
    labels={
        "year": "Год",
        "avg_temp": "Средняя температура, °C"
    },
    title="Среднегодовая температура в Шанхае"
)

fig1.update_traces(
    mode="lines+markers",
    hovertemplate=(
        "Год: %{x}<br>"
        "Средняя температура: %{y:.2f} °C"
        "<extra></extra>"
    )
)

fig1.update_layout(
    height=520,
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "На этом графике можно исследовать долгосрочный температурный тренд "
    "и сравнивать начало и конец выбранного периода."
)


# ============================================================
# 9. GRAPH 2 — MIN / MAX
# ============================================================

st.markdown(
    '<div class="section-title">📈 2. Минимальная и максимальная температура</div>',
    unsafe_allow_html=True
)

temp_long = annual.melt(
    id_vars="year",
    value_vars=["avg_tmin", "avg_temp", "avg_tmax"],
    var_name="type",
    value_name="temperature"
)

temp_long["type"] = temp_long["type"].map(
    {
        "avg_tmin": "Средняя минимальная",
        "avg_temp": "Средняя",
        "avg_tmax": "Средняя максимальная"
    }
)

fig2 = px.line(
    temp_long,
    x="year",
    y="temperature",
    color="type",
    markers=True,
    labels={
        "year": "Год",
        "temperature": "Температура, °C",
        "type": "Показатель"
    },
    title="Температурный диапазон по годам"
)

fig2.update_traces(
    mode="lines+markers",
    hovertemplate=(
        "%{fullData.name}<br>"
        "Год: %{x}<br>"
        "Температура: %{y:.2f} °C"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=540,
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# 10. GRAPH 3 — PRECIPITATION
# ============================================================

st.markdown(
    '<div class="section-title">🌧️ 3. Годовое количество осадков</div>',
    unsafe_allow_html=True
)

fig3 = px.bar(
    annual,
    x="year",
    y="precipitation",
    labels={
        "year": "Год",
        "precipitation": "Осадки, mm"
    },
    title="Годовые осадки в Шанхае"
)

fig3.update_traces(
    hovertemplate=(
        "Год: %{x}<br>"
        "Осадки: %{y:.0f} mm"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=500,
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig3, use_container_width=True)


# ============================================================
# 11. MONTHLY CLIMATE PROFILE
# ============================================================

if show_monthly:

    st.markdown(
        '<div class="section-title">🗓️ 4. Климатический профиль по месяцам</div>',
        unsafe_allow_html=True
    )

    monthly = (
        selected_years
        .groupby("month")
        .agg(
            temp=("temp", "mean"),
            tmin=("tmin", "mean"),
            tmax=("tmax", "mean"),
            prcp=("prcp", "mean")
        )
        .reset_index()
    )

    month_names = {
        1: "Янв",
        2: "Фев",
        3: "Мар",
        4: "Апр",
        5: "Май",
        6: "Июн",
        7: "Июл",
        8: "Авг",
        9: "Сен",
        10: "Окт",
        11: "Ноя",
        12: "Дек"
    }

    monthly["month_name"] = monthly["month"].map(month_names)

    tab1, tab2 = st.tabs(
        ["🌡️ Температура", "🌧️ Осадки"]
    )

    with tab1:

        mlong = monthly.melt(
            id_vars=["month", "month_name"],
            value_vars=["tmin", "temp", "tmax"],
            var_name="type",
            value_name="value"
        )

        mlong["type"] = mlong["type"].map(
            {
                "tmin": "Средняя минимальная",
                "temp": "Средняя",
                "tmax": "Средняя максимальная"
            }
        )

        fig4 = px.line(
            mlong,
            x="month_name",
            y="value",
            color="type",
            markers=True,
            category_orders={
                "month_name": list(month_names.values())
            },
            labels={
                "month_name": "Месяц",
                "value": "Температура, °C",
                "type": "Показатель"
            },
            title="Средний климатический профиль по месяцам"
        )

        fig4.update_layout(height=480)

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    with tab2:

        fig5 = px.bar(
            monthly,
            x="month_name",
            y="prcp",
            labels={
                "month_name": "Месяц",
                "prcp": "Средние месячные осадки, mm"
            },
            title="Средние месячные осадки"
        )

        fig5.update_layout(height=480)

        st.plotly_chart(
            fig5,
            use_container_width=True
        )


# ============================================================
# 12. CLIMATE EXTREMES / STATISTICS
# ============================================================

st.markdown(
    '<div class="section-title">🔎 5. Статистический анализ</div>',
    unsafe_allow_html=True
)

s1, s2, s3 = st.columns(3)

with s1:
    warmest_year = annual.loc[
        annual["avg_temp"].idxmax()
    ]

    st.metric(
        "Самый тёплый год",
        int(warmest_year["year"]),
        f"{warmest_year['avg_temp']:.2f} °C"
    )

with s2:
    wettest_year = annual.loc[
        annual["precipitation"].idxmax()
    ]

    st.metric(
        "Самый влажный год",
        int(wettest_year["year"]),
        f"{wettest_year['precipitation']:.0f} mm"
    )

with s3:
    coolest_year = annual.loc[
        annual["avg_temp"].idxmin()
    ]

    st.metric(
        "Самый прохладный год",
        int(coolest_year["year"]),
        f"{coolest_year['avg_temp']:.2f} °C"
    )


# ============================================================
# 13. MAP OF SHANGHAI + SURROUNDINGS
# ============================================================

if show_map:

    st.markdown(
        '<div class="section-title">🗺️ 6. Шанхай и окружающий регион</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Карта показывает положение Шанхая и крупных городов "
        "дельты Янцзы. Климатические наблюдения в этом проекте "
        "относятся к станции Shanghai / 58362."
    )

    cities = pd.DataFrame(
        {
            "city": [
                "Shanghai",
                "Suzhou",
                "Wuxi",
                "Nantong",
                "Jiaxing",
                "Hangzhou",
                "Ningbo"
            ],
            "lat": [
                31.2304,
                31.2989,
                31.4912,
                31.9807,
                30.7461,
                30.2741,
                29.8683
            ],
            "lon": [
                121.4737,
                120.5853,
                120.3119,
                120.8943,
                120.7555,
                120.1551,
                121.5440
            ],
            "role": [
                "Главный город / климатическая точка",
                "Окрестности",
                "Окрестности",
                "Окрестности",
                "Окрестности",
                "Окрестности",
                "Окрестности"
            ]
        }
    )

    fig_map = px.scatter_map(
        cities,
        lat="lat",
        lon="lon",
        hover_name="city",
        hover_data={
            "role": True,
            "lat": False,
            "lon": False
        },
        zoom=5.6,
        center={
            "lat": 31.0,
            "lon": 120.9
        },
        height=620,
        map_style="open-street-map",
        size_max=18,
        title="Shanghai and Yangtze River Delta"
    )

    fig_map.update_traces(
        marker=dict(size=13)
    )

    fig_map.update_layout(
        margin=dict(l=0, r=0, t=55, b=0)
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )


# ============================================================
# 14. SIMPLE TREND ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🧠 7. Автоматический вывод</div>',
    unsafe_allow_html=True
)

if pd.notna(warming):

    direction = "повысилась" if warming > 0 else "снизилась"

    st.write(
        f"За выбранный период средняя годовая температура "
        f"{direction} примерно на **{abs(warming):.2f} °C** "
        f"(сравнение первого и последнего года диапазона)."
    )

if pd.notna(trend_per_decade):

    st.write(
        f"Линейный температурный тренд составляет примерно "
        f"**{trend_per_decade:+.2f} °C за десятилетие**."
    )

st.write(
    "Важно: линейный тренд — это статистическая оценка, "
    "а не прогноз будущего климата."
)


# ============================================================
# 15. DATA TABLE
# ============================================================

st.markdown(
    '<div class="section-title">📋 8. Таблица данных</div>',
    unsafe_allow_html=True
)

with st.expander("Открыть годовые значения"):

    display_annual = annual.copy()

    display_annual.columns = [
        "Год",
        "Средняя температура °C",
        "Средняя минимальная °C",
        "Средняя максимальная °C",
        "Осадки mm",
        "Амплитуда °C"
    ]

    st.dataframe(
        display_annual,
        use_container_width=True,
        hide_index=True
    )


with st.expander("Открыть исходные месячные данные"):

    st.dataframe(
        selected_years,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 16. SOURCE
# ============================================================

st.markdown(
    """
    <div class="source-box">
        <b>Источник данных:</b> Meteostat monthly climate data<br>
        <b>Станция:</b> Shanghai / 58362<br>
        <b>Период:</b> 2000–2025<br>
        <b>Показатели:</b> температура, минимум, максимум, осадки
    </div>
    """,
    unsafe_allow_html=True
)

st.success(
    "🌏 Shanghai Climate Observatory готов."
)
