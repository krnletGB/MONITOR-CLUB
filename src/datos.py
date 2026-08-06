from datetime import date
from pathlib import Path
import pandas as pd
import streamlit as st


CARPETA_DATA = Path("data")

RUTA_DETALLE_CLUB = CARPETA_DATA / "detalle_club.pkl"
RUTA_VENTA_CLUB = CARPETA_DATA / "venta_club.pkl"
RUTA_CLIENTES_APP = CARPETA_DATA / "clientes_app.pkl"


def validar_archivo(
    ruta: Path,
) -> None:
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe el archivo {ruta}. "
            "Ejecuta primero: python actualizar_datos.py"
        )


@st.cache_data(show_spinner=False)
def cargar_detalle_club_completo() -> pd.DataFrame:
    validar_archivo(RUTA_DETALLE_CLUB)

    return pd.read_pickle(
        RUTA_DETALLE_CLUB
    )


@st.cache_data(show_spinner=False)
def cargar_venta_club_completa() -> pd.DataFrame:
    validar_archivo(RUTA_VENTA_CLUB)

    return pd.read_pickle(
        RUTA_VENTA_CLUB
    )


@st.cache_data(show_spinner=False)
def cargar_clientes_app() -> pd.DataFrame:
    validar_archivo(RUTA_CLIENTES_APP)

    return pd.read_pickle(
        RUTA_CLIENTES_APP
    )


def cargar_detalle_club(
    fecha_inicio: date,
    fecha_fin: date,
) -> pd.DataFrame:
    df = cargar_detalle_club_completo()

    if df.empty:
        return df.copy()

    fecha_inicio_ts = pd.Timestamp(
        fecha_inicio
    )

    fecha_fin_ts = pd.Timestamp(
        fecha_fin
    )

    mascara = (
        df["Fecha_Compra"].ge(fecha_inicio_ts)
        & df["Fecha_Compra"].le(fecha_fin_ts)
    )

    return df.loc[mascara].copy()


def cargar_venta_club(
    fecha_inicio: date,
    fecha_fin: date,
) -> pd.DataFrame:
    df = cargar_venta_club_completa()

    if df.empty:
        return df.copy()

    fecha_inicio_ts = pd.Timestamp(
        fecha_inicio
    )

    fecha_fin_ts = pd.Timestamp(
        fecha_fin
    )

    mascara = (
        df["Fecha"].ge(fecha_inicio_ts)
        & df["Fecha"].le(fecha_fin_ts)
    )

    return df.loc[mascara].copy()


def limpiar_cache() -> None:
    st.cache_data.clear()