import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL

# =========================================================
# ESTO A PUNTA A ARCHIVO SECRETS.TOML (DATOS DE BD) -borren eeste comen cuando terminen
# =========================================================
@st.cache_resource
def obtener_engine() -> Engine:
    """
    Crea la conexión reutilizable a SQL Server.
    """

    servidor = st.secrets.get(
        "DB_SERVER",
        os.getenv("DB_SERVER", ""),
    )

    base_datos = st.secrets.get(
        "DB_DATABASE",
        os.getenv("DB_DATABASE", ""),
    )

    usuario = st.secrets.get(
        "DB_USER",
        os.getenv("DB_USER", ""),
    )

    contrasena = st.secrets.get(
        "DB_PASSWORD",
        os.getenv("DB_PASSWORD", ""),
    )

    driver = st.secrets.get(
        "DB_DRIVER",
        os.getenv(
            "DB_DRIVER",
            "ODBC Driver 17 for SQL Server",
        ),
    )

    if not servidor:
        raise ValueError(
            "No se configuró DB_SERVER."
        )

    if not base_datos:
        raise ValueError(
            "No se configuró DB_DATABASE."
        )

    parametros = {
        "driver": driver,
        "TrustServerCertificate": "yes",
    }

    if usuario and contrasena:
        url_conexion = URL.create(
            drivername="mssql+pyodbc",
            username=usuario,
            password=contrasena,
            host=servidor,
            database=base_datos,
            query=parametros,
        )
    else:
        parametros["trusted_connection"] = "yes"

        url_conexion = URL.create(
            drivername="mssql+pyodbc",
            host=servidor,
            database=base_datos,
            query=parametros,
        )

    engine = create_engine(
        url_conexion,
        pool_pre_ping=True,
        pool_recycle=1800,
        fast_executemany=True,
    )

    return engine