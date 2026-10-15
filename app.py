
import streamlit as st
import pandas as pd
import datetime
import time
import os
import io
import json
import pytz

# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================
ZONA_BOGOTA = pytz.timezone("America/Bogota")

def ahora_bogota():
    return datetime.datetime.now(ZONA_BOGOTA)

def obtener_hora_bogota():
    return ahora_bogota().strftime("%H:%M:%S")

def obtener_fecha_bogota():
    return ahora_bogota().date()

st.set_page_config(
    page_title="Control de Tiempos y Métodos | Planta Multiproceso",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "planta_activa" not in st.session_state:
    st.session_state["planta_activa"] = "Metalmecánica"

planta_seleccionada = st.session_state["planta_activa"]

# =========================================================
# 2. CONFIGURACIÓN DE CADA PLANTA
# =========================================================
if planta_seleccionada == "Metalmecánica":

    COLOR_ACCENT = "#0284c7"
    COLOR_BADGE_BG = "#f0f9ff"
    COLOR_BADGE_TEXT = "#0369a1"
    COLOR_BADGE_BORDER = "#bae6fd"
    COLOR_HEADER_BG = "#f8fafc"
    COLOR_HEADER_BORDER = "#0284c7"
    COLOR_HEADER_TEXT = "#0f172a"

    ARCHIVO_EXCEL = "Registro_Produccion_Metalmecanica.xlsx"
    ARCHIVO_OPERARIOS = "Lista_Operarios_Metalmecanica.json"

    MAQUINAS_LIST = [
        "Punzonadora Trumpf Trumatic 2000R",
        "Cortadora Láser CNC (MT 36) - F 3015",
        "Plegadora Durma CNC",
        "Dobladora Dener",
        "Soldadura MIG",
        "Soldadura PUNTO",
        "Horno Pintura",
        "Soldadura LASER",
        "Otra Máquina"
    ]

    MATERIALES_LIST = [
        "CR (Cold Rolled)",
        "HR (Hot Rolled)",
        "Acero Inoxidable",
        "Aluminio",
        "Lámina Galvanizada",
        "Otro Material"
    ]

    CALIBRES_LIST = [
        "0.8 mm (C22)",
        "0.9 mm (C20)",
        "1.2 mm (C18)",
        "1.5 mm (C16)",
        "1.9 mm (C14)",
        "2.5 mm (C12)",
        '3.0 mm (1/8")',
        '4.5 mm (3/16")',
        '6.0 mm (1/4")',
        "OTRO / LIBRE (Escribir en vivo)"
    ]

    MOTIVOS_PARO_LIST = [
        "Ninguno / Operación Normal",
        "Falta de material / Materia prima",
        "Cambio de herramienta / Setup",
        "Mantenimiento autónomo / Limpieza",
        "Falta de programa NC / Ingeniería",
        "Ajuste de holgura / Calidad",
        "Falta de energía / Aire comprimido",
        "Cambio de boquilla / Consumibles",
        "Alerta / Paro de emergencia de máquina",
        "Descanso / Almuerzo operador",
        "Operario en máquina sin producción (Ociosidad / Espera)",
        "Otro / Imprevisto"
    ]

else:

    COLOR_ACCENT = "#ea580c"
    COLOR_BADGE_BG = "#fff7ed"
    COLOR_BADGE_TEXT = "#c2410c"
    COLOR_BADGE_BORDER = "#fed7aa"
    COLOR_HEADER_BG = "#fafaf9"
    COLOR_HEADER_BORDER = "#ea580c"
    COLOR_HEADER_TEXT = "#1c1917"

    ARCHIVO_EXCEL = "Registro_Produccion_Maderas.xlsx"
    ARCHIVO_OPERARIOS = "Lista_Operarios_Maderas.json"

    MAQUINAS_LIST = [
        "Prensa Hidráulica MH3848",
        "Canteadora E-700-3 Pro",
        "Fresadora CNC ELECNC-1530ATC",
        "Seccionadora Horizontal MD03",
        "Enchapadora Cantos MD024",
        "Escuadradora MD025",
        "Trompo Tupi Eje Inclinable",
        "Prensa Hidráulica Fría MD028",
        "Taladro Múltiple Alfa 21T",
        "Taladro de Árbol KTC-18FC",
        "Otra Máquina Maderas"
    ]

    MATERIALES_LIST = [
        "Tablero MDF estándar (Crudo/Melamínico)",
        "Tablero MDF Enchapado",
        "Aglomerado MDP Melamínico",
        "Madera Sólida (Pino / Teca)",
        "Contrachapado / Triplex",
        "Tablero OSB Estructural",
        "Otro Material Maderas"
    ]

    CALIBRES_LIST = [
        "14 mm",
        "18 mm",
        "25 mm",
        "30 mm",
        "40 mm",
        "50 mm",
        "OTRO / LIBRE (Escribir en vivo)"
    ]

    MOTIVOS_PARO_LIST = [
        "Ninguno / Operación Normal",
        "Mantenimiento Preventivo Mecánico",
        "Cambio de Herramienta ATC / Brocas",
        "Ajuste de Temperatura en Prensa Caliente",
        "Cambio de Depósito / Adhesivo Canteadora",
        "Falta de Material / Insumos en Planta",
        "Falla Neumática / Presión de Aire < 6 bar",
        "Descanso / Almuerzo operador",
        "Operario en máquina sin producción (Ociosidad / Espera)",
        "Otro / Imprevisto"
    ]

# =========================================================
# 3. DISEÑO VISUAL
# =========================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {{
    --accent: {COLOR_ACCENT};
}}

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #334155;
}}

[data-testid="stHeader"] {{
    height: 0;
}}

.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1600px !important;
}}

[data-testid="stElementToolbar"] {{
    display: none !important;
}}

.top-bar-container {{
    background: linear-gradient(120deg, #0f172a, #172554);
    border-left: 4px solid var(--accent);
    padding: 13px 18px;
    border-radius: 9px;
    color: white;
    margin-bottom: 12px;
    min-height: 65px;
}}

.main-title {{
    color: white;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: .35px;
    display: flex;
    align-items: center;
    gap: 9px;
    flex-wrap: wrap;
}}

.sub-title {{
    color: #cbd5e1;
    font-size: 11px;
    margin-top: 4px;
}}

.badge-plant {{
    background: {COLOR_BADGE_BG};
    color: {COLOR_BADGE_TEXT};
    border: 1px solid {COLOR_BADGE_BORDER};
    padding: 3px 8px;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 800;
}}

.stButton > button {{
    border-radius: 8px !important;
    font-weight: 800 !important;
    transition: all .15s ease-in-out;
}}

button[kind="primary"] {{
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
    color: white !important;
}}

.timer-card {{
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    padding: 9px 13px;
    min-height: 70px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 1px 3px rgba(15,23,42,.04);
}}

.timer-card-active {{
    border: 2px solid var(--accent);
    padding: 8px 12px;
    box-shadow: 0 3px 8px rgba(15,23,42,.07);
}}

.timer-top-line {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}}

.timer-title-text {{
    font-size: 10px;
    font-weight: 800;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: .4px;
}}

.pill-idle {{
    color: #94a3b8;
    font-size: 9px;
    font-weight: 800;
}}

.pill-active {{
    color: var(--accent);
    font-size: 9px;
    font-weight: 800;
}}

.display-row {{
    display: flex;
    align-items: baseline;
    gap: 6px;
}}

.digits {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 25px;
    font-weight: 500;
    color: #0f172a;
    line-height: 1;
    font-variant-numeric: tabular-nums;
}}

.digits-active {{
    color: var(--accent);
}}

.unit-compact {{
    font-size: 10px;
    font-weight: 700;
    color: #64748b;
}}

.section-header {{
    background: {COLOR_HEADER_BG};
    border-left: 3px solid {COLOR_HEADER_BORDER};
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 800;
    color: {COLOR_HEADER_TEXT};
    border-radius: 0 5px 5px 0;
    margin: 5px 0 12px;
    text-transform: uppercase;
    letter-spacing: .45px;
}}

.section-header-red {{
    background: #fef2f2;
    border-left: 3px solid #ef4444;
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 800;
    color: #991b1b;
    border-radius: 0 5px 5px 0;
    margin: 5px 0 12px;
    text-transform: uppercase;
    letter-spacing: .45px;
}}

div[data-testid="stExpander"] {{
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}}

div[data-testid="stMetric"] {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 12px;
    border-radius: 9px;
}}

.footer-credits {{
    text-align: center;
    padding: 12px;
    margin-top: 18px;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
    border-radius: 7px;
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
}}

.footer-credits span {{
    color: var(--accent);
    font-weight: 800;
}}

@media (max-width: 900px) {{
    .main-title {{ font-size: 14px; }}
    .digits {{ font-size: 21px; }}
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4. ENCABEZADO Y SELECTOR DE PLANTA
# =========================================================
col_head, col_sw1, col_sw2 = st.columns([2.7, 1.15, 1.05])

with col_sw1:
    if st.button(
        "PLANTA METALMECÁNICA",
        use_container_width=True,
        type="primary" if planta_seleccionada == "Metalmecánica" else "secondary"
    ):
        st.session_state["planta_activa"] = "Metalmecánica"
        st.rerun()

with col_sw2:
    if st.button(
        "PLANTA DE MADERAS",
        use_container_width=True,
        type="primary" if planta_seleccionada == "Maderas" else "secondary"
    ):
        st.session_state["planta_activa"] = "Maderas"
        st.rerun()

with col_head:
    badge_text = planta_seleccionada.upper()
    st.markdown(f"""
    <div class="top-bar-container">
        <div class="main-title">
            CONTROL DE TIEMPOS Y MÉTODOS
            <span class="badge-plant">{badge_text}</span>
        </div>
        <div class="sub-title">
            Captura en vivo · Muestreo estándar · Control de producción
        </div>
    </div>
    """, unsafe_allow_html=True)
