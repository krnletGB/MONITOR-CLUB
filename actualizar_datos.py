from pathlib import Path
import pandas as pd
from sqlalchemy import text
from src.conexion import obtener_engine
from src.consultas import (
    CONSULTA_CLIENTES_APP,
    CONSULTA_DETALLE_CLUB,
    CONSULTA_VENTA_CLUB,
)


CARPETA_DATA = Path("data")

RUTA_DETALLE_CLUB = CARPETA_DATA / "detalle_club.pkl"
RUTA_VENTA_CLUB = CARPETA_DATA / "venta_club.pkl"
RUTA_CLIENTES_APP = CARPETA_DATA / "clientes_app.pkl"
# =========================================================
# PKLS, REVISAR SI ES ACCIONABLE O NO 
# =========================================================

def guardar_pkl(
    df: pd.DataFrame,
    ruta: Path,
) -> None:
    ruta.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_pickle(ruta)

    print(
        f"Guardado: {ruta} | "
        f"{len(df):,} registros"
    )


def actualizar_detalle_club() -> None:
    engine = obtener_engine()

    print("Consultando detalle Club...")

    with engine.connect() as conexion:
        df = pd.read_sql(
            text(CONSULTA_DETALLE_CLUB),
            conexion,
        )

    columnas_fecha = [
        "Fecha_Compra",
        "Fecha_Vencimiento",
        "Fecha_Alta",
        "Fecha_Ult_Modif",
        "FechaAceptacionApp",
    ]

    for columna in columnas_fecha:
        if columna in df.columns:
            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce",
            )

    guardar_pkl(
        df,
        RUTA_DETALLE_CLUB,
    )


def actualizar_venta_club() -> None:
    engine = obtener_engine()

    print("Consultando venta Club...")

    with engine.connect() as conexion:
        df = pd.read_sql(
            text(CONSULTA_VENTA_CLUB),
            conexion,
        )

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(
            df["Fecha"],
            errors="coerce",
        )

    if "Venta_Neta" in df.columns:
        df["Venta_Neta"] = pd.to_numeric(
            df["Venta_Neta"],
            errors="coerce",
        ).fillna(0)

    guardar_pkl(
        df,
        RUTA_VENTA_CLUB,
    )


def actualizar_clientes_app() -> None:
    engine = obtener_engine()

    print("Consultando clientes App...")

    with engine.connect() as conexion:
        df = pd.read_sql(
            text(CONSULTA_CLIENTES_APP),
            conexion,
        )

    if "Fecha_Vencimiento" in df.columns:
        df["Fecha_Vencimiento"] = pd.to_datetime(
            df["Fecha_Vencimiento"],
            errors="coerce",
        )

    guardar_pkl(
        df,
        RUTA_CLIENTES_APP,
    )


def main() -> None:
    CARPETA_DATA.mkdir(
        parents=True,
        exist_ok=True,
    )

    #actualizar_detalle_club()
    actualizar_venta_club()
    actualizar_clientes_app()

    print("Actualización terminada.")


if __name__ == "__main__":
    main()