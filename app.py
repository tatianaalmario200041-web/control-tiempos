import streamlit as st
import pandas as pd
import datetime
import time
import os
import json
import pytz
import io

# ============================================================
# 1. CONFIGURACIÓN GENERAL E INDUSTRIAL
# ============================================================

st.set_page_config(
    page_title="TOMA DE TIEMPOS MODERLINE",
    layout="wide",
    initial_sidebar_state="expanded"
)

ZONA_BOGOTA = pytz.timezone("America/Bogota")
PIN_EXPORTACION = "190520"

ARCHIVOS_EXCEL = {
    "Metalmecánica": "Registro_Produccion_Metalmecanica.xlsx",
    "Maderas": "Registro_Produccion_Maderas.xlsx"
}

ARCHIVOS_OPERARIOS = {
    "Metalmecánica": "Lista_Operarios_Metalmecanica.json",
    "Maderas": "Lista_Operarios_Maderas.json"
}

COLUMNAS_REGISTRO = [
    "Planta",
    "Operario",
    "Orden",
    "Fecha",
    "Turno",
    "Máquina",
    "Proyecto",
    "Detalle Pieza",
    "Material",
    "Espesor/Calibre",
    "Cantidad Lote",
    "Piezas OK",
    "Setup (min)",
    "Tiempo Estándar (min)",
    "Ciclo Real (min)",
    "Espera Operario (min)",
    "Paro Máquina (min)",
    "Descargue (min)",
    "Motivo Paro",
    "Hora Inicio",
    "Hora Fin"
]

# ============================================================
# 2. CONFIGURACIÓN DE PLANTAS Y PALETA DE COLORES TÉCNICA
# ============================================================

CONFIG_PLANTAS = {
    "Metalmecánica": {
        "color_primario": "#0284c7",      # Azul Cobalto Técnico
        "color_secundario": "#0369a1",
        "bg_badge": "#f0f9ff",
        "text_badge": "#0369a1",
        "bg_timer_active": "#f0f9ff",
        "border_active": "#0284c7",
        "maquinas": [
            "Punzonadora Trumpf Trumatic 2000R",
            "Cortadora Láser CNC (MT 36) - F 3015",
            "Plegadora Durma CNC",
            "Dobladora Dener",
            "Soldadura MIG",
            "Soldadura PUNTO",
            "Horno Pintura",
            "Soldadura LASER",
            "Otra Máquina"
        ],
        "materiales": [
            "CR (Cold Rolled)",
            "HR (Hot Rolled)",
            "Acero Inoxidable",
            "Aluminio",
            "Lámina Galvanizada",
            "Otro Material"
        ],
        "calibres": [
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
        ],
        "motivos_paro": [
            "Falla mecánica",
            "Falla eléctrica",
            "Falla neumática",
            "Falta de material",
            "Falta de herramientas",
            "Ajuste o calibración",
            "Cambio de referencia",
            "Mantenimiento",
            "Falta de programación",
            "Espera de calidad",
            "Falta de operario",
            "Pausa no programada",
            "Sin energía",
            "Otro motivo"
        ]
    },

    "Maderas": {
        "color_primario": "#ea580c",      # Naranja Óxido Técnico
        "color_secundario": "#c2410c",
        "bg_badge": "#fff7ed",
        "text_badge": "#c2410c",
        "bg_timer_active": "#fffaf5",
        "border_active": "#ea580c",
        "maquinas": [
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
        ],
        "materiales": [
            "Tablero MDF estándar (Crudo/Melamínico)",
            "Tablero MDF Enchapado",
            "Aglomerado MDP Melamínico",
            "Madera Sólida (Pino / Teca)",
            "Contrachapado / Triplex",
            "Tablero OSB Estructural",
            "Otro Material Maderas"
        ],
        "calibres": [
            "14 mm",
            "18 mm",
            "25 mm",
            "30 mm",
            "40 mm",
            "50 mm",
            "OTRO / LIBRE (Escribir en vivo)"
        ],
        "motivos_paro": [
            "Falla mecánica",
            "Falla eléctrica",
            "Falla hidráulica",
            "Falta de tablero o madera",
            "Falta de herramientas",
            "Cambio de referencia",
            "Ajuste de máquina",
            "Cambio de cuchilla o herramienta",
            "Mantenimiento",
            "Espera de calidad",
            "Falta de operario",
            "Falta de programación",
            "Falta de adhesivo o insumo",
            "Otro motivo"
        ]
    }
}

# Inicialización segura de la planta actual para los estilos dinámicos
if "planta_actual" not in st.session_state:
    st.session_state["planta_actual"] = "Metalmecánica"

planta_activa_ini = st.session_state["planta_actual"]
CFG = CONFIG_PLANTAS[planta_activa_ini]

COLOR_PRI = CFG["color_primario"]
COLOR_SEC = CFG["color_secundario"]
BG_BADGE = CFG["bg_badge"]
TXT_BADGE = CFG["text_badge"]
BG_TIMER_ACT = CFG["bg_timer_active"]
BORDER_ACT = CFG["border_active"]

# ============================================================
# 3. ESTILOS CSS DE NIVEL INGENIERÍA INDUSTRIAL AVANZADA
# ============================================================

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1e293b;
}}

.stApp {{
    background: #f8fafc;
}}

[data-testid="stHeader"] {{
    background: rgba(248, 250, 252, 0.95);
}}

.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}}

/* Encabezado Técnico Dinámico */
.engineering-header {{
    background: #0f172a;
    border-left: 5px solid {COLOR_PRI};
    padding: 22px 26px;
    border-radius: 8px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}}

.engineering-title {{
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.3px;
    margin: 0;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.plant-badge {{
    background-color: {BG_BADGE};
    color: {TXT_BADGE};
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

.engineering-subtitle {{
    color: #94a3b8;
    font-size: 12px;
    font-weight: 500;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Títulos de Secciones Técnicas */
.section-title-eng {{
    font-size: 13px;
    font-weight: 800;
    color: #475569;
    background: #e2e8f0;
    padding: 6px 12px;
    border-radius: 4px;
    margin: 16px 0 12px 0;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border-left: 3px solid {COLOR_PRI};
}}

/* Tarjetas de Métricas Ejecutivas */
.metric-card-eng {{
    background: white;
    padding: 16px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}}

.metric-label-eng {{
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.metric-value-eng {{
    color: #0f172a;
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    margin-top: 6px;
    letter-spacing: -0.5px;
}}

/* Tarjetas de Cronómetros de Alta Precisión Mejoradas */
.timer-card-eng {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    transition: all 0.2s ease;
}}

.timer-card-eng-active {{
    background: {BG_TIMER_ACT};
    border: 2px solid {BORDER_ACT};
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}}

.timer-header-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}}

.timer-name-eng {{
    font-size: 11px;
    font-weight: 800;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.timer-status-idle {{
    font-size: 9px;
    font-weight: 700;
    color: #64748b;
    background: #f1f5f9;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}}

.timer-status-active {{
    font-size: 9px;
    font-weight: 800;
    color: #ffffff;
    background: {COLOR_PRI};
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}}

.timer-digits-eng {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    font-weight: 500;
    color: #0f172a;
    letter-spacing: -0.5px;
    line-height: 1.1;
    margin: 4px 0;
}}

.timer-desc-eng {{
    font-size: 11px;
    color: #64748b;
}}

/* Forzar color exacto de la planta en los botones de Iniciar y de Acción Principal */
div.stButton > button[kind="primary"] {{
    background-color: {COLOR_PRI} !important;
    border-color: {COLOR_PRI} !important;
    color: #ffffff !important;
}}

div.stButton > button[kind="primary"]:hover {{
    background-color: {COLOR_SEC} !important;
    border-color: {COLOR_SEC} !important;
    color: #ffffff !important;
}}

div.stButton > button {{
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
    min-height: 38px !important;
}}

div[data-testid="stDownloadButton"] button {{
    border-radius: 6px !important;
    font-weight: 700 !important;
    min-height: 40px !important;
}}

label {{
    font-weight: 700 !important;
    font-size: 12px !important;
    color: #334155 !important;
}}

footer {{
    visibility: hidden;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. FUNCIONES DE FECHA Y FORMATO
# ============================================================

def ahora_bogota():
    return datetime.datetime.now(ZONA_BOGOTA)


def obtener_hora_bogota():
    return ahora_bogota().strftime("%H:%M:%S")


def obtener_fecha_bogota():
    return ahora_bogota().date()


def formatear_duracion(segundos):
    segundos = max(0, int(segundos))
    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def minutos_desde_segundos(segundos):
    return round(max(0, segundos) / 60, 2)


def inicializar_estado(clave, valor):
    if clave not in st.session_state:
        st.session_state[clave] = valor


# ============================================================
# 5. GESTIÓN DE CRONÓMETROS Y OPERARIOS
# ============================================================

CRONOMETROS = {
    "setup": {
        "nombre": "Setup / Alistamiento",
        "descripcion": "Preparación inicial y puesta a punto de máquina"
    },
    "ciclo": {
        "nombre": "Ciclo Real Operativo",
        "descripcion": "Tiempo efectivo de procesamiento y fabricación"
    },
    "descargue": {
        "nombre": "Descargue y Post-Corte",
        "descripcion": "Retiro, evacuación y despacho de piezas"
    },
    "paros": {
        "nombre": "Paro / Tiempo Muerto de Máquina",
        "descripcion": "Detenciones imprevistas o mecánicas"
    },
    "espera": {
        "nombre": "Operario en Espera",
        "descripcion": "Tiempos ociosos o espera de insumos"
    }
}


def inicializar_cronometros():
    for clave in CRONOMETROS:
        inicializar_estado(f"{clave}_acumulado", 0.0)
        inicializar_estado(f"{clave}_inicio", None)


def segundos_cronometro(clave):
    acumulado = float(st.session_state.get(f"{clave}_acumulado", 0.0))
    inicio = st.session_state.get(f"{clave}_inicio")
    if inicio is not None:
        acumulado += time.time() - inicio
    return max(0.0, acumulado)


def cronometros_activos_count():
    return sum(
        1 for clave in CRONOMETROS
        if st.session_state.get(f"{clave}_inicio") is not None
    )


def iniciar_cronometro(clave):
    st.session_state[f"{clave}_inicio"] = time.time()
    if not st.session_state.get("hora_inicio_registro"):
        st.session_state["hora_inicio_registro"] = obtener_hora_bogota()


def pausar_cronometro(clave):
    inicio = st.session_state.get(f"{clave}_inicio")
    if inicio is not None:
        st.session_state[f"{clave}_acumulado"] += time.time() - inicio
        st.session_state[f"{clave}_inicio"] = None


def reiniciar_cronometros():
    for clave in CRONOMETROS:
        st.session_state[f"{clave}_acumulado"] = 0.0
        st.session_state[f"{clave}_inicio"] = None
    st.session_state["hora_inicio_registro"] = None


inicializar_cronometros()
inicializar_estado("hora_inicio_registro", None)


def cargar_operarios(planta):
    archivo = ARCHIVOS_OPERARIOS[planta]
    if not os.path.exists(archivo):
        return []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if isinstance(datos, list):
            return sorted(set(str(x).strip() for x in datos if str(x).strip()))
        return []
    except (json.JSONDecodeError, OSError):
        return []


def guardar_operarios(planta, operarios):
    archivo = ARCHIVOS_OPERARIOS[planta]
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(sorted(set(operarios)), f, ensure_ascii=False, indent=4)


# ============================================================
# 6. MANEJO DE ARCHIVOS EXCEL
# ============================================================

def leer_historial(planta):
    archivo = ARCHIVOS_EXCEL[planta]
    if not os.path.exists(archivo):
        return pd.DataFrame(columns=COLUMNAS_REGISTRO)
    try:
        df = pd.read_excel(archivo, engine="openpyxl")
        for columna in COLUMNAS_REGISTRO:
            if columna not in df.columns:
                df[columna] = None
        return df[COLUMNAS_REGISTRO]
    except Exception as e:
        st.error(f"Error al leer el archivo de la planta. Detalle: {e}")
        return None


def guardar_registro(planta, registro):
    archivo = ARCHIVOS_EXCEL[planta]
    if os.path.exists(archivo):
        try:
            df_existente = pd.read_excel(archivo, engine="openpyxl")
        except Exception as e:
            raise RuntimeError(f"No se pudo leer el historial previo: {e}")
        for columna in COLUMNAS_REGISTRO:
            if columna not in df_existente.columns:
                df_existente[columna] = None
        df_existente = df_existente[COLUMNAS_REGISTRO]
    else:
        df_existente = pd.DataFrame(columns=COLUMNAS_REGISTRO)

    nuevo = pd.DataFrame([registro], columns=COLUMNAS_REGISTRO)
    resultado = pd.concat([df_existente, nuevo], ignore_index=True)
    resultado.to_excel(archivo, index=False, engine="openpyxl")


def crear_excel_en_memoria(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Registro_Industrial")
        hoja = writer.sheets["Registro_Industrial"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions
        for columna in hoja.columns:
            letra = columna[0].column_letter
            max_largo = max(len(str(celda.value or "")) for celda in columna)
            hoja.column_dimensions[letra].width = min(max(max_largo + 3, 12), 35)
    buffer.seek(0)
    return buffer


# ============================================================
# 7. CONFIGURACIÓN EN BARRA LATERAL
# ============================================================

with st.sidebar:
    st.markdown("### Configuración de Planta")
    planta = st.radio(
        "Seleccione planta activa",
        options=["Metalmecánica", "Maderas"],
        index=0 if st.session_state["planta_actual"] == "Metalmecánica" else 1,
        key="selector_planta"
    )

    if planta != st.session_state["planta_actual"]:
        st.session_state["planta_actual"] = planta
        st.rerun()

    config = CONFIG_PLANTAS[planta]

    st.markdown("---")
    st.markdown("### Estado de Estación")
    activos_qty = cronometros_activos_count()
    if activos_qty > 0:
        st.success(f"Cronómetros activos: {activos_qty}")
    else:
        st.info("Estación en pausa / Sin actividad")

    st.caption(f"Planta: {planta}")
    st.caption(f"Fecha: {obtener_fecha_bogota().strftime('%Y-%m-%d')}")

# ============================================================
# 8. ENCABEZADO INDUSTRIAL PROFESIONAL
# ============================================================

st.markdown(
    f"""
    <div class="engineering-header" style="border-left-color: {config['color_primario']};">
        <div class="engineering-title">
            TOMA DE TIEMPOS MODERLINE
            <span class="plant-badge" style="background-color: {config['bg_badge']}; color: {config['text_badge']};">{planta.upper()}</span>
        </div>
        <div class="engineering-subtitle">Ingeniería de Costos y Procesos Industriales • Estándar Operativo</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 9. PESTAÑAS PRINCIPALES
# ============================================================

tab_registro, tab_historial, tab_admin = st.tabs([
    "Registro Operativo y Cronometraje",
    "Historial y Analítica de Ciclos",
    "Administración y Base de Datos"
])

# ============================================================
# 10. PESTAÑA 1: REGISTRO Y CRONÓMETROS SIMULTÁNEOS
# ============================================================

with tab_registro:
    operarios = cargar_operarios(planta)

    st.markdown('<div class="section-title-eng">1. Datos Generales de la Orden de Producción</div>', unsafe_allow_html=True)

    col_op1, col_op2, col_op3 = st.columns([1.5, 1.5, 1])

    with col_op1:
        opciones_operarios = ["Seleccione operario..."] + operarios
        operario = st.selectbox("Operario Responsable", opciones_operarios, key=f"op_sel_{planta}")

    with col_op2:
        nuevo_operario = st.text_input("Registrar Nuevo Operario", placeholder="Nombre y Apellido", key=f"nuevo_op_{planta}")
        if st.button("Registrar Operario", key=f"btn_save_op_{planta}", use_container_width=True, type="primary"):
            nombre = nuevo_operario.strip()
            if not nombre:
                st.warning("Ingrese el nombre del operario.")
            elif nombre in operarios:
                st.info("El operario ya se encuentra registrado.")
            else:
                operarios.append(nombre)
                guardar_operarios(planta, operarios)
                st.success("Operario registrado con éxito.")
                st.rerun()

    with col_op3:
        fecha_registro = st.date_input("Fecha de Registro", value=obtener_fecha_bogota(), key=f"fec_{planta}")

    col_op4, col_op5, col_op6 = st.columns(3)

    with col_op4:
        orden = st.text_input("Orden de Producción (OP)", placeholder="Ej. OP-2026-001", key=f"ord_{planta}")
    with col_op5:
        turno = st.selectbox("Turno de Trabajo", ["Turno 1 (Mañana)", "Turno 2 (Tarde)", "Turno 3 (Noche)", "Mixto"], key=f"tur_{planta}")
    with col_op6:
        maquina = st.selectbox("Máquina / Estación", config["maquinas"], key=f"maq_{planta}")

    col_prod1, col_prod2 = st.columns(2)
    with col_prod1:
        proyecto = st.text_input("Proyecto / Referencia General", placeholder="Ej. Estantería Metálica Módulo A", key=f"proy_{planta}")
    with col_prod2:
        detalle_pieza = st.text_input("Especificación de Pieza / Sub-Ensamblaje", placeholder="Ej. Lateral Derecho Perforado", key=f"det_{planta}")

    col_mat1, col_mat2, col_mat3 = st.columns(3)
    with col_mat1:
        material = st.selectbox("Material Insumo", config["materiales"], key=f"mat_{planta}")
    with col_mat2:
        calibre = st.selectbox("Espesor / Calibre", config["calibres"], key=f"cal_{planta}")
    with col_mat3:
        calibre_personalizado = ""
        if calibre == "OTRO / LIBRE (Escribir en vivo)":
            calibre_personalizado = st.text_input("Especificar Calibre Manual", placeholder="Valor exacto", key=f"cal_lib_{planta}")

    calibre_final = calibre_personalizado.strip() if calibre == "OTRO / LIBRE (Escribir en vivo)" else calibre

    col_cant1, col_cant2, col_cant3 = st.columns(3)
    with col_cant1:
        cantidad_lote = st.number_input("Cantidad Total Lote", min_value=1, value=1, step=1, key=f"cant_lote_{planta}")
    with col_cant2:
        piezas_ok = st.number_input("Piezas Conformes (OK)", min_value=0, value=1, step=1, key=f"p_ok_{planta}")
    with col_cant3:
        tiempo_estandar = st.number_input("Tiempo Estándar Unitario (min)", min_value=0.0, value=0.0, step=0.1, format="%.2f", key=f"t_std_{planta}")

    st.markdown('<div class="section-title-eng">2. Cronómetros Múltiples (Funcionamiento Simultáneo e Independiente)</div>', unsafe_allow_html=True)
    st.caption("Puede iniciar varios cronómetros a la vez (por ejemplo, registrar paros en paralelo o solapamiento de tiempos) o gestionarlos de forma independiente.")

    claves_cronometros = list(CRONOMETROS.keys())

    for inicio_fila in range(0, len(claves_cronometros), 2):
        columnas = st.columns(2)
        for idx_col, col_actual in enumerate(columnas):
            pos = inicio_fila + idx_col
            if pos >= len(claves_cronometros):
                continue
            clave = claves_cronometros[pos]
            datos = CRONOMETROS[clave]
            activo = st.session_state.get(f"{clave}_inicio") is not None
            duracion = segundos_cronometro(clave)

            card_cls = "timer-card-eng-active" if activo else "timer-card-eng"
            status_cls = "timer-status-active" if activo else "timer-status-idle"
            status_txt = "EN EJECUCIÓN" if activo else "DETENIDO"

            with col_actual:
                st.markdown(
                    f"""
                    <div class="{card_cls}">
                        <div class="timer-header-row">
                            <span class="timer-name-eng">{datos['nombre']}</span>
                            <span class="{status_cls}">[{status_txt}]</span>
                        </div>
                        <div class="timer-digits-eng">{formatear_duracion(duracion)}</div>
                        <div class="timer-desc-eng">{datos['descripcion']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if not activo:
                        if st.button("Iniciar", key=f"iniciar_{clave}_{planta}", use_container_width=True, type="primary"):
                            iniciar_cronometro(clave)
                            st.rerun()
                    else:
                        if st.button("Pausar", key=f"pausar_{clave}_{planta}", use_container_width=True):
                            pausar_cronometro(clave)
                            st.rerun()
                with b_col2:
                    if st.button("Reiniciar", key=f"reset_{clave}_{planta}", use_container_width=True):
                        pausar_cronometro(clave)
                        st.session_state[f"{clave}_acumulado"] = 0.0
                        st.rerun()

    if cronometros_activos_count() > 0:
        time.sleep(1)
        st.rerun()

    st.markdown('<div class="section-title-eng">3. Motivo de Paro o Detención Operativa</div>', unsafe_allow_html=True)
    motivo_paro = st.selectbox("Seleccione Motivo Principal de Paro", ["No aplica / Operación Continua"] + config["motivos_paro"], key=f"mot_{planta}")

    st.markdown('<div class="section-title-eng">4. Consolidado y Analítica de Tiempos del Registro</div>', unsafe_allow_html=True)

    tiempos_seg = {clv: segundos_cronometro(clv) for clv in CRONOMETROS}
    setup_min = minutos_desde_segundos(tiempos_seg["setup"])
    ciclo_min = minutos_desde_segundos(tiempos_seg["ciclo"])
    descargue_min = minutos_desde_segundos(tiempos_seg["descargue"])
    paros_min = minutos_desde_segundos(tiempos_seg["paros"])
    espera_min = minutos_desde_segundos(tiempos_seg["espera"])

    tiempo_total_min = round(setup_min + ciclo_min + descargue_min + paros_min + espera_min, 2)
    tiempo_productivo_min = ciclo_min
    tiempo_improductivo_min = round(paros_min + espera_min, 2)

    cm1, cm2, cm3, cm4 = st.columns(4)
    with cm1:
        st.markdown(f"""
            <div class="metric-card-eng">
                <div class="metric-label-eng">Tiempo Total</div>
                <div class="metric-value-eng">{tiempo_total_min:.2f} min</div>
            </div>
        """, unsafe_allow_html=True)
    with cm2:
        st.markdown(f"""
            <div class="metric-card-eng">
                <div class="metric-label-eng">Ciclo Productivo</div>
                <div class="metric-value-eng">{tiempo_productivo_min:.2f} min</div>
            </div>
        """, unsafe_allow_html=True)
    with cm3:
        st.markdown(f"""
            <div class="metric-card-eng">
                <div class="metric-label-eng">Tiempos Improductivos</div>
                <div class="metric-value-eng">{tiempo_improductivo_min:.2f} min</div>
            </div>
        """, unsafe_allow_html=True)
    with cm4:
        eficiencia_parcial = (tiempo_productivo_min / tiempo_total_min * 100) if tiempo_total_min > 0 else 0.0
        st.markdown(f"""
            <div class="metric-card-eng">
                <div class="metric-label-eng">Eficiencia de Ciclo</div>
                <div class="metric-value-eng">{eficiencia_parcial:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_btn_save, col_btn_clear = st.columns([2, 1])
    with col_btn_save:
        guardar_btn = st.button("Guardar Registro en Base de Datos", type="primary", use_container_width=True, key=f"save_db_{planta}")
    with col_btn_clear:
        limpiar_btn = st.button("Reiniciar Todo", use_container_width=True, key=f"clear_all_{planta}")

    if limpiar_btn:
        reiniciar_cronometros()
        st.rerun()

    if guardar_btn:
        errores = []
        if operario == "Seleccione operario...":
            errores.append("Debe seleccionar un operario responsable.")
        if not orden.strip():
            errores.append("El campo Orden de Producción (OP) es obligatorio.")
        if not proyecto.strip():
            errores.append("El campo Proyecto / Referencia es obligatorio.")
        if not detalle_pieza.strip():
            errores.append("El detalle de la pieza es obligatorio.")
        if calibre == "OTRO / LIBRE (Escribir en vivo)" and not calibre_final:
            errores.append("Debe especificar el calibre de forma manual.")
        if piezas_ok > cantidad_lote:
            errores.append("Las piezas OK no pueden ser mayores a la cantidad del lote.")
        if tiempo_total_min <= 0:
            errores.append("Debe registrar al menos un tiempo operativo antes de guardar.")

        if errores:
            for err in errores:
                st.error(err)
        else:
            hora_ini = st.session_state.get("hora_inicio_registro") or obtener_hora_bogota()
            hora_fin = obtener_hora_bogota()
            motivo_final = "" if motivo_paro == "No aplica / Operación Continua" else motivo_paro

            registro_data = {
                "Planta": planta,
                "Operario": operario,
                "Orden": orden.strip(),
                "Fecha": fecha_registro.strftime("%Y-%m-%d"),
                "Turno": turno,
                "Máquina": maquina,
                "Proyecto": proyecto.strip(),
                "Detalle Pieza": detalle_pieza.strip(),
                "Material": material,
                "Espesor/Calibre": calibre_final,
                "Cantidad Lote": int(cantidad_lote),
                "Piezas OK": int(piezas_ok),
                "Setup (min)": setup_min,
                "Tiempo Estándar (min)": float(tiempo_estandar),
                "Ciclo Real (min)": ciclo_min,
                "Espera Operario (min)": espera_min,
                "Paro Máquina (min)": paros_min,
                "Descargue (min)": descargue_min,
                "Motivo Paro": motivo_final,
                "Hora Inicio": hora_ini,
                "Hora Fin": hora_fin
            }

            try:
                guardar_registro(planta, registro_data)
                st.success(f"Registro almacenado con éxito en {ARCHIVOS_EXCEL[planta]}.")
                reiniciar_cronometros()
                st.rerun()
            except Exception as ex:
                st.error(f"Error al guardar los datos: {ex}")

# ============================================================
# 11. PESTAÑA 2: HISTORIAL Y ANALÍTICA
# ============================================================

with tab_historial:
    st.markdown('<div class="section-title-eng">Historial y Consultas de Producción</div>', unsafe_allow_html=True)
    st.caption(f"Fuente de datos activa: {ARCHIVOS_EXCEL[planta]}")

    df_hist = leer_historial(planta)

    if df_hist is not None:
        if df_hist.empty:
            st.info("No se registran datos previos almacenados para esta planta.")
        else:
            cf1, cf2, cf3 = st.columns(3)
            with cf1:
                ops_list = sorted(df_hist["Operario"].dropna().astype(str).unique().tolist())
                filtro_op = st.selectbox("Filtrar por Operario", ["Todos"] + ops_list, key=f"f_op_{planta}")
            with cf2:
                maqs_list = sorted(df_hist["Máquina"].dropna().astype(str).unique().tolist())
                filtro_mq = st.selectbox("Filtrar por Máquina", ["Todas"] + maqs_list, key=f"f_mq_{planta}")
            with cf3:
                filtro_txt = st.text_input("Búsqueda por Orden (OP)", placeholder="Ingrese OP...", key=f"f_txt_{planta}")

            df_view = df_hist.copy()
            if filtro_op != "Todos":
                df_view = df_view[df_view["Operario"].astype(str) == filtro_op]
            if filtro_mq != "Todas":
                df_view = df_view[df_view["Máquina"].astype(str) == filtro_mq]
            if filtro_txt.strip():
                df_view = df_view[df_view["Orden"].astype(str).str.contains(filtro_txt.strip(), case=False, na=False)]

            tot_regs = len(df_view)
            tot_ciclo_val = pd.to_numeric(df_view["Ciclo Real (min)"], errors="coerce").fillna(0).sum()
            tot_paros_val = pd.to_numeric(df_view["Paro Máquina (min)"], errors="coerce").fillna(0).sum()

            ch1, ch2, ch3 = st.columns(3)
            ch1.metric("Registros Filtrados", tot_regs)
            ch2.metric("Suma Ciclo Real", f"{tot_ciclo_val:.2f} min")
            ch3.metric("Suma Paros de Máquina", f"{tot_paros_val:.2f} min")

            st.dataframe(df_view, use_container_width=True, hide_index=True)

            buffer_dl = crear_excel_en_memoria(df_view)
            st.download_button(
                label="Descargar Reporte Filtrado (Excel)",
                data=buffer_dl,
                file_name=f"Reporte_{planta}_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

# ============================================================
# 12. PESTAÑA 3: ADMINISTRACIÓN Y SEGURIDAD
# ============================================================

with tab_admin:
    st.markdown('<div class="section-title-eng">Panel de Administración de Base de Datos</div>', unsafe_allow_html=True)
    st.warning("Acceso restringido para supervisores y analistas de costos.")

    pin_code = st.text_input("Ingrese PIN de Seguridad Autorizado", type="password", key=f"pin_adm_{planta}")

    if pin_code == PIN_EXPORTACION:
        st.success("Acceso autorizado con éxito.")
        if os.path.exists(ARCHIVOS_EXCEL[planta]):
            with open(ARCHIVOS_EXCEL[planta], "rb") as bin_file:
                st.download_button(
                    label=f"Descargar Base de Datos Completa ({planta})",
                    data=bin_file,
                    file_name=ARCHIVOS_EXCEL[planta],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )

            if st.button("Eliminar / Reiniciar Historial de Planta", type="secondary", use_container_width=True):
                try:
                    os.remove(ARCHIVOS_EXCEL[planta])
                    st.success("Base de datos reiniciada correctamente.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No se pudo eliminar el archivo: {exc}")
        else:
            st.info("No existe un archivo físico de base de datos para esta planta.")
    elif pin_code != "":
        st.error("PIN incorrecto.")
