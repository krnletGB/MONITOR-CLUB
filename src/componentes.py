import html
import streamlit as st

# =========================================================
# AQUI COLOCO TODO LO REALACIONADO A COMPONENTES DE ESTILO 
# =========================================================

def marca_sidebar() -> None:
    contenido = (
        '<div class="marca-sidebar">'
        '<div class="marca-sidebar-titulo">'
        '▣ &nbsp; CLIENTES CLUB'
        '</div>'
        '<div class="marca-sidebar-subtitulo">'
        'Inteligencia comercial'
        '</div>'
        '</div>'
    )

    st.sidebar.markdown(
        contenido,
        unsafe_allow_html=True,
    )


def encabezado_pagina(
    titulo: str,
    subtitulo: str,
) -> None:
    contenido = (
        '<div class="encabezado-pagina">'
        '<div class="encabezado-punto"></div>'
        '<div>'
        '<div class="titulo-principal">'
        f'{html.escape(titulo)}'
        '</div>'
        '<div class="titulo-secundario">'
        f'{html.escape(subtitulo)}'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        contenido,
        unsafe_allow_html=True,
    )


def titulo_bloque(
    titulo: str,
    subtitulo: str = "",
    icono: str = "",
) -> None:
    icono_html = ""

    if icono:
        icono_html = (
            '<span class="titulo-bloque-icono">'
            f'{html.escape(icono)}'
            '</span>'
        )

    contenido = (
        '<div class="cabecera-bloque">'
        '<div class="titulo-bloque">'
        f'{icono_html}'
        f'{html.escape(titulo)}'
        '</div>'
        '<div class="subtitulo-bloque">'
        f'{html.escape(subtitulo)}'
        '</div>'
        '</div>'
    )

    st.markdown(
        contenido,
        unsafe_allow_html=True,
    )


def tarjeta_kpi(
    titulo: str,
    valor: str,
    subtitulo: str = "",
    icono: str = "•",
    color: str = "rosa",
    variacion: float | None = None,
    texto_variacion: str = "vs año anterior",
    sufijo_variacion: str = "%",
) -> None:
    variacion_html = ""

    if variacion is not None:

        positivo = variacion >= 0

        color = "verde" if positivo else "rojo"

        flecha = "▲" if positivo else "▼"

        st.markdown(
            f"""
            <div class="kpi-variacion {color}">
                {flecha} {abs(variacion):.1%}
                <span>vs año anterior</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    contenido = (
        '<div class="kpi-card">'
        '<div class="kpi-fila-superior">'
        f'<div class="kpi-icono {html.escape(color)}">'
        f'{html.escape(icono)}'
        '</div>'
        '<div class="kpi-contenido">'
        '<div class="kpi-titulo">'
        f'{html.escape(titulo)}'
        '</div>'
        '<div class="kpi-valor">'
        f'{html.escape(valor)}'
        '</div>'
        '<div class="kpi-subtitulo">'
        f'{html.escape(subtitulo)}'
        '</div>'
        '</div>'
        '</div>'
        f'{variacion_html}'
        '</div>'
    )

    st.markdown(
        contenido,
        unsafe_allow_html=True,
    )


def tarjeta_insight(
    texto: str,
    titulo: str = "Insight del periodo",
) -> None:
    contenido = (
        '<div class="insight-card">'
        '<div class="insight-icono">✦</div>'
        '<div>'
        '<div class="insight-titulo">'
        f'{html.escape(titulo)}'
        '</div>'
        '<div class="insight-texto">'
        f'{html.escape(texto)}'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        contenido,
        unsafe_allow_html=True,
    )

def tarjeta_kpi_principal(
    titulo: str,
    valor: str,
    subtitulo: str,
    icono: str,
    color: str = "rosa",
    variacion: float | None = None,
) -> None:
    variacion_html = ""

    if variacion is not None:
        es_positiva = variacion >= 0
        clase = "positivo" if es_positiva else "negativo"
        flecha = "▲" if es_positiva else "▼"

        variacion_html = (
            '<div class="kpi-principal-variacion">'
            f'<span class="{clase}">'
            f'{flecha} {abs(variacion):.1%}'
            '</span>'
            '<span class="kpi-variacion-texto">'
            'vs año anterior'
            '</span>'
            '</div>'
        )

    contenido = (
        '<div class="kpi-principal-card">'
        f'<div class="kpi-principal-icono {html.escape(color)}">'
        f'{html.escape(icono)}'
        '</div>'
        '<div class="kpi-principal-contenido">'
        '<div class="kpi-principal-titulo">'
        f'{html.escape(titulo)}'
        '</div>'
        '<div class="kpi-principal-valor">'
        f'{html.escape(valor)}'
        '</div>'
        '<div class="kpi-principal-subtitulo">'
        f'{html.escape(subtitulo)}'
        '</div>'
        f'{variacion_html}'
        '</div>'
        '</div>'
    )

    st.markdown(
        contenido,
        unsafe_allow_html=True,
    )


def tarjeta_kpi_secundaria(
    titulo: str,
    valor: str,
    subtitulo: str,
    icono: str,
    color: str = "rosa",
    variacion: float | None = None,
    variacion_pp: bool = False,
) -> None:
    variacion_html = ""

    if variacion is not None:
        es_positiva = variacion >= 0
        clase = "positivo" if es_positiva else "negativo"
        flecha = "▲" if es_positiva else "▼"

        if variacion_pp:
            texto_valor = f"{abs(variacion):.2f} pp"
        else:
            texto_valor = f"{abs(variacion):.1%}"

        variacion_html = (
            '<div class="kpi-secundaria-variacion">'
            f'<span class="{clase}">'
            f'{flecha} {texto_valor}'
            '</span>'
            '<span class="kpi-variacion-texto">'
            'vs año anterior'
            '</span>'
            '</div>'
        )

    contenido = (
        '<div class="kpi-secundaria-card">'
        f'<div class="kpi-secundaria-icono {html.escape(color)}">'
        f'{html.escape(icono)}'
        '</div>'
        '<div class="kpi-secundaria-contenido">'
        '<div class="kpi-secundaria-titulo">'
        f'{html.escape(titulo)}'
        '</div>'
        '<div class="kpi-secundaria-valor">'
        f'{html.escape(valor)}'
        '</div>'
        '<div class="kpi-secundaria-subtitulo">'
        f'{html.escape(subtitulo)}'
        '</div>'
        f'{variacion_html}'
        '</div>'
        '</div>'
    )

    st.markdown(
        contenido,
        unsafe_allow_html=True,
    )

def tarjeta_kpi_doble(
    titulo: str,
    titulo_izquierdo: str,
    valor_izquierdo: str,
    titulo_derecho: str,
    valor_derecho: str,
    subtitulo: str,
    icono: str = "↔",
    color: str = "azul",
) -> None:
    contenido = (
        '<div class="kpi-doble-card">'
        f'<div class="kpi-doble-icono {html.escape(color)}">'
        f'{html.escape(icono)}'
        '</div>'
        '<div class="kpi-doble-contenido">'
        '<div class="kpi-doble-titulo-general">'
        f'{html.escape(titulo)}'
        '</div>'
        '<div class="kpi-doble-metricas">'
        '<div class="kpi-doble-metrica">'
        '<div class="kpi-doble-etiqueta">'
        f'{html.escape(titulo_izquierdo)}'
        '</div>'
        '<div class="kpi-doble-valor">'
        f'{html.escape(valor_izquierdo)}'
        '</div>'
        '</div>'
        '<div class="kpi-doble-separador"></div>'
        '<div class="kpi-doble-metrica">'
        '<div class="kpi-doble-etiqueta">'
        f'{html.escape(titulo_derecho)}'
        '</div>'
        '<div class="kpi-doble-valor">'
        f'{html.escape(valor_derecho)}'
        '</div>'
        '</div>'
        '</div>'
        '<div class="kpi-doble-subtitulo">'
        f'{html.escape(subtitulo)}'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        contenido,
        unsafe_allow_html=True,
    )   