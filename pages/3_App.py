import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from src.conexion import obtener_engine
import plotly.graph_objects as go


st.set_page_config(page_title="APP", layout="wide")


DICC_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# =========================================================
# 1. FUNCIONES PARA CARGAR DATOS DESDE SQL SERVER
# =========================================================
@st.cache_data(ttl=300)
def obtener_datos_app():
    query = "SELECT * FROM clientes_que_usan_App"
    engine = obtener_engine()
    return pd.read_sql(query, engine)

@st.cache_data(ttl=3600)
def obtener_fechas_limite():
    engine = obtener_engine()
    query = """
    SELECT 
        MIN(Fecha_Compra) AS fecha_min,
        MAX(Fecha_Compra) AS fecha_max
    FROM ia_tarjetas_club
    """
    df = pd.read_sql(query, engine)
    return df['fecha_min'].iloc[0], df['fecha_max'].iloc[0]

@st.cache_data(ttl=3600)
def obtener_anios_disponibles():
    engine = obtener_engine()
    query = "SELECT DISTINCT YEAR(Fecha_Compra) AS anio FROM ia_tarjetas_club WHERE Fecha_Compra IS NOT NULL ORDER BY anio DESC"
    df = pd.read_sql(query, engine)
    return df['anio'].tolist()

@st.cache_data(ttl=3600)
def obtener_catalogos_filtros():
    engine = obtener_engine()

    def fetch_list(query, col_name):
        try:
            df = pd.read_sql(query, engine)
            return sorted([x for x in df[col_name].dropna().unique() if str(x).strip() != ''])
        except Exception:
            return []

    return {
        'nombre_cluster': fetch_list("SELECT DISTINCT nombre_cluster FROM ia_tarjetas_club WHERE nombre_cluster IS NOT NULL", "nombre_cluster"),
        'Categoria': fetch_list("SELECT DISTINCT Categoria_GB FROM ia_tarjetas_club WHERE Categoria_GB IS NOT NULL", "Categoria_GB"),
        'Nombre': fetch_list("SELECT DISTINCT Nombre_Completo FROM ia_tarjetas_club WHERE Nombre_Completo IS NOT NULL", "Nombre_Completo"),
        'sucursal': fetch_list("SELECT DISTINCT sucursal FROM ia_tarjetas_club WHERE sucursal IS NOT NULL", "sucursal"),
        'Proveedor': fetch_list("SELECT DISTINCT Nombre_Proveedor FROM ia_tarjetas_club WHERE Nombre_Proveedor IS NOT NULL", "Nombre_Proveedor"),
        'NoTarjeta': fetch_list("SELECT DISTINCT NoTarjeta FROM ia_tarjetas_club WHERE NoTarjeta IS NOT NULL", "NoTarjeta")
    }

@st.cache_data(ttl=3600)
def obtener_crecimiento_adopcion():
    engine = obtener_engine()
    query = """
    WITH Web AS (
        SELECT 
            FORMAT(acepta_condiciones, 'yyyy-MM') AS Mes,
            COUNT(*) AS Cantidad_Web
        FROM gr_clubprecios
        WHERE acepta_condiciones IS NOT NULL
        GROUP BY FORMAT(acepta_condiciones, 'yyyy-MM')
    ),
    Movil AS (
        SELECT 
            FORMAT(FechaAceptacionApp, 'yyyy-MM') AS Mes,
            COUNT(*) AS Cantidad_Movil
        FROM gr_clubprecios
        WHERE FechaAceptacionApp IS NOT NULL
          AND AceptaApp = 'S'
        GROUP BY FORMAT(FechaAceptacionApp, 'yyyy-MM')
    )
    SELECT 
        COALESCE(w.Mes, m.Mes) AS Mes,
        ISNULL(w.Cantidad_Web, 0) AS Registros_Web,
        ISNULL(m.Cantidad_Movil, 0) AS Registros_Movil
    FROM Web w
    FULL OUTER JOIN Movil m ON w.Mes = m.Mes
    WHERE COALESCE(w.Mes, m.Mes) IS NOT NULL
    ORDER BY Mes ASC
    """
    return pd.read_sql(query, engine)

def _construir_filtros_extra(filtros: dict) -> str:
    condiciones = []
    if filtros.get('categoria') and filtros['categoria'] != "Todas":
        condiciones.append(f"Categoria_GB = '{filtros['categoria']}'")
    if filtros.get('cliente') and filtros['cliente'] != "Todas":
        condiciones.append(f"Nombre_Completo = '{filtros['cliente']}'")
    if filtros.get('sucursal') and filtros['sucursal'] != "Todas":
        condiciones.append(f"sucursal = '{filtros['sucursal']}'")
    if filtros.get('proveedor') and filtros['proveedor'] != "Todas":
        condiciones.append(f"Nombre_Proveedor = '{filtros['proveedor']}'")
    if filtros.get('no_tarjeta') and filtros['no_tarjeta'] != "Todas":
        condiciones.append(f"NoTarjeta = '{filtros['no_tarjeta']}'")
    return (" AND " + " AND ".join(condiciones)) if condiciones else ""

def _clusters_in_clause(clusters: list) -> str:
    lista = ", ".join(f"'{c}'" for c in clusters)
    return f"nombre_cluster IN ({lista})"

# Consulta por Año y Mes (YTD)
def obtener_resumen_cluster_anio_sql(clusters, anio_seleccionado, mes_seleccionado, filtros_extra):
    anio_anterior = anio_seleccionado - 1
    where_cluster = _clusters_in_clause(clusters)
    extra = _construir_filtros_extra(filtros_extra)

    query = f"""
    WITH DatosBase AS (
        SELECT 
            nombre_cluster,
            CASE 
                WHEN YEAR(Fecha_Compra) = {anio_seleccionado} THEN 'Actual'
                WHEN YEAR(Fecha_Compra) = {anio_anterior} THEN 'Anterior'
            END AS Periodo,
            NoTarjeta,
            Cve_Cliente,
            Cve_Producto,
            Importe_Neto,
            importeclubprecios,
            CP_Real_Gral,
            acepta_condiciones
        FROM ia_tarjetas_club
        WHERE {where_cluster}
          AND YEAR(Fecha_Compra) IN ({anio_seleccionado}, {anio_anterior})
          AND MONTH(Fecha_Compra) = {mes_seleccionado}
          {extra}
    )
    SELECT 
        nombre_cluster,
        Periodo,
        COUNT(DISTINCT NoTarjeta) AS Tarjetas_Activas,
        COUNT(DISTINCT CASE WHEN acepta_condiciones IS NOT NULL THEN Cve_Cliente END) AS Clientes_App_Web,
        COUNT(DISTINCT Cve_Producto) AS Num_SKU,
        SUM(Importe_Neto) AS Importe_Neto,
        SUM(importeclubprecios) AS Importe_Club,
        SUM(CP_Real_Gral) AS Costo_Promedio
    FROM DatosBase
    WHERE Periodo IS NOT NULL
    GROUP BY nombre_cluster, Periodo
    """
    engine = obtener_engine()
    return pd.read_sql(query, engine)

# Consulta de Proveedores por Año y Mes (YTD)
def obtener_resumen_proveedor_anio_sql(clusters, anio_seleccionado, mes_seleccionado, filtros_extra):
    anio_anterior = anio_seleccionado - 1
    lista_clusters = ", ".join(f"'{c}'" for c in clusters)
    where_cluster = f"nombre_cluster IN ({lista_clusters})"
    extra = _construir_filtros_extra(filtros_extra)

    query = f"""
    WITH DatosBase AS (
        SELECT 
            Nombre_Proveedor,
            CASE 
                WHEN YEAR(Fecha_Compra) = {anio_seleccionado} THEN 'Actual'
                WHEN YEAR(Fecha_Compra) = {anio_anterior} THEN 'Anterior'
            END AS Periodo,
            Importe_Neto,
            importeclubprecios,
            CP_Real_Gral
        FROM ia_tarjetas_club WITH (NOLOCK)
        WHERE {where_cluster}
          AND YEAR(Fecha_Compra) IN ({anio_seleccionado}, {anio_anterior})
          AND MONTH(Fecha_Compra) = {mes_seleccionado}
          {extra}
    )
    SELECT 
        Nombre_Proveedor,
        Periodo,
        SUM(Importe_Neto) AS Importe_Neto,
        SUM(importeclubprecios) AS Importe_Club,
        SUM(CP_Real_Gral) AS Costo_Promedio
    FROM DatosBase
    WHERE Periodo IS NOT NULL AND Nombre_Proveedor IS NOT NULL AND Nombre_Proveedor <> ''
    GROUP BY Nombre_Proveedor, Periodo
    """
    engine = obtener_engine()
    return pd.read_sql(query, engine)

def construir_tabla_proveedor(df_raw):
    if df_raw.empty:
        return pd.DataFrame(columns=[
            'Nombres Proveedor.', 'VTA Actual', 'VTA AA', 'Margen Frontal', 'Margen Frontal C/ Bonificación'
        ])

    df_act = df_raw[df_raw['Periodo'] == 'Actual'].set_index('Nombre_Proveedor')
    df_ant = df_raw[df_raw['Periodo'] == 'Anterior'].set_index('Nombre_Proveedor')
    proveedores = df_raw['Nombre_Proveedor'].unique()

    filas = []
    for p in proveedores:
        vta_act = df_act.loc[p, 'Importe_Neto'] if p in df_act.index else 0.0
        abono_act = df_act.loc[p, 'Importe_Club'] if p in df_act.index else 0.0
        costo_act = df_act.loc[p, 'Costo_Promedio'] if p in df_act.index else 0.0
        vta_ant = df_ant.loc[p, 'Importe_Neto'] if p in df_ant.index else 0.0

        m_frontal = ((vta_act - costo_act) / vta_act) if vta_act else 0.0
        m_frontal_bonif = ((vta_act - costo_act - abono_act) / vta_act) if vta_act else 0.0

        filas.append({
            'Nombres Proveedor.': p,
            'VTA Actual': vta_act,
            'VTA AA': vta_ant,
            'Margen Frontal': m_frontal,
            'Margen Frontal C/ Bonificación': m_frontal_bonif
        })
    return pd.DataFrame(filas)


# =========================================================
# 2. ESTILOS CSS 
# =========================================================
st.markdown("""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">
    
    <style>
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #FF5100;
        border-radius: 10px;
        padding: 14px 16px;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 18px -3px rgba(0, 51, 102, 0.12), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #ff5100;
        border-left-color: #e04700;
    }

    .kpi-top {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .kpi-header {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #1e293b;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined', 'Material Icons';
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        line-height: 1;
        color: #334FB5;
        display: inline-block;
    }

    .kpi-value {
        font-size: 22px;
        font-weight: 800;
        color: #334FB5;
        line-height: 1.2;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .kpi-label {
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 6px;
    }

    .kpi-badge-positive {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        color: #15803d;
        background-color: #dcfce7;
        padding: 2px 8px;
        border-radius: 6px;
        margin-top: 4px;
        width: fit-content;
    }
    
    .kpi-badge-negative {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        color: #b91c1c;
        background-color: #fee2e2;
        padding: 2px 8px;
        border-radius: 6px;
        margin-top: 4px;
        width: fit-content;
    }

    .kpi-badge-info {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        color: #334FB5;
        background-color: #e0f2fe;
        padding: 2px 8px;
        border-radius: 6px;
        margin-top: 4px;
        width: fit-content;
    }

    .section-header-container {
        background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
        border: 1px solid #cbd5e1;
        border-left: 5px solid #334FB5;
        border-radius: 10px;
        padding: 12px 20px;
        margin-top: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }

    .section-header-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .section-header-icon {
        background: rgba(0, 51, 102, 0.08);
        border-radius: 8px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .section-title {
        font-size: 26px;
        font-weight: 800;
        color: #334FB5;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.3px;
        text-transform: uppercase;
    }

    .section-subtitle {
        font-size: 12px;
        font-weight: 500;
        color: #475569;
        margin-top: 2px;
    }

    .filter-panel-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    .filter-badge-req {
        background-color: #fff7ed;
        color: #FF5100;
        border: 1px solid #ffd8c2;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-left: 6px;
    }

    .filter-badge-opt {
        background-color: #f0f7ff;
        color: #334FB5;
        border: 1px solid #bae6fd;
        font-size: 10px;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        text-transform: uppercase;
        margin-left: 6px;
    }

    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border-color: #cbd5e1 !important;
        transition: all 0.2s ease;
    }

    div[data-baseweb="select"]:hover > div {
        border-color: #1E88E5 !important;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF5100 0%, #e04700 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(255, 81, 0, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(255, 81, 0, 0.35) !important;
    }

    .stApp [data-testid="stExpander"] {
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        background-color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_kpi_card(icon, titulo, valor, label, delta=None):
    badge_html = ""
    if delta is not None:
        if isinstance(delta, (int, float)):
            clase = "kpi-badge-positive" if delta >= 0 else "kpi-badge-negative"
            simbolo = "▲" if delta >= 0 else "▼"
            badge_html = f'<div class="{clase}">{simbolo} {delta:.2%}</div>'
        else:
            badge_html = f'<div class="kpi-badge-info">{delta}</div>'

    card_html = (
        f'<div class="kpi-card">'
        f'<div class="kpi-top">'
        f'<div class="kpi-header">'
        f'<span class="material-symbols-outlined">{icon}</span>'
        f'<span>{titulo}</span>'
        f'</div>'
        f'<div class="kpi-value">{valor}</div>'
        f'{badge_html}'
        f'</div>'
        f'<div class="kpi-label" title="{label}">{label}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

def render_section_header(icon, titulo, subtitulo=""):
    header_html = f"""
    <div class="section-header-container">
        <div class="section-header-left">
            <div class="section-header-icon">
                <span class="material-symbols-outlined">{icon}</span>
            </div>
            <div>
                <div class="section-title">{titulo}</div>
                {f'<div class="section-subtitle">{subtitulo}</div>' if subtitulo else ''}
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


# =========================================================
# 3. MÉTRICAS DE USO DE APP
# =========================================================
try:
    df = obtener_datos_app()
    df['Fecha_Vencimiento'] = pd.to_datetime(df['Fecha_Vencimiento'], errors='coerce')
    ahora = datetime.now()
    condiciones_no_null = df['Acepta_condiciones'].notnull() & (df['Acepta_condiciones'] != '')

    v_clientes_vigentes = df[df['Fecha_Vencimiento'] > ahora]['Cve_Cliente'].nunique()
    v_clientes_app_new = df[df['AceptaApp'] == 'S']['Cve_Cliente'].nunique()
    v_clientes_app_mudaron = df[(df['AceptaApp'] == 'S') & condiciones_no_null]['Cve_Cliente'].nunique()
    v_cliente_nyeva_app = v_clientes_app_new - v_clientes_app_mudaron
    v_cliente_app_viejita = df[condiciones_no_null]['Cve_Cliente'].nunique()
    v_total_app = v_cliente_nyeva_app + v_cliente_app_viejita
    v_porcentaje = (v_total_app / v_clientes_vigentes * 100) if v_clientes_vigentes > 0 else 0.0

    render_section_header("grid_view", "Uso de Aplicación Móvil", "Métricas de adopción y migración de clientes")
    cols = st.columns(7)

    metricas = [
        {"icon": "group", "titulo": "TOTAL CLUB", "val": f"{v_clientes_vigentes:,}".replace(",", "."), "label": "Clientes activos", "badge": "▲ Vigentes"},
        {"icon": "smartphone", "titulo": "NUEVA APP", "val": f"{v_clientes_app_new:,}".replace(",", "."), "label": "Descargaron la nueva", "badge": None},
        {"icon": "sync", "titulo": "MUDARON", "val": f"{v_clientes_app_mudaron:,}".replace(",", "."), "label": "Migraron a nueva", "badge": None},
        {"icon": "devices", "titulo": "APP ANTERIOR", "val": f"{v_cliente_app_viejita:,}".replace(",", "."), "label": "Siguen en app web", "badge": None},
        {"icon": "check_circle", "titulo": "CON NUEVA APP", "val": f"{v_cliente_nyeva_app:,}".replace(",", "."), "label": "Primera descarga", "badge": None},
        {"icon": "star", "titulo": "TOTAL APP", "val": f"{v_total_app:,}".replace(",", "."), "label": "Tienen la app", "badge": None},
        {"icon": "bar_chart", "titulo": "ADOPCIÓN", "val": f"{v_porcentaje:.2f}%", "label": "Del total de clientes", "badge": None}
    ]

    for col, m in zip(cols, metricas):
        with col:
            render_kpi_card(m["icon"], m["titulo"], m["val"], m["label"], m["badge"])

except Exception as e:
    st.error(f"Error procesando métricas de uso de App: {e}")

# =========================================================
# 4. RESUMEN POR CLUSTER 
# =========================================================
st.divider()
render_section_header("analytics", "Resumen por Cluster", "Comparativa YTD de ventas y márgenes por agrupación")

if "consulta_lista" not in st.session_state:
    st.session_state.consulta_lista = False

try:
    catalogos = obtener_catalogos_filtros()
    anios_disponibles = obtener_anios_disponibles()

    #st.markdown('<div class="filter-panel-card">', unsafe_allow_html=True)
    
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    
    with f_col1:
        st.markdown('**Selección de Clusters** <span class="filter-badge-req">Obligatorio</span>', unsafe_allow_html=True)
        f_clusters = st.multiselect(
            label="Clusters",
            options=catalogos['nombre_cluster'],
            default=st.session_state.get('sel_clusters', []),
            placeholder="Selecciona uno o varios clusters...",
            label_visibility="collapsed"
        )

    with f_col2:
        st.markdown('**Año de Análisis** <span class="filter-badge-req">Obligatorio</span>', unsafe_allow_html=True)
        f_anio = st.selectbox(
            label="Año",
            options=anios_disponibles,
            index=0 if anios_disponibles else 0,
            label_visibility="collapsed"
        )

    with f_col3:
        st.markdown('**Mes Corte (YTD)** <span class="filter-badge-req">Obligatorio</span>', unsafe_allow_html=True)
        mes_actual_num = datetime.now().month
        f_mes = st.selectbox(
            label="Mes",
            options=list(DICC_MESES.keys()),
            format_func=lambda x: DICC_MESES[x],
            index=mes_actual_num - 1,
            label_visibility="collapsed"
        )

    st.write("")

    with st.expander("🛠️ Filtros de Segmentación Adicionales", expanded=False):
        fa_col1, fa_col2, fa_col3 = st.columns(3)
        
        with fa_col1:
            st.markdown('**Categoría** <span class="filter-badge-opt">Opcional</span>', unsafe_allow_html=True)
            f_categoria = st.selectbox("Categoría", ["Todas"] + catalogos['Categoria'], label_visibility="collapsed")
            
            st.markdown('<div style="margin-top: 10px;"><b>Nombre Sucursal</b> <span class="filter-badge-opt">Opcional</span></div>', unsafe_allow_html=True)
            f_sucursal = st.selectbox("Sucursal", ["Todas"] + catalogos['sucursal'], label_visibility="collapsed")

        with fa_col2:
            st.markdown('**Nombre Cliente** <span class="filter-badge-opt">Opcional</span>', unsafe_allow_html=True)
            f_cliente = st.selectbox("Cliente", ["Todas"] + catalogos['Nombre'], label_visibility="collapsed")
            
            st.markdown('<div style="margin-top: 10px;"><b>Nombre Proveedor</b> <span class="filter-badge-opt">Opcional</span></div>', unsafe_allow_html=True)
            f_proveedor = st.selectbox("Proveedor", ["Todas"] + catalogos['Proveedor'], label_visibility="collapsed")

        with fa_col3:
            st.markdown('**No. Tarjeta** <span class="filter-badge-opt">Opcional</span>', unsafe_allow_html=True)
            f_no_tarjeta = st.selectbox("Tarjeta", ["Todas"] + catalogos['NoTarjeta'], label_visibility="collapsed")

    st.write("")

    btn_consultar = st.button("Consultar", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if btn_consultar:
        if not f_clusters:
            st.warning("⚠️ Selecciona al menos un **Cluster** para poder consultar.")
        else:
            st.session_state.sel_clusters = f_clusters
            st.session_state.sel_anio = int(f_anio)
            st.session_state.sel_mes = int(f_mes)
            st.session_state.filtros_extra = {
                'categoria': f_categoria,
                'cliente': f_cliente,
                'sucursal': f_sucursal,
                'proveedor': f_proveedor,
                'no_tarjeta': f_no_tarjeta
            }
            st.session_state.consulta_lista = True

    if not st.session_state.consulta_lista:
        st.info("Elige el cluster, año y mes de corte en el panel superior, luego presiona **Consultar**.")
    else:
        clusters_sel = st.session_state.sel_clusters
        anio_sel = st.session_state.sel_anio
        mes_sel = st.session_state.sel_mes
        filtros_extra = st.session_state.filtros_extra

        with st.spinner("Consultando datos YTD del cluster..."):
            df_raw = obtener_resumen_cluster_anio_sql(clusters_sel, anio_sel, mes_sel, filtros_extra)

        if df_raw.empty:
            st.info("No se encontraron registros para los filtros seleccionados.")
        else:
            df_act = df_raw[df_raw['Periodo'] == 'Actual'].set_index('nombre_cluster')
            df_ant = df_raw[df_raw['Periodo'] == 'Anterior'].set_index('nombre_cluster')

            clusters = df_raw['nombre_cluster'].unique()
            filas = []

            for c in clusters:
                vta_act = df_act.loc[c, 'Importe_Neto'] if c in df_act.index else 0.0
                vta_ant = df_ant.loc[c, 'Importe_Neto'] if c in df_ant.index else 0.0
                abono_act = df_act.loc[c, 'Importe_Club'] if c in df_act.index else 0.0
                abono_ant = df_ant.loc[c, 'Importe_Club'] if c in df_ant.index else 0.0
                costo_act = df_act.loc[c, 'Costo_Promedio'] if c in df_act.index else 0.0

                tarjetas = df_act.loc[c, 'Tarjetas_Activas'] if c in df_act.index else 0
                app_web = df_act.loc[c, 'Clientes_App_Web'] if c in df_act.index else 0
                skus = df_act.loc[c, 'Num_SKU'] if c in df_act.index else 0

                vta_var = ((vta_act - vta_ant) / vta_ant) if vta_ant else 0.0
                abono_var = ((abono_act - abono_ant) / abono_ant) if abono_ant else 0.0
                pct_bonif = (abono_act / vta_act) if vta_act else 0.0
                
                m_frontal = ((vta_act - costo_act) / vta_act) if vta_act else 0.0
                m_frontal_bonif = ((vta_act - costo_act - abono_act) / vta_act) if vta_act else 0.0

                filas.append({
                    'Nombre Cluster': c,
                    'Tarjetas Activas': tarjetas,
                    'Clientes App Web': app_web,
                    '#SKU': skus,
                    'VTA Actual': vta_act,
                    'VTA AA': vta_ant,
                    'VTA VAR': vta_var,
                    'Abono Actual': abono_act,
                    'Abono AA': abono_ant,
                    'Abono VAR': abono_var,
                    'Porcentaje de Bonificación': pct_bonif,
                    'Margen Frontal': m_frontal,
                    'Margen Frontal C/ Bonificación': m_frontal_bonif,
                    '_costo_act': costo_act
                })

            resumen = pd.DataFrame(filas)

            total_vta_act = resumen['VTA Actual'].sum()
            total_vta_aa = resumen['VTA AA'].sum()
            total_abono_act = resumen['Abono Actual'].sum()
            total_abono_aa = resumen['Abono AA'].sum()
            total_costo_act = resumen['_costo_act'].sum()
            var_vta_total = ((total_vta_act - total_vta_aa) / total_vta_aa) if total_vta_aa else 0.0
            margen_promedio = ((total_vta_act - total_costo_act) / total_vta_act) if total_vta_act else 0.0

            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                render_kpi_card("payments", f"Venta {anio_sel} ({DICC_MESES[mes_sel][:3]}-{DICC_MESES[mes_sel][:3]})", f"${total_vta_act:,.0f}", f"Comparativa vs {anio_sel-1}", delta=var_vta_total)
            with kpi_col2:
                render_kpi_card("history", f"Venta {anio_sel-1} ({DICC_MESES[mes_sel][:3]}-{DICC_MESES[mes_sel][:3]})", f"${total_vta_aa:,.0f}", f"Acumulado YTD {anio_sel-1}", delta=None)
            with kpi_col3:
                render_kpi_card("loyalty", "Abono Total", f"${total_abono_act:,.0f}", "Monto abonado a clientes", delta=None)
            with kpi_col4:
                render_kpi_card("trending_up", "Margen Frontal", f"{margen_promedio:.2%}", "Margen promedio global", delta=None)

            st.write("")

            resumen['Share Cliente'] = np.where(total_vta_act != 0, resumen['VTA Actual'] / total_vta_act, 0.0)

            fila_total = pd.DataFrame([{
                'Nombre Cluster': 'TOTAL',
                'Share Cliente': 1.0,
                'Tarjetas Activas': resumen['Tarjetas Activas'].sum(),
                'Clientes App Web': resumen['Clientes App Web'].sum(),
                '#SKU': df_raw[df_raw['Periodo'] == 'Actual']['Num_SKU'].sum(),
                'VTA Actual': total_vta_act,
                'VTA AA': total_vta_aa,
                'VTA VAR': var_vta_total,
                'Abono Actual': total_abono_act,
                'Abono AA': total_abono_aa,
                'Abono VAR': ((total_abono_act - total_abono_aa) / total_abono_aa) if total_abono_aa else 0.0,
                'Porcentaje de Bonificación': (total_abono_act / total_vta_act) if total_vta_act else 0.0,
                'Margen Frontal': margen_promedio,
                'Margen Frontal C/ Bonificación': ((total_vta_act - total_costo_act - total_abono_act) / total_vta_act) if total_vta_act else 0.0
            }])

            cols_order = [
                'Nombre Cluster', 'Share Cliente', 'Tarjetas Activas', 'Clientes App Web', '#SKU',
                'VTA Actual', 'VTA AA', 'VTA VAR', 'Abono Actual', 'Abono AA', 'Abono VAR',
                'Porcentaje de Bonificación', 'Margen Frontal', 'Margen Frontal C/ Bonificación'
            ]

            tabla_final = pd.concat([resumen[cols_order], fila_total[cols_order]], ignore_index=True)

            def resaltar_variacion(val):
                if isinstance(val, (int, float)):
                    if val > 0:
                        return 'color: #16a34a; font-weight: bold;'
                    elif val < 0:
                        return 'color: #dc2626; font-weight: bold;'
                return ''

            def resaltar_total(s):
                is_total = s['Nombre Cluster'] == 'TOTAL'
                return ['background-color: #f1f5f9; font-weight: bold; color: #334FB5;' if is_total else '' for _ in s]

            st.caption(f"Comparativa YTD ({DICC_MESES[mes_sel]} a {DICC_MESES[mes_sel]}) Año {anio_sel} vs. Año {anio_sel - 1} · {len(clusters)} cluster(s)")
            
            styler_df = tabla_final.style.format({
                'Share Cliente': '{:.2%}',
                'Tarjetas Activas': '{:,.0f}',
                'Clientes App Web': '{:,.0f}',
                '#SKU': '{:,.0f}',
                'VTA Actual': '${:,.1f}',
                'VTA AA': '${:,.1f}',
                'VTA VAR': '{:.2%}',
                'Abono Actual': '${:,.1f}',
                'Abono AA': '${:,.1f}',
                'Abono VAR': '{:.2%}',
                'Porcentaje de Bonificación': '{:.2%}',
                'Margen Frontal': '{:.2%}',
                'Margen Frontal C/ Bonificación': '{:.2%}'
            }).map(
                resaltar_variacion, subset=['VTA VAR', 'Abono VAR']
            ).apply(
                resaltar_total, axis=1
            ).bar(
                subset=['Share Cliente'], color='#dbeafe', vmin=0, vmax=1
            )

            col_tabla, col_grafica = st.columns([1.3, 1], gap="medium")

            with col_tabla:
                st.dataframe(
                    styler_df,
                    use_container_width=True,
                    hide_index=True,
                    height=480
                )

            with col_grafica:
                opcion_metrica = st.radio(
                    "Métrica a visualizar:",
                    options=["Ventas", "Abonos", "Margen Frontal"],
                    horizontal=True,
                    key="radio_metrica_grafica"
                )

                fig = go.Figure()

                if opcion_metrica == "Ventas":
                    fig.add_trace(go.Bar(
                        y=resumen['Nombre Cluster'],
                        x=resumen['VTA Actual'],
                        name=f'Venta {anio_sel}',
                        orientation='h',
                        marker=dict(color='#FF5100'),
                        text=resumen['VTA Actual'],
                        texttemplate='$%{x:,.0f}',
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Venta Actual: $%{x:,.2f}<extra></extra>'
                    ))
                    fig.add_trace(go.Bar(
                        y=resumen['Nombre Cluster'],
                        x=resumen['VTA AA'],
                        name=f'Venta {anio_sel-1}',
                        orientation='h',
                        marker=dict(color='#334FB5'),
                        text=resumen['VTA AA'],
                        texttemplate='$%{x:,.0f}',
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Venta AA: $%{x:,.2f}<extra></extra>'
                    ))
                    titulo_graf = f"Venta Actual ({anio_sel}) vs Año Anterior ({anio_sel-1}) por Cluster"
                    formato_eje = "$,.0f"

                elif opcion_metrica == "Abonos":
                    fig.add_trace(go.Bar(
                        y=resumen['Nombre Cluster'],
                        x=resumen['Abono Actual'],
                        name=f'Abono {anio_sel}',
                        orientation='h',
                        marker=dict(color='#16a34a'),
                        text=resumen['Abono Actual'],
                        texttemplate='$%{x:,.0f}',
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Abono Actual: $%{x:,.2f}<extra></extra>'
                    ))
                    fig.add_trace(go.Bar(
                        y=resumen['Nombre Cluster'],
                        x=resumen['Abono AA'],
                        name=f'Abono {anio_sel-1}',
                        orientation='h',
                        marker=dict(color='#0284c7'),
                        text=resumen['Abono AA'],
                        texttemplate='$%{x:,.0f}',
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Abono AA: $%{x:,.2f}<extra></extra>'
                    ))
                    titulo_graf = "Abonos YTD por Cluster"
                    formato_eje = "$,.0f"

                else:  # Margen Frontal
                    fig.add_trace(go.Bar(
                        y=resumen['Nombre Cluster'],
                        x=resumen['Margen Frontal'],
                        name='Margen Frontal',
                        orientation='h',
                        marker=dict(color='#8b5cf6'),
                        text=resumen['Margen Frontal'],
                        texttemplate='%{x:.2%}',
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Margen Frontal: %{x:.2%}<extra></extra>'
                    ))
                    titulo_graf = "Margen Frontal por Cluster"
                    formato_eje = ".0%"

                fig.update_layout(
                    title=dict(
                        text=f"<b>{titulo_graf}</b>",
                        font=dict(size=14, color='#334FB5')
                    ),
                    barmode='group',
                    xaxis=dict(tickformat=formato_eje),
                    yaxis=dict(autorange="reversed"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    template="plotly_white",
                    height=420,
                    margin=dict(l=10, r=10, t=30, b=10)
                )

                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error procesando el panel de resumen: {e}")

st.divider()
render_section_header("storefront", "Resumen por Proveedor", "Análisis acumulado YTD de ventas y márgenes por marcas/proveedores")

try:
    if not st.session_state.get("consulta_lista"):
        st.info("Aplica los filtros de arriba (cluster + año + mes) para ver este resumen.")
    else:
        clusters_sel = st.session_state.sel_clusters
        anio_sel = st.session_state.sel_anio
        mes_sel = st.session_state.sel_mes
        filtros_extra = st.session_state.filtros_extra

        with st.spinner("Consultando proveedores del cluster seleccionado..."):
            df_prov_raw = obtener_resumen_proveedor_anio_sql(clusters_sel, anio_sel, mes_sel, filtros_extra)

        if df_prov_raw.empty:
            st.info("No se encontraron registros de proveedores para los filtros y clusters seleccionados.")
        else:
            tabla_prov = construir_tabla_proveedor(df_prov_raw)

            tot_vta_act = tabla_prov['VTA Actual'].sum()
            tot_vta_aa = tabla_prov['VTA AA'].sum()
            var_vta = ((tot_vta_act - tot_vta_aa) / tot_vta_aa) if tot_vta_aa else 0.0

            pkpi1, pkpi2, pkpi3 = st.columns(3)
            with pkpi1:
                render_kpi_card("storefront", "Proveedores Activos", f"{len(tabla_prov):,}", "Asociados al cluster", delta=None)
            with pkpi2:
                render_kpi_card("point_of_sale", f"Venta YTD {anio_sel}", f"${tot_vta_act:,.1f}", f"Variación vs {anio_sel-1}", delta=var_vta)
            with pkpi3:
                render_kpi_card("event_repeat", f"Venta YTD {anio_sel-1}", f"${tot_vta_aa:,.1f}", f"Acumulado YTD {anio_sel-1}", delta=None)

            st.write("")

            st.caption(f"Proveedores asociados al cluster: **{', '.join(clusters_sel)}** ({DICC_MESES[mes_sel]} a {DICC_MESES[mes_sel]} {anio_sel} vs. {anio_sel - 1})")
            
            p_col_tabla, p_col_grafica = st.columns([1.3, 1], gap="medium")

            with p_col_tabla:
                st.dataframe(
                    tabla_prov.style.format({
                        'VTA Actual': '${:,.1f}',
                        'VTA AA': '${:,.1f}',
                        'Margen Frontal': '{:.2%}',
                        'Margen Frontal C/ Bonificación': '{:.2%}'
                    }).bar(
                        subset=['VTA Actual'], color='#dbeafe'
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=480
                )

            with p_col_grafica:
                top_n = st.slider("Mostrar Top Proveedores por Venta:", 5, 20, 10, key="slider_top_prov")
                
                opcion_prov = st.radio(
                    "Métrica a visualizar:",
                    options=["VTA Actual", "Margen Frontal", "Margen Frontal C/ Bonificación"],
                    horizontal=True,
                    key="radio_proveedor_metricas"
                )

                
                df_top_prov = tabla_prov.nlargest(top_n, 'VTA Actual')

                fig_prov = go.Figure()

                if opcion_prov == "VTA Actual":
                    col_metrica = 'VTA Actual'
                    color_bar = '#FF5100'
                    text_tmpl = '$%{x:,.0f}'
                    hover_tmpl = '<b>%{y}</b><br>Venta Actual: $%{x:,.2f}<extra></extra>'
                    tick_fmt = "$,.0f"
                    x_range = None
                elif opcion_prov == "Margen Frontal":
                    col_metrica = 'Margen Frontal'
                    color_bar = '#8b5cf6'
                    text_tmpl = '%{x:.2%}'
                    hover_tmpl = '<b>%{y}</b><br>Margen Frontal: %{x:.2%}<extra></extra>'
                    tick_fmt = ".0%"
                    x_range = [-0.5, 0.5]
                else:  
                    col_metrica = 'Margen Frontal C/ Bonificación'
                    color_bar = '#ec4899'
                    text_tmpl = '%{x:.2%}'
                    hover_tmpl = '<b>%{y}</b><br>Margen Frontal C/ Bonif.: %{x:.2%}<extra></extra>'
                    tick_fmt = ".0%"
                    x_range = [-0.5, 0.5]

                fig_prov.add_trace(go.Bar(
                    y=df_top_prov['Nombres Proveedor.'],
                    x=df_top_prov[col_metrica],
                    name=opcion_prov,
                    orientation='h',
                    marker=dict(color=color_bar),
                    text=df_top_prov[col_metrica],
                    texttemplate=text_tmpl,
                    textposition='outside',
                    hovertemplate=hover_tmpl
                ))

                layout_axis_x = dict(tickformat=tick_fmt)
                if x_range is not None:
                    layout_axis_x['range'] = x_range

                fig_prov.update_layout(
                    title=dict(text=f"<b>Top {top_n} Proveedores por Venta ({opcion_prov})</b>", font=dict(size=13, color='#334FB5')),
                    xaxis=layout_axis_x,
                    yaxis=dict(autorange="reversed"),
                    template="plotly_white",
                    height=480,
                    margin=dict(l=10, r=30, t=40, b=10)
                )

                st.plotly_chart(fig_prov, use_container_width=True)

except Exception as e:
    st.error(f"Error procesando el panel de proveedores: {e}")
# =========================================================
# 6. COMPARATIVA DE CRECIMIENTO: APP WEB VS APP MÓVIL
# =========================================================
st.divider()
try:
    render_section_header("stacked_line_chart", "App Ahorro GB: Web vs Móvil", "Comportamiento de aceptaciones de condiciones")
    
    df_crecimiento = obtener_crecimiento_adopcion()

    if df_crecimiento.empty:
        st.info("No hay datos históricos disponibles.")
    else:
        tipo_vista = st.radio(
            "Visualización:",
            options=["Mensual", "Acumulado"],
            horizontal=True,
            key="radio_vista_adopcion"
        )

        df_crecimiento['Acumulado_Web'] = df_crecimiento['Registros_Web'].cumsum()
        df_crecimiento['Acumulado_Movil'] = df_crecimiento['Registros_Movil'].cumsum()

        col_web = 'Registros_Web' if "Mensual" in tipo_vista else 'Acumulado_Web'
        col_movil = 'Registros_Movil' if "Mensual" in tipo_vista else 'Acumulado_Movil'

        fig_crecimiento = go.Figure()

        # App Web
        fig_crecimiento.add_trace(go.Scatter(
            x=df_crecimiento['Mes'],
            y=df_crecimiento[col_web],
            mode='lines+markers+text',
            name='App Web',
            text=df_crecimiento[col_web],
            textposition="top center",
            line=dict(color='#10b981', width=3),  
            marker=dict(size=8),
            hovertemplate='<b>Mes:</b> %{x}<br><b>Web:</b> %{y:,.0f}<extra></extra>'
        ))

        # App Móvil
        fig_crecimiento.add_trace(go.Scatter(
            x=df_crecimiento['Mes'],
            y=df_crecimiento[col_movil],
            mode='lines+markers+text',
            name='App Móvil',
            text=df_crecimiento[col_movil],
            textposition="bottom center",
            line=dict(color='#FF5100', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Mes:</b> %{x}<br><b>Móvil:</b> %{y:,.0f}<extra></extra>'
        ))

        fig_crecimiento.update_layout(
            title=dict(
                text=f"<b>Aceptaciones {tipo_vista} por Plataforma</b>",
                font=dict(size=14, color='#334FB5')
            ),
            xaxis=dict(title="Mes / Año", type='category'),
            yaxis=dict(title="Cantidad de Usuarios"),
            template="plotly_white",
            height=420,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_crecimiento, use_container_width=True)

except Exception as e:
    st.error(f"Error cargando la comparativa de adopción: {e}")