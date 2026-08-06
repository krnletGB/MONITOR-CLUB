import streamlit as st


def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        :root {
            --rosa-principal: #FF5100;
            --rosa-oscuro: #CC4706; 
            --rosa-claro: #F5905F;
            --rosa-borde: #FF5100;

            --azul-texto: #102342;
            --azul-secundario: #53627a;

            --verde: #19a44a;
            --rojo: #dc3545;

            --fondo: #f6f8fc;
            --blanco: #ffffff;
            --borde: #e7ebf2;
            --sombra: 0 10px 30px rgba(31, 44, 74, 0.08);
        }

        html,
        body,
        [class*="css"] {
            font-family:
                Inter,
                "Segoe UI",
                Arial,
                sans-serif;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 90% 0%,
                    rgba(255, 225, 237, 0.42),
                    transparent 25%
                ),
                linear-gradient(
                    180deg,
                    #f9faff 0%,
                    var(--fondo) 100%
                );
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stDecoration"] {
            display: none;
        }

        .block-container {
            max-width: 1720px;
            padding-top: 1.25rem;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-bottom: 3rem;
        }

        /* ==================================================
           SIDEBAR
        ================================================== */

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #CC4706 0%,
                    #FF631C 50%,
                    #ff5100 100%
                );
            border-right: none;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }

        [data-testid="stSidebar"] * {
            color: white;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 0.4rem;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 12px;
            margin: 0.22rem 0.55rem;
            padding: 0.62rem 0.85rem;
            transition: 0.18s ease;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: rgba(255, 255, 255, 0.13);
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: rgba(255, 255, 255, 0.19);
            box-shadow:
                inset 0 0 0 1px rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebarNav"] span {
            font-weight: 700;
        }

        .marca-sidebar {
            padding: 1rem 1rem 1.35rem 1rem;
            border-bottom:
                1px solid rgba(255, 255, 255, 0.17);
            margin-bottom: 0.8rem;
        }

        .marca-sidebar-titulo {
            font-size: 1.05rem;
            font-weight: 850;
            letter-spacing: 0.02rem;
        }

        .marca-sidebar-subtitulo {
            font-size: 0.76rem;
            opacity: 0.82;
            margin-top: 0.18rem;
        }

        /* ==================================================
           TÍTULOS
        ================================================== */

        .encabezado-pagina {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.15rem 0 1.25rem 0;
        }

        .encabezado-punto {
            width: 13px;
            height: 13px;
            flex: 0 0 13px;
            border-radius: 999px;
            background:
                linear-gradient(
                    135deg,
                    #ff4fa0,
                    #FF5100
                );
            box-shadow:
                0 0 0 7px rgba(212, 20, 110, 0.08);
        }

        .titulo-principal {
            color: var(--azul-texto);
            font-size: 2rem;
            line-height: 1.05;
            font-weight: 900;
            letter-spacing: -0.045rem;
        }

        .titulo-secundario {
            color: var(--azul-secundario);
            font-size: 0.95rem;
            margin-top: 0.35rem;
        }

        .titulo-bloque {
            color: var(--azul-texto);
            font-size: 1.03rem;
            line-height: 1.2;
            font-weight: 850;
        }

        .subtitulo-bloque {
            color: #7a8597;
            font-size: 0.77rem;
            margin-top: 0.18rem;
        }

        /* ==================================================
           CONTENEDORES
        ================================================== */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--borde);
            border-radius: 17px;
            box-shadow: var(--sombra);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
        > div {
            padding-top: 0.25rem;
        }

        .separador-suave {
            height: 1px;
            margin: 0.65rem 0 0.85rem 0;
            background: #edf0f5;
        }

        /* ==================================================
           FILTROS
        ================================================== */

        div[data-testid="stSelectbox"] label,
        div[data-testid="stMultiSelect"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stDateInput"] label {
            color: var(--azul-texto) !important;
            font-size: 0.75rem !important;
            font-weight: 750 !important;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stDateInput"] input {
            min-height: 42px;
            border-radius: 9px !important;
            border-color: #dde3ec !important;
            background: #ffffff !important;
            color: var(--azul-texto) !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #a1a9b7;
        }

        div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stDateInput"] input:focus {
            border-color: #ed5b9b !important;
            box-shadow:
                0 0 0 3px rgba(212, 20, 110, 0.09)
                !important;
        }

        div[data-testid="stExpander"] {
            background: white;
            border: 1px solid var(--borde);
            border-radius: 16px;
            box-shadow: var(--sombra);
        }

        div[data-testid="stExpander"] summary {
            color: var(--azul-texto);
            font-weight: 800;
        }

        /* ==================================================
           BOTONES
        ================================================== */

        div.stButton > button {
            width: 100%;
            min-height: 42px;
            border-radius: 10px;
            border: 1px solid #f184b4;
            background: white;
            color: var(--rosa-principal);
            font-weight: 800;
            transition: 0.18s ease;
        }

        div.stButton > button:hover {
            background: var(--rosa-principal);
            color: white;
            border-color: var(--rosa-principal);
            transform: translateY(-1px);
        }

        /* ==================================================
           KPI
        ================================================== */

        .kpi-card {
            min-height: 150px;
            height: 100%;
            padding: 1.05rem 1rem 0.9rem 1rem;
            border-radius: 16px;
            border: 1px solid var(--borde);
            background:
                linear-gradient(
                    155deg,
                    #ffffff 0%,
                    #ffffff 72%,
                    #fbfcff 100%
                );
            box-shadow: var(--sombra);
            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow:
                0 15px 34px rgba(31, 44, 74, 0.13);
        }

        .kpi-fila-superior {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .kpi-icono {
            width: 47px;
            height: 47px;
            flex: 0 0 47px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.3rem;
            font-weight: 800;
            box-shadow:
                0 8px 18px rgba(23, 38, 70, 0.14);
        }

        .kpi-icono.rosa {
            background:
                linear-gradient(
                    135deg,
                    #ff4d9b,
                    #e80b68
                );
        }

        .kpi-icono.morado {
            background:
                linear-gradient(
                    135deg,
                    #9a66ff,
                    #6a32e6
                );
        }

        .kpi-icono.verde {
            background:
                linear-gradient(
                    135deg,
                    #67d66f,
                    #28a845
                );
        }

        .kpi-icono.azul {
            background:
                linear-gradient(
                    135deg,
                    #5f9cff,
                    #1668e9
                );
        }

        .kpi-icono.naranja {
            background:
                linear-gradient(
                    135deg,
                    #ffae54,
                    #f57400
                );
        }

        .kpi-icono.cian {
            background:
                linear-gradient(
                    135deg,
                    #43d8e7,
                    #02a6bb
                );
        }

        .kpi-titulo {
            color: #4b5870;
            font-size: 0.68rem;
            line-height: 1.2;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.025rem;
        }

        .kpi-valor {
            color: var(--azul-texto);
            font-size: 1.45rem;
            line-height: 1.2;
            font-weight: 900;
            margin-top: 0.26rem;
            white-space: nowrap;
        }

        .kpi-subtitulo {
            color: #8a94a5;
            font-size: 0.67rem;
            margin-top: 0.28rem;
        }

        .kpi-variacion {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            margin-top: 1.05rem;
            font-size: 0.69rem;
        }

        .kpi-variacion-valor {
            font-weight: 850;
        }

        .kpi-variacion-valor.positivo {
            color: var(--verde);
        }

        .kpi-variacion-valor.negativo {
            color: var(--rojo);
        }

        .kpi-variacion-texto {
            color: #788396;
        }

        /* ==================================================
           INSIGHT
        ================================================== */

        .insight-card {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1.1rem 1.25rem;
            border-radius: 16px;
            border: 1px solid var(--rosa-borde);
            background:
                linear-gradient(
                    100deg,
                    #fff8fb 0%,
                    #ffffff 74%
                );
            box-shadow:
                0 8px 24px rgba(212, 20, 110, 0.05);
        }

        .insight-icono {
            width: 50px;
            height: 50px;
            flex: 0 0 50px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.35rem;
            background:
                linear-gradient(
                    135deg,
                    #ff4d9b,
                    #e80b68
                );
        }

        .insight-titulo {
            color: var(--azul-texto);
            font-weight: 850;
            font-size: 0.9rem;
        }

        .insight-texto {
            color: #45546d;
            font-size: 0.78rem;
            line-height: 1.65;
            margin-top: 0.22rem;
        }

        /* ==================================================
           TABLAS
        ================================================== */

        div[data-testid="stDataFrame"] {
            border: none;
            border-radius: 10px;
            overflow: hidden;
        }

        div[data-testid="stDataFrame"] thead tr th {
            background: #fafbfe !important;
            color: #536079 !important;
            font-size: 0.7rem !important;
            font-weight: 850 !important;
            text-transform: uppercase;
            border-bottom:
                1px solid #e7ebf2 !important;
        }

        div[data-testid="stDataFrame"] tbody td {
            color: #223351 !important;
            border-bottom:
                1px solid #edf0f5 !important;
        }

        /* ==================================================
           PLOTLY
        ================================================== */

        div[data-testid="stPlotlyChart"] {
            border-radius: 12px;
            overflow: hidden;
        }

        /* ==================================================
           ALERTAS
        ================================================== */

        div[data-testid="stAlert"] {
            border-radius: 13px;
        }

        @media (max-width: 1100px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .titulo-principal {
                font-size: 1.65rem;
            }

            .kpi-card {
                min-height: 138px;
            }
        }
        .etiqueta-seccion {
            color: #79859a;
            font-size: 0.74rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .espacio-seccion {
            height: 0.65rem;
        }

        .espacio-insight {
            height: 1rem;
        }

        .espacio-seccion-grande {
            height: 1.15rem;
        }

        .insight-card {
            min-height: 82px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 0.25rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
        div[data-testid="stDataFrame"] {
            margin-top: 0.25rem;
        }

        @media (max-width: 1350px) {
            .kpi-card {
                min-height: 165px;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            .kpi-icono {
                width: 42px;
                height: 42px;
                flex-basis: 42px;
            }

            .kpi-valor {
                font-size: 1.25rem;
            }
        }

        /* ==================================================
        KPI PRINCIPALES IGUALES A TICKET PROMEDIO
        ================================================== */

        .kpi-principal-card {
            min-height: 108px;
            height: auto;

            display: flex;
            align-items: center;
            gap: 0.8rem;

            padding: 0.85rem 1rem;

            border: 1px solid #e5e9f1;
            border-radius: 14px;

            background: #ffffff;

            box-shadow:
                0 8px 20px rgba(31, 44, 74, 0.08);

            overflow: hidden;

            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease;
        }

        .kpi-principal-card:hover {
            transform: translateY(-2px);

            box-shadow:
                0 12px 26px rgba(31, 44, 74, 0.12);
        }

        /* Icono igual al de Ticket Promedio */
        .kpi-principal-icono {
            width: 60px !important;
            height: 60px !important;

            min-width: 60px !important;
            max-width: 60px !important;

            flex: 0 0 60px !important;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 16px;

            color: white;
            font-size: 1.4rem;
            font-weight: 900;

            background:
                linear-gradient(
                    135deg,
                    #0d338c,
                    #3157dd
                ) !important;

            box-shadow:
                0 8px 18px rgba(24, 40, 75, 0.16);
        }

        .kpi-principal-contenido {
            flex: 1;
            min-width: 0;
            width: auto;
        }

        /* Título igual al Ticket Promedio */
        .kpi-principal-titulo {
            color: #090373;
            font-size: 0.78rem;
            line-height: 1.1;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.02rem;

            margin: 0 0 0.3rem 0;
        }

        /* Valor principal */
        .kpi-principal-valor {
            color: #102342;
            font-size: 1.55rem;
            line-height: 1.05;
            font-weight: 900;

            margin: 0;

            white-space: nowrap;
        }

        /* Subtítulo */
        .kpi-principal-subtitulo {
            color: #8993a4;
            font-size: 0.66rem;
            line-height: 1.2;

            margin-top: 0.28rem;
        }

        /* Variación */
        .kpi-variacion{
                    margin-top:8px;
                    font-size:.72rem;
                    font-weight:700;
        
                }
        
                .kpi-variacion.verde{
                    color:#17a34a;
                }
        
                .kpi-variacion.rojo{
                    color:#e53935;
                }
        
                .kpi-variacion span{
                    color:#7b8798;
                    font-weight:500;
        
                }


        /*==================================================
        KPIs SECUNDARIOS
        ==================================================*/

        .kpi-secundaria-card{

            min-height:82px;

            display:flex;
            align-items:center;
            gap:.75rem;

            padding:.75rem .9rem;

            background:#fff;

            border:1px solid #e5e9f1;
            border-radius:14px;

            box-shadow:
                0 6px 16px rgba(31,44,74,.08);

            transition:
                transform .18s ease,
                box-shadow .18s ease;

        }

        .kpi-secundaria-card:hover{

            transform:translateY(-2px);

            box-shadow:
                0 10px 22px rgba(31,44,74,.12);

        }

        /* icono */

        .kpi-secundaria-icono{

            width:46px;
            height:46px;

            min-width:46px;
            max-width:46px;

            flex:0 0 46px;

            display:flex;
            align-items:center;
            justify-content:center;

            border-radius:14px;

            color:white;

            font-size:1.05rem;
            font-weight:900;

            background:
                linear-gradient(
                    135deg,
                    #0d338c,
                    #3157dd
                );

            box-shadow:
                0 6px 14px rgba(24,40,75,.14);

        }

        /* contenido */

        .kpi-secundaria-contenido{

            flex:1;

        }

        /* titulo */

        .kpi-secundaria-titulo{

            color:#5b6677;

            font-size:.64rem;

            font-weight:900;

            text-transform:uppercase;

            margin-bottom:.15rem;

        }

        /* valor */

        .kpi-secundaria-valor{

            color:#132647;

            font-size:1.12rem;

            font-weight:900;

            line-height:1;

        }

        /* subtitulo */

        .kpi-secundaria-subtitulo{

            color:#8a93a5;

            font-size:.63rem;

            margin-top:.18rem;

        }

        /* Variación */
                .kpi-variacion{
                            margin-top:8px;
                            font-size:.72rem;
                            font-weight:700;
                
                        }
                
                        .kpi-variacion.verde{
                            color:#17a34a;
                        }
                
                        .kpi-variacion.rojo{
                            color:#e53935;
                        }
                
                        .kpi-variacion span{
                            color:#7b8798;
                            font-weight:500;
                
                        }

        /* ==================================================
            KPI DOBLE: TICKET PROMEDIO
        ================================================== */

        .kpi-doble-card {
            min-height: 108px;
            height: auto;

            display: flex;
            align-items: center;
            gap: 0.8rem;

            padding: 0.85rem 1rem;

            border: 1px solid #e5e9f1;
            border-radius: 14px;

            background: #ffffff;

            box-shadow:
                0 8px 20px rgba(31, 44, 74, 0.08);

            overflow: hidden;
        }

        .kpi-doble-card:hover {
            transform: translateY(-2px);

            box-shadow:
                0 12px 26px rgba(31, 44, 74, 0.12);
        }

        /* Icono cuadrado, sin estirarse */
        .kpi-doble-icono {
            width: 60px !important;
            height: 60px !important;

            min-width: 60px !important;
            max-width: 60px !important;

            flex: 0 0 60px !important;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 16px;

            color: white;
            font-size: 1.4rem;
            font-weight: 900;

            background:
                linear-gradient(
                    135deg,
                    #0d338c,
                    #3157dd
                ) !important;

            box-shadow:
                0 8px 18px rgba(24, 40, 75, 0.16);
        }

        /* Contenido */
        .kpi-doble-contenido {
            flex: 1;
            min-width: 0;
            width: auto;
        }

        .kpi-doble-titulo-general {
            color: #090373;
            font-size: 0.78rem;
            line-height: 1.1;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.02rem;

            margin: 0 0 0.4rem 0;
        }

        /* Las dos métricas lado a lado */
        .kpi-doble-metricas {
            width: 100%;

            display: grid;
            grid-template-columns: 1fr 1px 1fr;
            align-items: center;
            gap: 0.75rem;
        }

        .kpi-doble-metrica {
            min-width: 0;
        }

        .kpi-doble-etiqueta {
            color: #526078;
            font-size: 0.61rem;
            line-height: 1.15;
            font-weight: 800;
            text-transform: uppercase;

            white-space: normal;
        }

        .kpi-doble-valor {
            color: #102342;
            font-size: 1.35rem;
            line-height: 1.05;
            font-weight: 900;

            margin-top: 0.18rem;

            white-space: nowrap;
        }

        .kpi-doble-separador {
            width: 1px;
            height: 34px;

            background: #e1e6ef;
        }

        .kpi-doble-subtitulo {
            color: #8993a4;
            font-size: 0.66rem;
            line-height: 1.2;

            margin-top: 0.4rem;
        }

        /* ==================================================
        COMPORTAMIENTO RESPONSIVO DE KPI
        ================================================== */

        .st-key-kpi_principales
        [data-testid="stHorizontalBlock"],
        .st-key-kpi_secundarios
        [data-testid="stHorizontalBlock"] {
            display: flex;
            flex-wrap: wrap;
            align-items: stretch;
        }

        /* Cada columna puede crecer y bajar de fila */
        .st-key-kpi_principales
        [data-testid="column"] {
            flex: 1 1 280px !important;
            min-width: 280px !important;
        }

        .st-key-kpi_secundarios
        [data-testid="column"] {
            flex: 1 1 220px !important;
            min-width: 220px !important;
        }

        /* Evita que los títulos se rompan letra por letra */
        .kpi-principal-titulo,
        .kpi-secundaria-titulo,
        .kpi-doble-titulo-general,
        .kpi-doble-etiqueta {
            word-break: normal;
            overflow-wrap: normal;
            white-space: normal;
        }

        /* Valores completos */
        .kpi-principal-valor,
        .kpi-secundaria-valor,
        .kpi-doble-valor {
            word-break: normal;
            overflow-wrap: normal;
            white-space: nowrap;
        }

        /* ==================================================
        TABLET
        ================================================== */

        @media screen and (max-width: 1250px) {
            .st-key-kpi_principales
            [data-testid="column"] {
                flex: 1 1 calc(50% - 1rem) !important;
                min-width: 320px !important;
            }

            .st-key-kpi_secundarios
            [data-testid="column"] {
                flex: 1 1 calc(33.333% - 1rem) !important;
                min-width: 250px !important;
            }

            .kpi-principal-card {
                min-height: 108px;
                height: auto;
                display: flex;
                align-items: center;
                gap: .8rem;
                padding: .85rem 1rem;
                border: 1px solid #e5e9f1;
                border-radius: 14px;
            }
        }

        /* ==================================================
        MÓVIL O VENTANA MUY ANGOSTA
        ================================================== */

        @media screen and (max-width: 760px) {
            .block-container {
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }

            .st-key-kpi_principales
            [data-testid="column"],
            .st-key-kpi_secundarios
            [data-testid="column"] {
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            .kpi-principal-card,
            .kpi-doble-card {
                min-height: auto;
                padding: 1.1rem;
            }

            .kpi-principal-icono{
                width:60px;
                height:60px;
                flex:0 0 60px;

                border-radius:18px;

                font-size:1.55rem;

                box-shadow:
                    0 8px 20px rgba(0,0,0,.12);
            }

            .kpi-principal-valor {
                font-size: 1.65rem;
            }

            .kpi-secundaria-card {
                min-height: auto;
            }
        }

        /* ==================================================
        MÓVIL MUY PEQUEÑO
        ================================================== */

        @media screen and (max-width: 480px) {
            .kpi-principal-card,
            .kpi-doble-card {
                align-items: flex-start;
                flex-direction: column;
            }

            .kpi-doble-metricas {
                width: 100%;
            }

            .kpi-doble-metrica {
                min-width: 0;
            }

            .kpi-doble-valor {
                font-size: 1.3rem;
            }

            .titulo-principal {
                font-size: 1.45rem;
            }
        }
        
        /* Columnas generales: permiten salto en pantallas angostas */
        @media screen and (max-width: 900px) {
            div[data-testid="stExpander"]
            div[data-testid="stHorizontalBlock"] {
                flex-wrap: wrap;
            }

            div[data-testid="stExpander"]
            div[data-testid="column"] {
                flex: 1 1 280px !important;
                min-width: 280px !important;
            }
        }

        @media screen and (max-width: 600px) {
            div[data-testid="stExpander"]
            div[data-testid="column"] {
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    