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
marca_sidebar()


pagina_sucursal = st.Page(
    "pages/1_Sucursal.py",
    title="Resumen sucursal",
    icon=":material/store:",
    default=True,
)

navegacion = st.navigation(
    {
        "Inteligencia comercial": [
            pagina_sucursal,
        ],
    }
)

navegacion.run()