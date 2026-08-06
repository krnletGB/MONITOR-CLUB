import pandas as pd
import plotly.graph_objects as go

# =========================================================
# GRÁFICAS (AQUI PONGAN TODO LO DE GRAFICAS)
# =========================================================
COLORES_CLUSTER = [
    "#f02783",
    "#7c4ce4",
    "#4eb15c",
    "#ff821c",
    "#4c7dea",
    "#b7bbc3",
    "#26b9c4",
]


def grafica_dona_cluster(
    df: pd.DataFrame,
) -> go.Figure:
    if df.empty:
        return go.Figure()

    columna_cluster = (
        "nombre_cluster"
        if "nombre_cluster" in df.columns
        else "subcluster_ia"
    )

    total = float(df["venta_actual"].sum())

    figura = go.Figure(
        go.Pie(
            labels=df[columna_cluster].fillna("Sin cluster"),
            values=df["venta_actual"],
            hole=0.58,
            sort=False,
            marker={
                "colors": COLORES_CLUSTER[: len(df)],
                "line": {
                    "color": "white",
                    "width": 2,
                },
            },
            textinfo="percent",
            textfont={
                "size": 12,
                "color": "white",
            },
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Venta: $%{value:,.0f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),
        )
    )

    if total >= 1_000_000:
        texto_total = f"${total / 1_000_000:,.1f} M"
    else:
        texto_total = f"${total:,.0f}"

    figura.add_annotation(
        x=0.5,
        y=0.5,
        text=(
            "<span style='font-size:12px;color:#7b8495'>"
            "Total"
            "</span>"
            f"<br><b>{texto_total}</b>"
        ),
        showarrow=False,
        align="center",
        font={
            "size": 16,
            "color": "#102342",
        },
    )

    figura.update_layout(
        height=340,
        margin={
            "l": 5,
            "r": 5,
            "t": 10,
            "b": 5,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )

    return figura


def grafica_top_sucursales(
    df: pd.DataFrame,
    top: int = 10,
) -> go.Figure:
    if df.empty:
        return go.Figure()

    datos = (
        df.nlargest(top, "venta_actual")
        .sort_values("venta_actual", ascending=True)
        .copy()
    )

    figura = go.Figure(
        go.Bar(
            x=datos["venta_actual"],
            y=datos["sucursal"],
            orientation="h",
            marker={
                "color": "#f02783",
                "line": {
                    "color": "#f02783",
                    "width": 0,
                },
            },
            text=datos["venta_actual"],
            texttemplate="$%{text:,.0f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Venta: $%{x:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    figura.update_layout(
        height=395,
        margin={
            "l": 10,
            "r": 85,
            "t": 10,
            "b": 15,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis={
            "visible": False,
            "showgrid": False,
        },
        yaxis={
            "title": "",
            "tickfont": {
                "size": 11,
                "color": "#283953",
            },
        },
    )

    return figura