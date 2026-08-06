from datetime import date
import pandas as pd
import streamlit as st
from estilos import aplicar_estilos
from src.componentes import (
    encabezado_pagina,
    tarjeta_insight,
    tarjeta_kpi_principal,
    tarjeta_kpi_secundaria,
    tarjeta_kpi_doble, 
    titulo_bloque,
)
from src.datos import (
    cargar_detalle_club,
    cargar_venta_club,
)
from src.graficas import grafica_dona_cluster
from src.metricas import (
    obtener_metricas_generales,
    resumen_por_cluster,
    resumen_por_sucursal,
    contar_tickets_unicos,
)


aplicar_estilos()


# =========================================================
# FORMATOS
# =========================================================

def formato_moneda(valor: float) -> str:
    valor = float(valor or 0)

    if abs(valor) >= 1_000_000_000:
        return f"${valor / 1_000_000_000:,.1f} mil M"

    if abs(valor) >= 1_000_000:
        return f"${valor / 1_000_000:,.1f} M"

    if abs(valor) >= 1_000:
        return f"${valor / 1_000:,.1f} mil"

    return f"${valor:,.0f}"


def formato_entero(valor: float | int) -> str:
    return f"{int(valor or 0):,}"


def formato_porcentaje(valor: float) -> str:
    return f"{float(valor or 0):.2%}"


def obtener_periodo_anterior(
    fecha_inicio: date,
    fecha_fin: date,
) -> tuple[date, date]:
    inicio = pd.Timestamp(fecha_inicio)
    fin = pd.Timestamp(fecha_fin)

    return (
        (inicio - pd.DateOffset(years=1)).date(),
        (fin - pd.DateOffset(years=1)).date(),
    )


def opciones_texto(
    serie: pd.Series,
) -> list[str]:
    return sorted(
        serie.dropna()
        .astype(str)
        .str.strip()
        .loc[lambda x: x.ne("")]
        .unique()
        .tolist()
    )


def filtrar_por_texto(
    df: pd.DataFrame,
    columna: str,
    texto: str,
) -> pd.DataFrame:
    if not texto.strip():
        return df

    if columna not in df.columns:
        return df

    mascara = (
        df[columna]
        .fillna("")
        .astype(str)
        .str.contains(
            texto.strip(),
            case=False,
            regex=False,
        )
    )

    return df.loc[mascara].copy()


# =========================================================
# ENCABEZADO
# =========================================================

encabezado_pagina(
    titulo="Resumen por sucursal",
    subtitulo="Desempeño del programa Clientes Club",
)


# =========================================================
# PERIODO
# =========================================================

hoy = date.today()

with st.expander(
    "Periodo de análisis",
    icon=":material/calendar_month:",
    expanded=False,
):
    col_periodo, col_inicio, col_fin = st.columns(
        [1.1, 0.9, 0.9],
        gap="medium",
    )

    with col_periodo:
        periodo = st.selectbox(
            "Periodo",
            options=[
                "Año actual",
                "Últimos 12 meses",
                "Mes actual",
                "Personalizado",
            ],
            key="sucursal_periodo",
        )

    if periodo == "Año actual":
        fecha_inicio = date(hoy.year, 1, 1)
        fecha_fin = hoy

    elif periodo == "Últimos 12 meses":
        fecha_inicio = (
            pd.Timestamp(hoy)
            - pd.DateOffset(months=12)
        ).date()
        fecha_fin = hoy

    elif periodo == "Mes actual":
        fecha_inicio = date(
            hoy.year,
            hoy.month,
            1,
        )
        fecha_fin = hoy

    else:
        with col_inicio:
            fecha_inicio = st.date_input(
                "Fecha inicial",
                value=date(hoy.year, 1, 1),
                key="sucursal_fecha_inicio",
            )

        with col_fin:
            fecha_fin = st.date_input(
                "Fecha final",
                value=hoy,
                key="sucursal_fecha_fin",
            )

    if periodo != "Personalizado":
        with col_inicio:
            st.date_input(
                "Fecha inicial",
                value=fecha_inicio,
                disabled=True,
                key="sucursal_fecha_inicio_auto",
            )

        with col_fin:
            st.date_input(
                "Fecha final",
                value=fecha_fin,
                disabled=True,
                key="sucursal_fecha_fin_auto",
            )

if fecha_inicio > fecha_fin:
    st.error(
        "La fecha inicial no puede ser mayor que la fecha final."
    )
    st.stop()


fecha_inicio_aa, fecha_fin_aa = obtener_periodo_anterior(
    fecha_inicio,
    fecha_fin,
)


# =========================================================
# CARGA
# =========================================================

with st.spinner("Cargando información..."):
    df_actual = cargar_detalle_club(
        fecha_inicio,
        fecha_fin,
    )

    df_anterior = cargar_detalle_club(
        fecha_inicio_aa,
        fecha_fin_aa,
    )
    with st.spinner("Cargando venta total del formato Club..."):
        df_venta_formato_actual = cargar_venta_club(
            fecha_inicio,
            fecha_fin,
        )

        df_venta_formato_anterior = cargar_venta_club(
            fecha_inicio_aa,
            fecha_fin_aa,
        )


if df_actual.empty:
    st.warning(
        "No existen registros para el periodo seleccionado."
    )
    st.stop()


# =========================================================
# FILTROS
# =========================================================

with st.expander(
    "Filtros avanzados",
    icon=":material/tune:",
    expanded=True,
):
    fila_1 = st.columns(
        [1.1, 0.9, 0.95, 1.1],
        gap="medium",
    )

    with fila_1[0]:
        sucursales = st.multiselect(
            "Sucursal",
            options=opciones_texto(
                df_actual["sucursal"]
            ),
            placeholder="Todas las sucursales",
            key="filtro_sucursal",
        )

    df_dependiente = df_actual.copy()

    if sucursales:
        df_dependiente = df_dependiente[
            df_dependiente["sucursal"].isin(
                sucursales
            )
        ]

    with fila_1[1]:
        clusters = st.multiselect(
            "Cluster",
            options=opciones_texto(
                df_dependiente["nombre_cluster"]
            ),
            placeholder="Todos los clusters",
            key="filtro_cluster",
        )

    if clusters:
        df_dependiente = df_dependiente[
            df_dependiente["nombre_cluster"].isin(
                clusters
            )
        ]

    with fila_1[2]:
        categorias = st.multiselect(
            "Categoría",
            options=opciones_texto(
                df_dependiente["Categoria_GB"]
            ),
            placeholder="Todas las categorías",
            key="filtro_categoria",
        )

    if categorias:
        df_dependiente = df_dependiente[
            df_dependiente["Categoria_GB"].isin(
                categorias
            )
        ]

    with fila_1[3]:
        proveedores = st.multiselect(
            "Proveedor",
            options=opciones_texto(
                df_dependiente["Nombres_Agrupado"]
            ),
            placeholder="Todos los proveedores",
            key="filtro_proveedor",
        )

    fila_2 = st.columns(
        [1.65, 1, 0.8],
        gap="medium",
    )

    with fila_2[0]:
        buscar_cliente = st.text_input(
            "Buscar cliente",
            placeholder=(
                "Escribe nombre, apellido o parte del nombre"
            ),
            key="buscar_cliente",
            icon=":material/search:",
        )

    with fila_2[1]:
        buscar_tarjeta = st.text_input(
            "Número de tarjeta",
            placeholder="Ejemplo: 7001234",
            key="buscar_tarjeta",
            icon=":material/credit_card:",
        )

    with fila_2[2]:
        mes_vencimiento = st.selectbox(
            "Mes de vencimiento",
            options=[
                "Todos",
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre",
            ],
            key="mes_vencimiento",
        )


# =========================================================
# APLICAR FILTROS
# =========================================================

def aplicar_filtros(
    df: pd.DataFrame,
) -> pd.DataFrame:
    resultado = df.copy()

    if sucursales:
        resultado = resultado[
            resultado["sucursal"].isin(
                sucursales
            )
        ]

    if clusters:
        resultado = resultado[
            resultado["nombre_cluster"].isin(
                clusters
            )
        ]

    if categorias:
        resultado = resultado[
            resultado["Categoria_GB"].isin(
                categorias
            )
        ]

    if proveedores:
        resultado = resultado[
            resultado["Nombres_Agrupado"].isin(
                proveedores
            )
        ]

    resultado = filtrar_por_texto(
        resultado,
        "Nombre_Completo",
        buscar_cliente,
    )

    resultado = filtrar_por_texto(
        resultado,
        "NoTarjeta",
        buscar_tarjeta,
    )

    if (
        mes_vencimiento != "Todos"
        and "Fecha_Vencimiento" in resultado.columns
    ):
        mapa_meses = {
            "Enero": 1,
            "Febrero": 2,
            "Marzo": 3,
            "Abril": 4,
            "Mayo": 5,
            "Junio": 6,
            "Julio": 7,
            "Agosto": 8,
            "Septiembre": 9,
            "Octubre": 10,
            "Noviembre": 11,
            "Diciembre": 12,
        }

        resultado = resultado[
            resultado["Fecha_Vencimiento"].dt.month.eq(
                mapa_meses[mes_vencimiento]
            )
        ]

    return resultado


df_actual_filtrado = aplicar_filtros(df_actual)
df_anterior_filtrado = aplicar_filtros(df_anterior)


if df_actual_filtrado.empty:
    st.info(
        "No hay información que coincida con los filtros."
    )
    st.stop()

venta_formato_club = float(
    df_venta_formato_actual["Venta_Neta"].sum()
    if not df_venta_formato_actual.empty
    else 0
)

venta_formato_club_aa = float(
    df_venta_formato_anterior["Venta_Neta"].sum()
    if not df_venta_formato_anterior.empty
    else 0
)

variacion_formato_club = (
    (
        venta_formato_club
        - venta_formato_club_aa
    )
    / venta_formato_club_aa
    if venta_formato_club_aa != 0
    else 0
)
# =========================================================
# MÉTRICAS
# =========================================================

metricas = obtener_metricas_generales(
    df_actual_filtrado,
    df_anterior_filtrado,
)

df_cluster = resumen_por_cluster(
    df_actual_filtrado,
    df_anterior_filtrado,
)

df_sucursal = resumen_por_sucursal(
    df_actual_filtrado,
    df_anterior_filtrado,
)

abono_ytd = float(
    df_actual_filtrado["importeclubprecios"].sum()
    if "importeclubprecios"
    in df_actual_filtrado.columns
    else metricas["abono_actual"]
)

abono_ytd_aa = float(
    df_anterior_filtrado["importeclubprecios"].sum()
    if "importeclubprecios"
    in df_anterior_filtrado.columns
    else metricas["abono_anterior"]
)

variacion_abono_ytd = (
    (
        abono_ytd
        - abono_ytd_aa
    )
    / abono_ytd_aa
    if abono_ytd_aa != 0
    else 0
)

porcentaje_abono = (
    abono_ytd / metricas["venta_actual"]
    if metricas["venta_actual"] != 0
    else 0
)

porcentaje_abono_aa = (
    abono_ytd_aa / metricas["venta_anterior"]
    if metricas["venta_anterior"] != 0
    else 0
)

variacion_porcentaje_abono_pp = (
    porcentaje_abono
    - porcentaje_abono_aa
) * 100

tickets_club = contar_tickets_unicos(
    df_actual_filtrado
)

tickets_club_aa = contar_tickets_unicos(
    df_anterior_filtrado
)

ticket_promedio_club = (
    metricas["venta_actual"] / tickets_club
    if tickets_club > 0
    else 0
)
# =========================================================
# KPI PRINCIPALES (los 3 grandes, el kpi doble es otra card)
# =========================================================

st.markdown(
    '<div class="espacio-kpi-principal"></div>',
    unsafe_allow_html=True,
)

with st.container(
    key="kpi_principales",
):
    columnas_principales = st.columns(
        4,
        gap="medium",
    )
    ticket_promedio_formato = None

    with columnas_principales[0]:
        tarjeta_kpi_principal(
            titulo="Venta Club",
            valor=formato_moneda(
                metricas["venta_actual"]
            ),
            subtitulo="Total del periodo",
            icono="$",
            color="azul",
            variacion=metricas["variacion_venta"],
        )

    with columnas_principales[1]:
        tarjeta_kpi_principal(
            titulo="Venta formato Club",
            valor=formato_moneda(
                venta_formato_club
            ),
            subtitulo="Total grupo Year To Date",
            icono="▣",
            color="azul",
            variacion=variacion_formato_club,
        )

    with columnas_principales[2]:
        tarjeta_kpi_principal(
            titulo="Tarjetas activas",
            valor=formato_entero(
                metricas["tarjetas_actuales"]
            ),
            subtitulo="Clientes con compra",
            icono="●",
            color="azul",
            variacion=metricas["variacion_tarjetas"],
        )

    with columnas_principales[3]:
        tarjeta_kpi_doble(
            titulo="Ticket promedio",
            titulo_izquierdo="Tarjeta Club",
            valor_izquierdo=formato_moneda(
                ticket_promedio_club
            ),
            titulo_derecho="Formato Club",
            valor_derecho=(
                formato_moneda(
                    ticket_promedio_formato
                )
                if ticket_promedio_formato is not None
                else "N/D"
            ),
            subtitulo="Venta promedio por ticket",
            icono="↔",
            color="azul",
        )


# =========================================================
# KPI SECUNDARIOS (los cards chiquitos)
# =========================================================

st.markdown(
    '<div class="espacio-kpi-secundaria"></div>',
    unsafe_allow_html=True,
)

with st.container(
    key="kpi_secundarios",
):
    columnas_secundarias = st.columns(
        5,
        gap="small",
    )

    with columnas_secundarias[0]:
        tarjeta_kpi_secundaria(
            titulo="Clientes App",
            valor=formato_entero(
                metricas["clientes_app"]
            ),
            subtitulo="Usuarios identificados",
            icono="◉",
            color="azul",
            variacion=metricas[
                "variacion_clientes_app"
            ],
        )

    with columnas_secundarias[1]:
        tarjeta_kpi_secundaria(
            titulo="Abono",
            valor=formato_moneda(
                metricas["abono_actual"]
            ),
            subtitulo="Bonificación acumulada",
            icono="◇",
            color="azul",
            variacion=metricas["variacion_abono"],
        )

    with columnas_secundarias[2]:
        tarjeta_kpi_secundaria(
            titulo="Abono Year To Date",
            valor=formato_moneda(
                abono_ytd
            ),
            subtitulo="Monto acumulado",
            icono="$",
            color="azul",
            variacion=variacion_abono_ytd,
        )

    with columnas_secundarias[3]:
        tarjeta_kpi_secundaria(
            titulo="% Abono",
            valor=formato_porcentaje(
                porcentaje_abono
            ),
            subtitulo="Porcentaje Year To Date",
            icono="▥",
            color="azul",
            variacion=(
                variacion_porcentaje_abono_pp
            ),
            variacion_pp=True,
        )

    with columnas_secundarias[4]:
        tarjeta_kpi_secundaria(
            titulo="Margen",
            valor=formato_porcentaje(
                metricas["margen"]
            ),
            subtitulo="Margen frontal actual",
            icono="↗",
            color="azul",
            variacion=metricas[
                "variacion_margen_pp"
            ],
            variacion_pp=True,
        )

# =========================================================
# INSIGHT DEBAJO DE LOS KPI
# =========================================================

st.markdown(
    '<div class="espacio-insight"></div>',
    unsafe_allow_html=True,
)

if not df_cluster.empty and not df_sucursal.empty:
    cluster_lider = df_cluster.iloc[0]
    sucursal_lider = df_sucursal.iloc[0]

    columna_cluster = (
        "nombre_cluster"
        if "nombre_cluster" in df_cluster.columns
        else "subcluster_ia"
    )

    texto_insight = (
        f"El cluster {cluster_lider[columna_cluster]} lidera "
        f"la participación con "
        f"{cluster_lider['share_venta']:.1%} del total de venta Club. "
        f"Su variación contra el año anterior es de "
        f"{cluster_lider['variacion_venta']:.1%}. "
        f"La sucursal con mayor venta es "
        f"{sucursal_lider['sucursal']}, con "
        f"{formato_moneda(sucursal_lider['venta_actual'])}. "
        f"En el periodo se identificaron "
        f"{formato_entero(metricas['clientes_app'])} clientes App."
    )

    tarjeta_insight(
        texto=texto_insight,
        titulo="Resumen inteligente del periodo",
    )


# =========================================================
# PRIMERA FILA DE ANÁLISIS
# =========================================================

st.markdown(
    '<div class="espacio-seccion-grande"></div>',
    unsafe_allow_html=True,
)

col_cluster, col_sucursal = st.columns(
    [1.05, 1],
    gap="medium",
)


# ---------------------------------------------------------
# CLUSTER
# ---------------------------------------------------------

with col_cluster:
    with st.container(border=True):
        titulo_bloque(
            titulo="Desempeño por cluster",
            subtitulo=(
                "Participación y variación "
                "contra el año anterior"
            ),
            icono="◔",
        )

        st.markdown(
            '<div class="separador-suave"></div>',
            unsafe_allow_html=True,
        )

        col_tabla_cluster, col_dona = st.columns(
            [1.25, 1],
            gap="small",
        )

        with col_tabla_cluster:
            tabla_cluster = df_cluster.rename(
                columns={
                    "nombre_cluster": "Cluster",
                    "subcluster_ia": "Cluster",
                    "share_venta": "Share",
                    "venta_actual": "Venta Club",
                    "variacion_venta": "Variación",
                    "margen": "Margen",
                }
            )

            columnas_cluster = [
                "Cluster",
                "Share",
                "Venta Club",
                "Variación",
                "Margen",
            ]

            columnas_cluster = [
                columna
                for columna in columnas_cluster
                if columna in tabla_cluster.columns
            ]

            st.dataframe(
                tabla_cluster[columnas_cluster],
                use_container_width=True,
                hide_index=True,
                height=310,
                column_config={
                    "Share": (
                        st.column_config.ProgressColumn(
                            "Share",
                            min_value=0,
                            max_value=1,
                            format="%.1f%%",
                        )
                    ),
                    "Venta Club": (
                        st.column_config.NumberColumn(
                            format="$%,.0f"
                        )
                    ),
                    "Variación": (
                        st.column_config.NumberColumn(
                            format="%.1f%%"
                        )
                    ),
                    "Margen": (
                        st.column_config.NumberColumn(
                            format="%.1f%%"
                        )
                    ),
                },
            )

        with col_dona:
            st.plotly_chart(
                grafica_dona_cluster(df_cluster),
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )


# ---------------------------------------------------------
# TOP SUCURSALES
# ---------------------------------------------------------

with col_sucursal:
    with st.container(border=True):
        titulo_bloque(
            titulo="Top 10 sucursales",
            subtitulo="Sucursales con mayor venta Club",
            icono="▣",
        )

        st.markdown(
            '<div class="separador-suave"></div>',
            unsafe_allow_html=True,
        )

        top_sucursales = (
            df_sucursal
            .nlargest(10, "venta_actual")
            .copy()
        )

        tabla_top = top_sucursales.rename(
            columns={
                "sucursal": "Sucursal",
                "venta_actual": "Venta Club",
                "share_venta": "Share",
                "variacion_venta": "Variación",
            }
        )

        st.dataframe(
            tabla_top[
                [
                    "Sucursal",
                    "Venta Club",
                    "Share",
                    "Variación",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=365,
            column_config={
                "Venta Club": (
                    st.column_config.NumberColumn(
                        format="$%,.0f"
                    )
                ),
                "Share": (
                    st.column_config.ProgressColumn(
                        "Share",
                        min_value=0,
                        max_value=1,
                        format="%.1f%%",
                    )
                ),
                "Variación": (
                    st.column_config.NumberColumn(
                        format="%.1f%%"
                    )
                ),
            },
        )


# =========================================================
# TABLAS DETALLADAS (aqui vienen todas las  medidas revisar que pasar arriba, aqi podria estar todo lo del BI pero arriba lo mas importante)
# =========================================================

st.markdown(
    '<div class="espacio-seccion-grande"></div>',
    unsafe_allow_html=True,
)

col_detalle_cluster, col_detalle_sucursal = st.columns(
    2,
    gap="medium",
)


with col_detalle_cluster:
    with st.container(border=True):
        titulo_bloque(
            titulo="Detalle por cluster",
            subtitulo=(
                "Clientes, productos, tickets, "
                "venta y bonificación"
            ),
            icono="◎",
        )

        st.markdown(
            '<div class="separador-suave"></div>',
            unsafe_allow_html=True,
        )

        detalle_cluster = df_cluster.rename(
            columns={
                "nombre_cluster": "Cluster",
                "subcluster_ia": "Cluster",
                "tarjetas_activas": "Tarjetas",
                "clientes_app": "Clientes App",
                "skus": "SKU",
                "tickets": "Tickets",
                "venta_actual": "Venta actual",
                "venta_anterior": "Venta AA",
                "variacion_venta": "Variación",
                "abono_actual": "Abono",
                "margen": "Margen",
            }
        )

        columnas_detalle_cluster = [
            "Cluster",
            "Tarjetas",
            "Clientes App",
            "SKU",
            "Tickets",
            "Venta actual",
            "Venta AA",
            "Variación",
            "Abono",
            "Margen",
        ]

        columnas_detalle_cluster = [
            columna
            for columna in columnas_detalle_cluster
            if columna in detalle_cluster.columns
        ]

        st.dataframe(
            detalle_cluster[columnas_detalle_cluster],
            use_container_width=True,
            hide_index=True,
            height=410,
            column_config={
                "Venta actual": (
                    st.column_config.NumberColumn(
                        format="$%,.0f"
                    )
                ),
                "Venta AA": (
                    st.column_config.NumberColumn(
                        format="$%,.0f"
                    )
                ),
                "Variación": (
                    st.column_config.NumberColumn(
                        format="%.1f%%"
                    )
                ),
                "Abono": (
                    st.column_config.NumberColumn(
                        format="$%,.0f"
                    )
                ),
                "Margen": (
                    st.column_config.NumberColumn(
                        format="%.1f%%"
                    )
                ),
            },
        )


with col_detalle_sucursal:
    with st.container(border=True):
        titulo_bloque(
            titulo="Detalle por sucursal",
            subtitulo=(
                "Actividad comercial de todas "
                "las sucursales"
            ),
            icono="▤",
        )

        st.markdown(
            '<div class="separador-suave"></div>',
            unsafe_allow_html=True,
        )

        detalle_sucursal = df_sucursal.rename(
            columns={
                "sucursal": "Sucursal",
                "share_venta": "Share",
                "tarjetas_activas": "Tarjetas",
                "clientes_app": "Clientes App",
                "skus": "SKU",
                "tickets": "Tickets",
                "venta_actual": "Venta actual",
                "venta_anterior": "Venta AA",
                "variacion_venta": "Variación",
            }
        )

        columnas_detalle_sucursal = [
            "Sucursal",
            "Share",
            "Tarjetas",
            "Clientes App",
            "SKU",
            "Tickets",
            "Venta actual",
            "Venta AA",
            "Variación",
        ]

        st.dataframe(
            detalle_sucursal[columnas_detalle_sucursal],
            use_container_width=True,
            hide_index=True,
            height=410,
            column_config={
                "Share": (
                    st.column_config.ProgressColumn(
                        "Share",
                        min_value=0,
                        max_value=1,
                        format="%.1f%%",
                    )
                ),
                "Venta actual": (
                    st.column_config.NumberColumn(
                        format="$%,.0f"
                    )
                ),
                "Venta AA": (
                    st.column_config.NumberColumn(
                        format="$%,.0f"
                    )
                ),
                "Variación": (
                    st.column_config.NumberColumn(
                        format="%.1f%%"
                    )
                ),
            },
        )


# =========================================================
# CLIENTES
# =========================================================

st.markdown(
    '<div class="espacio-seccion-grande"></div>',
    unsafe_allow_html=True,
)

with st.expander(
    "Ver detalle de clientes",
    icon=":material/person_search:",
):
    columnas_cliente = [
        "Nombre_Completo",
        "NoTarjeta",
        "nombre_cluster",
        "sucursal",
        "Categoria_GB",
        "Nombres_Agrupado",
        "Fecha_Compra",
        "Importe_Neto",
        "Aportar",
    ]

    columnas_cliente = [
        columna
        for columna in columnas_cliente
        if columna in df_actual_filtrado.columns
    ]

    detalle_clientes = (
        df_actual_filtrado[columnas_cliente]
        .sort_values(
            "Importe_Neto",
            ascending=False,
        )
        .head(5000)
    )

    st.dataframe(
        detalle_clientes,
        use_container_width=True,
        hide_index=True,
        height=470,
        column_config={
            "Nombre_Completo": "Cliente",
            "NoTarjeta": "Número de tarjeta",
            "nombre_cluster": "Cluster",
            "sucursal": "Sucursal",
            "Categoria_GB": "Categoría",
            "Nombres_Agrupado": "Proveedor",
            "Fecha_Compra": st.column_config.DateColumn(
                "Fecha de compra",
                format="DD/MM/YYYY",
            ),
            "Importe_Neto": st.column_config.NumberColumn(
                "Venta",
                format="$%,.2f",
            ),
            "Aportar": st.column_config.NumberColumn(
                "Abono",
                format="$%,.2f",
            ),
        },
    )