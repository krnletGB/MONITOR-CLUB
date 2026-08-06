import numpy as np
import pandas as pd
# =========================================================
# MEDIDAS
# =========================================================

VALORES_APP = {
    "1",
    "true",
    "si",
    "sí",
    "s",
    "yes",
}


def dividir_seguro(
    numerador: float,
    denominador: float,
) -> float:
    if denominador in (0, None) or pd.isna(denominador):
        return 0.0

    return numerador / denominador


def mascara_app(
    serie: pd.Series,
) -> pd.Series:
    return (
        serie.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(VALORES_APP)
    )


def preparar_tarjeta_app(
    df: pd.DataFrame,
) -> pd.DataFrame:
    resultado = df.copy()

    if {"AceptaApp", "NoTarjeta"}.issubset(resultado.columns):
        resultado["tarjeta_app"] = resultado["NoTarjeta"].where(
            mascara_app(resultado["AceptaApp"])
        )
    else:
        resultado["tarjeta_app"] = pd.NA

    return resultado


def obtener_metricas_generales(
    df_actual: pd.DataFrame,
    df_anterior: pd.DataFrame,
) -> dict:
    venta_actual = float(
        df_actual["Importe_Neto"].sum()
        if "Importe_Neto" in df_actual.columns
        else 0
    )

    venta_anterior = float(
        df_anterior["Importe_Neto"].sum()
        if "Importe_Neto" in df_anterior.columns
        else 0
    )

    abono_actual = float(
        df_actual["Aportar"].sum()
        if "Aportar" in df_actual.columns
        else 0
    )

    abono_anterior = float(
        df_anterior["Aportar"].sum()
        if "Aportar" in df_anterior.columns
        else 0
    )

    tarjetas_actuales = int(
        df_actual["NoTarjeta"].nunique()
        if "NoTarjeta" in df_actual.columns
        else 0
    )

    tarjetas_anteriores = int(
        df_anterior["NoTarjeta"].nunique()
        if "NoTarjeta" in df_anterior.columns
        else 0
    )

    sucursales_actuales = int(
        df_actual["Cve_Sucursal"].nunique()
        if "Cve_Sucursal" in df_actual.columns
        else 0
    )

    sucursales_anteriores = int(
        df_anterior["Cve_Sucursal"].nunique()
        if "Cve_Sucursal" in df_anterior.columns
        else 0
    )

    clientes_app = 0
    clientes_app_anterior = 0

    if {"AceptaApp", "NoTarjeta"}.issubset(df_actual.columns):
        clientes_app = int(
            df_actual.loc[
                mascara_app(df_actual["AceptaApp"]),
                "NoTarjeta",
            ].nunique()
        )

    if {"AceptaApp", "NoTarjeta"}.issubset(df_anterior.columns):
        clientes_app_anterior = int(
            df_anterior.loc[
                mascara_app(df_anterior["AceptaApp"]),
                "NoTarjeta",
            ].nunique()
        )

    margen = 0.0
    margen_anterior = 0.0

    if {"Importe_Neto", "CP_Real"}.issubset(df_actual.columns):
        costo_actual = float(df_actual["CP_Real"].sum())
        margen = dividir_seguro(
            venta_actual - costo_actual,
            venta_actual,
        )

    if {"Importe_Neto", "CP_Real"}.issubset(df_anterior.columns):
        costo_anterior = float(df_anterior["CP_Real"].sum())
        margen_anterior = dividir_seguro(
            venta_anterior - costo_anterior,
            venta_anterior,
        )
    # VARIACION ES LA DIFERENCIA EN POWER BI
    return {
        "venta_actual": venta_actual,
        "venta_anterior": venta_anterior,
        "variacion_venta": dividir_seguro(
            venta_actual - venta_anterior,
            venta_anterior,
        ),
        "abono_actual": abono_actual,
        "abono_anterior": abono_anterior,
        "variacion_abono": dividir_seguro(
            abono_actual - abono_anterior,
            abono_anterior,
        ),
        "tarjetas_actuales": tarjetas_actuales,
        "tarjetas_anteriores": tarjetas_anteriores,
        "variacion_tarjetas": dividir_seguro(
            tarjetas_actuales - tarjetas_anteriores,
            tarjetas_anteriores,
        ),
        "clientes_app": clientes_app,
        "clientes_app_anterior": clientes_app_anterior,
        "variacion_clientes_app": dividir_seguro(
            clientes_app - clientes_app_anterior,
            clientes_app_anterior,
        ),
        "margen": margen,
        "margen_anterior": margen_anterior,
        "variacion_margen_pp": (
            margen - margen_anterior
        ) * 100,
        "sucursales_actuales": sucursales_actuales,
        "sucursales_anteriores": sucursales_anteriores,
        "variacion_sucursales": (
            sucursales_actuales - sucursales_anteriores
        ),
    }


def resumen_por_cluster(
    df_actual: pd.DataFrame,
    df_anterior: pd.DataFrame,
) -> pd.DataFrame:
    if df_actual.empty:
        return pd.DataFrame()

    columna_cluster = (
        "nombre_cluster"
        if "nombre_cluster" in df_actual.columns
        else "subcluster_ia"
    )

    actual_preparado = preparar_tarjeta_app(df_actual)
    anterior_preparado = preparar_tarjeta_app(df_anterior)

    actual = (
        actual_preparado.groupby(
            columna_cluster,
            dropna=False,
        )
        .agg(
            tarjetas_activas=("NoTarjeta", "nunique"),
            clientes_app=("tarjeta_app", "nunique"),
            skus=("Cve_Producto", "nunique"),
            tickets=("Remision", "nunique"),
            venta_actual=("Importe_Neto", "sum"),
            abono_actual=("Aportar", "sum"),
            costo_actual=("CP_Real", "sum"),
        )
        .reset_index()
    )

    anterior = (
        anterior_preparado.groupby(
            columna_cluster,
            dropna=False,
        )
        .agg(
            venta_anterior=("Importe_Neto", "sum"),
            abono_anterior=("Aportar", "sum"),
        )
        .reset_index()
    )

    resumen = actual.merge(
        anterior,
        on=columna_cluster,
        how="left",
    )

    resumen[
        ["venta_anterior", "abono_anterior"]
    ] = resumen[
        ["venta_anterior", "abono_anterior"]
    ].fillna(0)

    total_venta = resumen["venta_actual"].sum()

    resumen["share_venta"] = np.where(
        total_venta > 0,
        resumen["venta_actual"] / total_venta,
        0,
    )

    resumen["variacion_venta"] = np.where(
        resumen["venta_anterior"] != 0,
        (
            resumen["venta_actual"]
            - resumen["venta_anterior"]
        )
        / resumen["venta_anterior"],
        0,
    )

    resumen["variacion_abono"] = np.where(
        resumen["abono_anterior"] != 0,
        (
            resumen["abono_actual"]
            - resumen["abono_anterior"]
        )
        / resumen["abono_anterior"],
        0,
    )

    resumen["margen"] = np.where(
        resumen["venta_actual"] != 0,
        (
            resumen["venta_actual"]
            - resumen["costo_actual"]
        )
        / resumen["venta_actual"],
        0,
    )

    return resumen.sort_values(
        "venta_actual",
        ascending=False,
    )


def resumen_por_sucursal(
    df_actual: pd.DataFrame,
    df_anterior: pd.DataFrame,
) -> pd.DataFrame:
    if df_actual.empty:
        return pd.DataFrame()

    actual_preparado = preparar_tarjeta_app(df_actual)
    anterior_preparado = preparar_tarjeta_app(df_anterior)

    actual = (
        actual_preparado.groupby(
            ["Cve_Sucursal", "sucursal"],
            dropna=False,
        )
        .agg(
            tarjetas_activas=("NoTarjeta", "nunique"),
            clientes_app=("tarjeta_app", "nunique"),
            skus=("Cve_Producto", "nunique"),
            tickets=("Remision", "nunique"),
            venta_actual=("Importe_Neto", "sum"),
        )
        .reset_index()
    )

    anterior = (
        anterior_preparado.groupby(
            ["Cve_Sucursal", "sucursal"],
            dropna=False,
        )
        .agg(
            venta_anterior=("Importe_Neto", "sum"),
        )
        .reset_index()
    )

    resumen = actual.merge(
        anterior,
        on=["Cve_Sucursal", "sucursal"],
        how="left",
    )

    resumen["venta_anterior"] = resumen[
        "venta_anterior"
    ].fillna(0)

    total_venta = resumen["venta_actual"].sum()

    resumen["share_venta"] = np.where(
        total_venta > 0,
        resumen["venta_actual"] / total_venta,
        0,
    )

    resumen["variacion_venta"] = np.where(
        resumen["venta_anterior"] != 0,
        (
            resumen["venta_actual"]
            - resumen["venta_anterior"]
        )
        / resumen["venta_anterior"],
        0,
    )

    return resumen.sort_values(
        "venta_actual",
        ascending=False,
    )


def contar_tickets_unicos(
    df: pd.DataFrame,
) -> int:
    """
    Cuenta tickets sin mezclar remisiones iguales
    pertenecientes a diferentes sucursales o cajas. (Tickers unicos)
    """
    columnas_ticket = [
        columna
        for columna in [
            "Cve_Sucursal",
            "Caja",
            "Remision",
        ]
        if columna in df.columns
    ]

    if not columnas_ticket:
        return 0

    return int(
        df[columnas_ticket]
        .dropna(how="all")
        .drop_duplicates()
        .shape[0]
    )

