import streamlit as st
from estilos import aplicar_estilos
from src.componentes import marca_sidebar
st.set_page_config(
    page_title="Clientes Club",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilos()
with st.sidebar:
    marca_sidebar()


pagina_sucursal = st.Page(
    "pages/1_Sucursal.py",
    title="Resumen sucursal",
    icon=":material/store:",
    default=True,
)

pagina_cliente = st.Page(
    "pages/2_Cliente.py",
    title="Cliente",
    icon=":material/store:",
    
)


pagina_app = st.Page(
    "pages/3_App.py",
    title="App",
    icon=":material/store:",
    
)

pagina_resumen_mes = st.Page(
    "pages/4_Resumen_Mes.py",
    title="Resumen Mes",
    icon=":material/store:",
    
)

pagina_renovaciones = st.Page(
    "pages/5_Renovaciones.py",
    title="Renovaciones",
    icon=":material/store:",
    
)


navegacion = st.navigation(
    {
        "": [
            pagina_sucursal,
            pagina_cliente,
            pagina_app,
            pagina_resumen_mes,
            pagina_renovaciones
        ],
    }
)

navegacion.run()