import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Albion Market Dashboard", layout="wide")

sns.set_theme(style="whitegrid")

# -----------------------------
# CONFIG
# -----------------------------
BASE_ITEMS = [

    # ORE
    "T2_ORE","T3_ORE","T4_ORE","T5_ORE","T6_ORE","T7_ORE","T8_ORE",

    # WOOD
    "T2_WOOD","T3_WOOD","T4_WOOD","T5_WOOD","T6_WOOD","T7_WOOD","T8_WOOD",

    # STONE
    "T2_ROCK","T3_ROCK","T4_ROCK","T5_ROCK","T6_ROCK","T7_ROCK","T8_ROCK"
]

CIUDADES = [
    "Brecilien",
    "Bridgewatch",
    "Caerleon",
    "Fort Sterling",
    "Lymhurst",
    "Martlock",
    "Thetford"
]

# -----------------------------
# FUNCIONES DE DATOS
# -----------------------------
@st.cache_data(ttl=300)
def obtener_precios(items):
    url = f"https://europe.albion-online-data.com/api/v2/stats/prices/{','.join(items)}.json"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)

    if not df.empty and "quality" in df.columns:
        df = df[df["quality"] == 1]

    return df


@st.cache_data(ttl=600)
def obtener_historico(items):
    url = f"https://europe.albion-online-data.com/api/v2/stats/history/{','.join(items)}.json?time-scale=24"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data)


def max_min_item(df_item):
    compras_validas = df_item.loc[df_item["buy_price_max"] != 0, "buy_price_max"]

    if not compras_validas.empty:
        min_compra = compras_validas.min()
        max_venta = df_item["sell_price_max"].max()
    else:
        min_compra = 0
        max_venta = 0

    return min_compra, max_venta


def construir_items_plot(base_item):
    return [
        base_item,
        f"{base_item}_LEVEL1@1",
        f"{base_item}_LEVEL2@2",
        f"{base_item}_LEVEL3@3"
    ]


# -----------------------------
# GRÁFICA 1: COMPARATIVA 2x2
# -----------------------------
def grafica_comparativa_encantamientos(df, base_item):
    items_plot = construir_items_plot(base_item)

    fig, ax = plt.subplots(2, 2, figsize=(12, 10))
    color_sell = "#2ecc71"
    color_buy = "#e74c3c"
    beneficio_t = []

    for i, item in enumerate(items_plot):
        fila = i // 2
        columna = i % 2

        df_item = df[df["item_id"] == item].copy()
        df_item = df_item[df_item["city"].isin(CIUDADES)]

        if df_item.empty:
            ax[fila, columna].text(
                0.5, 0.5,
                f"Sin datos para {item}",
                ha="center", va="center"
            )
            ax[fila, columna].set_title(item)
            ax[fila, columna].axis("off")
            continue

        ax[fila, columna].scatter(
            df_item["city"],
            df_item["sell_price_max"],
            color=color_sell,
            s=100,
            alpha=0.9,
            edgecolor="black",
            label="Venta max"
        )

        ax[fila, columna].scatter(
            df_item["city"],
            df_item["buy_price_max"],
            color=color_buy,
            s=100,
            alpha=0.9,
            edgecolor="black",
            label="Compra max"
        )

        min_compra, max_venta = max_min_item(df_item)

        if min_compra > 0 and max_venta > 0:
            multiplicador = round(max_venta / min_compra, 2)
            beneficio_abs = max_venta - min_compra

            ax[fila, columna].axhspan(
                min_compra,
                max_venta,
                color="#27ae60",
                alpha=0.15,
                label=f"Beneficio x{multiplicador}\nBeneficio: {beneficio_abs}"
            )
            ax[fila, columna].axhline(min_compra, linestyle="--", color=color_buy, alpha=0.6)
            ax[fila, columna].axhline(max_venta, linestyle="--", color=color_sell, alpha=0.6)
            beneficio_t.append(multiplicador)

        ax[fila, columna].set_title(item)
        ax[fila, columna].set_xlabel("Ciudad")
        ax[fila, columna].set_ylabel("Precio")
        ax[fila, columna].tick_params(axis="x", rotation=30)
        ax[fila, columna].grid(True, linestyle="--", alpha=0.35)
        ax[fila, columna].legend(fontsize=8)

    if beneficio_t:
        titulo = f"Mercado de {base_item}\nBeneficio medio x{round(sum(beneficio_t)/len(beneficio_t), 2)}"
    else:
        titulo = f"Mercado de {base_item}"

    plt.suptitle(titulo, fontsize=16, weight="bold")
    plt.tight_layout()

    return fig


# -----------------------------
# GRÁFICA 2: HISTÓRICO POR CIUDADES
# -----------------------------
def grafica_historico_ciudades(df_h, item_hist):
    fig, ax = plt.subplots(figsize=(18, 8))

    df_ore = df_h[df_h["item_id"] == item_hist].copy()

    if df_ore.empty:
        ax.text(0.5, 0.5, "No hay histórico disponible para ese item", ha="center", va="center")
        ax.axis("off")
        return fig

    ciudades_disponibles = {}
    for idx, row in df_ore.iterrows():
        if row["location"] in CIUDADES:
            ciudades_disponibles[row["location"]] = idx

    if not ciudades_disponibles:
        ax.text(0.5, 0.5, "No hay datos históricos de ciudades válidas", ha="center", va="center")
        ax.axis("off")
        return fig

    for city in CIUDADES:
        if city not in ciudades_disponibles:
            continue

        i = ciudades_disponibles[city]
        df_city = pd.DataFrame(df_ore.loc[i, "data"])

        if df_city.empty:
            continue

        fechas_raw = list(df_city["timestamp"])
        fechas_f = [f[:10] for f in fechas_raw]

        ax.plot(
            fechas_f,
            df_city["avg_price"],
            marker="o",
            lw=3,
            markersize=6,
            label=city
        )

        for k in range(0, len(fechas_f), 3):
            ax.text(
                x=fechas_f[k],
                y=df_city["avg_price"].iloc[k] + 1,
                s=str(df_city["avg_price"].iloc[k]),
                ha="center",
                fontsize=9
            )

    ax.grid(alpha=0.3)
    ax.tick_params(axis="x", rotation=45)
    ax.set_title(f"Evolución del precio medio - {item_hist}", fontsize=16)
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Precio medio")
    ax.legend()
    plt.tight_layout()

    return fig


# -----------------------------
# INTERFAZ
# -----------------------------
st.title("Dashboard de mercado de Albion Online")

modo = st.sidebar.selectbox(
    "Qué quieres ver",
    [
        "Comparativa de encantamientos",
        "Histórico por ciudades"
    ]
)

base_item = st.sidebar.selectbox(
    "Recurso base",
    BASE_ITEMS,
    index=3
)

actualizar = st.sidebar.selectbox(
    "Actualizar cada",
    ["1m", "5m", "10m", "30m"],
    index=1
)

if modo == "Comparativa de encantamientos":
    st.subheader("Comparativa actual de precios por ciudades")
    items_plot = construir_items_plot(base_item)

    @st.fragment(run_every=actualizar)
    def actualizar_comparativa():
        df = obtener_precios(items_plot)
        fig = grafica_comparativa_encantamientos(df, base_item)
        st.pyplot(fig)

    actualizar_comparativa()

else:
    st.subheader("Histórico de precio medio por ciudades")

    item_hist = st.sidebar.selectbox(
        "Item histórico",
        construir_items_plot(base_item),
        index=1
    )

    @st.fragment(run_every=actualizar)
    def actualizar_historico():
        df_h = obtener_historico([item_hist])
        fig = grafica_historico_ciudades(df_h, item_hist)
        st.pyplot(fig)

    actualizar_historico()

