import streamlit as st
import pandas as pd
import datetime
import time
import os
import json
import pytz
import io

# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Control de Tiempos y Métodos",
    page_icon="⏱️",
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
# 2. CONFIGURACIÓN DE PLANTAS
# ============================================================

CONFIG_PLANTAS = {
    "Metalmecánica": {
        "color": "#0284c7",
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
        "color": "#ea580c",
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

# ============================================================
# 3. ESTILO VISUAL (Números Finos y Elegantes)
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: #f4f6fa;
}

[data-testid="stHeader"] {
    background: rgba(244, 246, 250, 0.95);
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

.hero {
    background: linear-gradient(135deg, #111827 0%, #202c40 100%);
    color: white;
    padding: 25px 28px;
    border-radius: 18px;
    margin-bottom: 20px;
    border-bottom: 4px solid var(--plant-color);
}

.hero h1 {
    color: white;
    font-size: 28px;
    font-weight: 800;
    margin: 0;
}

.hero p {
    color: #cbd5e1;
    margin: 7px 0 0 0;
    font-size: 13px;
}

.section-title {
    font-size: 17px;
    font-weight: 800;
    color: #172033;
    padding: 10px 0 8px 0;
    border-bottom: 2px solid #e2e8f0;
    margin: 12px 0 15px 0;
}

.metric-card {
    background: white;
    padding: 17px;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    min-height: 95px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.035);
}

.metric-label {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .4px;
}

.metric-value {
    color: #0f172a;
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px;
    font-weight: 500;
    margin-top: 8px;
    letter-spacing: -0.5px;
}

.timer-card {
    background: white;
    border: 1px solid #dbe3ed;
    border-radius: 15px;
    padding: 16px;
    margin-bottom: 12px;
}

.timer-name {
    font-size: 14px;
    color: #334155;
    font-weight: 800;
}

.timer-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 500;
    color: #0f172a;
    margin: 7px 0;
    letter-spacing: -0.5px;
}

.timer-note {
    font-size: 11px;
    color: #64748b;
}

div.stButton > button {
    border-radius: 9px;
    font-weight: 700;
    min-height: 40px;
    transition: all .15s ease;
}

div[data-testid="stDownloadButton"] button {
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #dbe3ed;
    border-radius: 10px;
    overflow: hidden;
}

label {
    font-weight: 600 !important;
}

footer {
    visibility: hidden;
}

@media (max-width: 700px) {
    .hero {
        padding: 18px;
    }
    .hero h1 {
        font-size: 22px;
    }
    .timer-value {
        font-size: 24px;
    }
}
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
# 5. OPERARIOS
# ============================================================

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
        json.dump(
            sorted(set(operarios)),
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 6. LECTURA Y ESCRITURA DE EXCEL
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
        st.error(
            f"No fue posible leer el archivo {archivo}. "
            f"Verifica que no esté abierto en Excel y que no esté dañado. "
            f"Detalle: {e}"
        )
        return None


def guardar_registro(planta, registro):
    archivo = ARCHIVOS_EXCEL[planta]

    if os.path.exists(archivo):
        try:
            df_existente = pd.read_excel(archivo, engine="openpyxl")
        except Exception as e:
            raise RuntimeError(
                f"No se pudo leer el historial existente. "
                f"No se guardó el registro para evitar sobrescribir datos. {e}"
            )

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
        df.to_excel(writer, index=False, sheet_name="Registro")
        hoja = writer.sheets["Registro"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        for columna in hoja.columns:
            letra = columna[0].column_letter
            max_largo = 0

            for celda in columna:
                valor = "" if celda.value is None else str(celda.value)
                max_largo = max(max_largo, len(valor))

            hoja.column_dimensions[letra].width = min(max(max_largo + 2, 12), 35)

    buffer.seek(0)
    return buffer


# ============================================================
# 7. CRONÓMETROS INDEPENDIENTES
# ============================================================

CRONOMETROS = {
    "setup": {
        "nombre": "Setup / Alistamiento",
        "descripcion": "Preparación inicial de máquina y herramientas"
    },
    "ciclo": {
        "nombre": "Ciclo Real",
        "descripcion": "Tiempo de operación productiva"
    },
    "descargue": {
        "nombre": "Descargue",
        "descripcion": "Retiro y organización de piezas terminadas"
    },
    "paros": {
        "nombre": "Paros de Máquina",
        "descripcion": "Tiempo de detención de la máquina"
    },
    "espera": {
        "nombre": "Espera de Operario",
        "descripcion": "Tiempo de espera sin operación productiva"
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


def cronometro_activo():
    return any(
        st.session_state.get(f"{clave}_inicio") is not None
        for clave in CRONOMETROS
    )


def iniciar_cronometro(clave):
    if cronometro_activo():
        st.warning(
            "Hay un cronómetro activo. Deténlo antes de iniciar otro."
        )
        return

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

# ============================================================
# 8. SELECCIÓN DE PLANTA
# ============================================================

if "planta_actual" not in st.session_state:
    st.session_state["planta_actual"] = "Metalmecánica"

with st.sidebar:
    st.markdown("## ⚙️ Configuración")

    planta = st.radio(
        "Selecciona la planta",
        options=["Metalmecánica", "Maderas"],
        index=(
            0 if st.session_state["planta_actual"] == "Metalmecánica"
            else 1
        ),
        key="selector_planta"
    )

    if planta != st.session_state["planta_actual"]:
        if cronometro_activo():
            st.warning(
                "Detén el cronómetro activo antes de cambiar de planta."
            )
            st.session_state["selector_planta"] = (
                st.session_state["planta_actual"]
            )
        else:
            st.session_state["planta_actual"] = planta
            st.rerun()

    planta = st.session_state["planta_actual"]
    config = CONFIG_PLANTAS[planta]

    st.markdown("---")
    st.markdown("### 📌 Estado de la sesión")

    if cronometro_activo():
        st.success("Cronómetro en ejecución")
    else:
        st.info("Sin cronómetros activos")

    st.caption(f"Planta activa: {planta}")
    st.caption(f"Fecha: {obtener_fecha_bogota().strftime('%d/%m/%Y')}")

# ============================================================
# 9. ENCABEZADO
# ============================================================

st.markdown(
    f"""
    <div class="hero" style="--plant-color:{config['color']}">
        <h1>⏱️ Control de Tiempos y Métodos</h1>
        <p>Registro de producción · Estudio de tiempos · Control operativo</p>
        <p><strong>Planta activa:</strong> {planta}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 10. PESTAÑAS PRINCIPALES
# ============================================================

tab_registro, tab_historial, tab_administracion = st.tabs([
    "📝 Registro de producción",
    "📊 Historial y análisis",
    "⚙️ Administración"
])

# ============================================================
# 11. PESTAÑA DE REGISTRO
# ============================================================

with tab_registro:

    operarios = cargar_operarios(planta)

    st.markdown(
        '<div class="section-title">1. Información de la operación</div>',
        unsafe_allow_html=True
    )

    col_op1, col_op2, col_op3 = st.columns([1.5, 1.5, 1])

    with col_op1:
        opciones_operarios = ["Seleccionar operario"] + operarios

        operario = st.selectbox(
            "Operario responsable",
            opciones_operarios,
            key=f"operario_select_{planta}"
        )

    with col_op2:
        nuevo_operario = st.text_input(
            "Agregar nuevo operario",
            placeholder="Nombre completo",
            key=f"nuevo_operario_{planta}"
        )

        if st.button(
            "➕ Guardar operario",
            key=f"guardar_operario_{planta}",
            use_container_width=True
        ):
            nombre = nuevo_operario.strip()

            if not nombre:
                st.warning("Escribe el nombre del operario.")
            elif nombre in operarios:
                st.info("Este operario ya está registrado.")
            else:
                operarios.append(nombre)
                guardar_operarios(planta, operarios)
                st.success(f"Operario agregado: {nombre}")
                st.rerun()

    with col_op3:
        fecha_registro = st.date_input(
            "Fecha del registro",
            value=obtener_fecha_bogota(),
            key=f"fecha_registro_{planta}"
        )

    col_op4, col_op5, col_op6 = st.columns(3)

    with col_op4:
        orden = st.text_input(
            "Orden de producción (OP)",
            placeholder="Ej. OP-00125",
            key=f"orden_{planta}"
        )

    with col_op5:
        turno = st.selectbox(
            "Turno",
            ["Mañana", "Tarde", "Noche", "Mixto"],
            key=f"turno_{planta}"
        )

    with col_op6:
        maquina = st.selectbox(
            "Máquina",
            config["maquinas"],
            key=f"maquina_{planta}"
        )

    col_prod1, col_prod2 = st.columns(2)

    with col_prod1:
        proyecto = st.text_input(
            "Proyecto / Producto",
            placeholder="Nombre del proyecto o producto",
            key=f"proyecto_{planta}"
        )

    with col_prod2:
        detalle_pieza = st.text_input(
            "Detalle de la pieza",
            placeholder="Referencia, pieza o descripción",
            key=f"detalle_pieza_{planta}"
        )

    col_mat1, col_mat2, col_mat3 = st.columns(3)

    with col_mat1:
        material = st.selectbox(
            "Material",
            config["materiales"],
            key=f"material_{planta}"
        )

    with col_mat2:
        calibre = st.selectbox(
            "Espesor / Calibre",
            config["calibres"],
            key=f"calibre_{planta}"
        )

    with col_mat3:
        calibre_personalizado = ""

        if calibre == "OTRO / LIBRE (Escribir en vivo)":
            calibre_personalizado = st.text_input(
                "Especificar espesor o calibre",
                placeholder="Escribe el valor",
                key=f"calibre_personalizado_{planta}"
            )

    if calibre == "OTRO / LIBRE (Escribir en vivo)":
        calibre_final = calibre_personalizado.strip()
    else:
        calibre_final = calibre

    col_cant1, col_cant2, col_cant3 = st.columns(3)

    with col_cant1:
        cantidad_lote = st.number_input(
            "Cantidad del lote",
            min_value=1,
            value=1,
            step=1,
            key=f"cantidad_lote_{planta}"
        )

    with col_cant2:
        piezas_ok = st.number_input(
            "Piezas OK",
            min_value=0,
            value=1,
            step=1,
            key=f"piezas_ok_{planta}"
        )

    with col_cant3:
        tiempo_estandar = st.number_input(
            "Tiempo estándar por pieza (min)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f",
            key=f"tiempo_estandar_{planta}"
        )

    st.markdown(
        '<div class="section-title">2. Cronómetros de estudio de tiempos</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Inicia el cronómetro correspondiente a la actividad. "
        "Pausa el cronómetro al terminarla. Solo puede haber uno activo a la vez."
    )

    claves_cronometros = list(CRONOMETROS.keys())

    for inicio_fila in range(0, len(claves_cronometros), 2):
        columnas = st.columns(2)

        for indice_columna, columna in enumerate(columnas):
            posicion = inicio_fila + indice_columna

            if posicion >= len(claves_cronometros):
                continue

            clave = claves_cronometros[posicion]
            datos = CRONOMETROS[clave]
            activo = st.session_state.get(f"{clave}_inicio") is not None
            duracion = segundos_cronometro(clave)

            with columna:
                st.markdown(
                    f"""
                    <div class="timer-card">
                        <div class="timer-name">{datos['nombre']}</div>
                        <div class="timer-value">{formatear_duracion(duracion)}</div>
                        <div class="timer-note">{datos['descripcion']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if not activo:
                        if st.button(
                            "▶ Iniciar",
                            key=f"iniciar_{clave}",
                            use_container_width=True,
                            type="primary"
                        ):
                            iniciar_cronometro(clave)
                            st.rerun()
                    else:
                        if st.button(
                            "⏸ Pausar",
                            key=f"pausar_{clave}",
                            use_container_width=True
                        ):
                            pausar_cronometro(clave)
                            st.rerun()

                with col_btn2:
                    if st.button(
                        "↺ Reiniciar",
                        key=f"reiniciar_{clave}",
                        use_container_width=True
                    ):
                        pausar_cronometro(clave)
                        st.session_state[f"{clave}_acumulado"] = 0.0
                        st.rerun()

    if cronometro_activo():
        time.sleep(1)
        st.rerun()

    st.markdown(
        '<div class="section-title">3. Motivo de paro</div>',
        unsafe_allow_html=True
    )

    motivo_paro = st.selectbox(
        "Motivo principal del paro",
        ["No aplica / Sin paro"] + config["motivos_paro"],
        key=f"motivo_paro_{planta}"
    )

    st.markdown(
        '<div class="section-title">4. Resumen de tiempos registrados</div>',
        unsafe_allow_html=True
    )

    tiempos_segundos = {
        clave: segundos_cronometro(clave)
        for clave in CRONOMETROS
    }

    setup_min = minutos_desde_segundos(tiempos_segundos["setup"])
    ciclo_min = minutos_desde_segundos(tiempos_segundos["ciclo"])
    descargue_min = minutos_desde_segundos(tiempos_segundos["descargue"])
    paros_min = minutos_desde_segundos(tiempos_segundos["paros"])
    espera_min = minutos_desde_segundos(tiempos_segundos["espera"])

    tiempo_total_min = round(
        setup_min + ciclo_min + descargue_min + paros_min + espera_min,
        2
    )

    tiempo_productivo_min = ciclo_min
    tiempo_no_productivo_min = round(paros_min + espera_min, 2)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Tiempo total</div>
                <div class="metric-value">{tiempo_total_min:.2f}</div>
                <div class="timer-note">Minutos</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Ciclo productivo</div>
                <div class="metric-value">{tiempo_productivo_min:.2f}</div>
                <div class="timer-note">Minutos</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Tiempo no productivo</div>
                <div class="metric-value">{tiempo_no_productivo_min:.2f}</div>
                <div class="timer-note">Espera + paros</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_m4:
        if tiempo_total_min > 0:
            porcentaje_productivo = (
                tiempo_productivo_min / tiempo_total_min
            ) * 100
        else:
            porcentaje_productivo = 0.0

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">% ciclo del total</div>
                <div class="metric-value">{porcentaje_productivo:.1f}%</div>
                <div class="timer-note">Participación del ciclo</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    col_guardar, col_limpiar = st.columns([2, 1])

    with col_guardar:
        guardar_boton = st.button(
            "💾 GUARDAR REGISTRO DE PRODUCCIÓN",
            type="primary",
            use_container_width=True,
            key="guardar_registro"
        )

    with col_limpiar:
        limpiar_boton = st.button(
            "🧹 Reiniciar cronómetros",
            use_container_width=True,
            key="limpiar_cronometros"
        )

    if limpiar_boton:
        reiniciar_cronometros()
        st.rerun()

    if guardar_boton:
        errores = []

        if operario == "Seleccionar operario":
            errores.append("Selecciona un operario responsable.")

        if not orden.strip():
            errores.append("Ingresa la orden de producción.")

        if not proyecto.strip():
            errores.append("Ingresa el proyecto o producto.")

        if not detalle_pieza.strip():
            errores.append("Ingresa el detalle de la pieza.")

        if calibre == "OTRO / LIBRE (Escribir en vivo)" and not calibre_final:
            errores.append("Especifica el espesor o calibre.")

        if piezas_ok > cantidad_lote:
            errores.append("Las piezas OK no pueden superar la cantidad del lote.")

        if cronometro_activo():
            errores.append("Pausa todos los cronómetros antes de guardar.")

        if tiempo_total_min <= 0:
            errores.append("Registra al menos un tiempo antes de guardar.")

        if errores:
            for error in errores:
                st.error(error)

        else:
            hora_inicio = (
                st.session_state.get("hora_inicio_registro")
                or obtener_hora_bogota()
            )
            hora_fin = obtener_hora_bogota()

            if motivo_paro == "No aplica / Sin paro":
                motivo_final = ""
            else:
                motivo_final = motivo_paro

            registro = {
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
                "Hora Inicio": hora_inicio,
                "Hora Fin": hora_fin
            }

            try:
                guardar_registro(planta, registro)
                st.success(
                    f"Registro guardado correctamente en {ARCHIVOS_EXCEL[planta]}."
                )
                reiniciar_cronometros()
                st.rerun()

            except Exception as e:
                st.error(f"No se pudo guardar el registro: {e}")

# ============================================================
# 12. PESTAÑA DE HISTORIAL Y ANÁLISIS
# ============================================================

with tab_historial:

    st.markdown(
        '<div class="section-title">Historial de producción</div>',
        unsafe_allow_html=True
    )

    st.caption(f"Archivo consultado: {ARCHIVOS_EXCEL[planta]}")

    df_historial = leer_historial(planta)

    if df_historial is not None:

        if df_historial.empty:
            st.info(
                "Todavía no hay registros para esta planta. "
                "Guarda una operación para comenzar el historial."
            )

        else:
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                operadores_historial = sorted(
                    df_historial["Operario"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                filtro_operario = st.selectbox(
                    "Filtrar por operario",
                    ["Todos"] + operadores_historial,
                    key=f"filtro_operario_{planta}"
                )

            with col_f2:
                maquinas_historial = sorted(
                    df_historial["Máquina"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                filtro_maquina = st.selectbox(
                    "Filtrar por máquina",
                    ["Todas"] + maquinas_historial,
                    key=f"filtro_maquina_{planta}"
                )

            with col_f3:
                filtro_op = st.text_input(
                    "Buscar orden de producción",
                    placeholder="Escribe una OP",
                    key=f"filtro_op_{planta}"
                )

            df_filtrado = df_historial.copy()

            if filtro_operario != "Todos":
                df_filtrado = df_filtrado[
                    df_filtrado["Operario"].astype(str) == filtro_operario
                ]

            if filtro_maquina != "Todas":
                df_filtrado = df_filtrado[
                    df_filtrado["Máquina"].astype(str) == filtro_maquina
                ]

            if filtro_op.strip():
                df_filtrado = df_filtrado[
                    df_filtrado["Orden"]
                    .astype(str)
                    .str.contains(filtro_op.strip(), case=False, na=False)
                ]

            # Indicadores calculados a partir del historial filtrado
            total_registros = len(df_filtrado)

            if "Ciclo Real (min)" in df_filtrado.columns:
                total_ciclo = pd.to_numeric(
                    df_filtrado["Ciclo Real (min)"], errors="coerce"
                ).fillna(0).sum()
            else:
                total_ciclo = 0

            if "Paro Máquina (min)" in df_filtrado.columns:
                total_paros = pd.to_numeric(
                    df_filtrado["Paro Máquina (min)"], errors="coerce"
                ).fillna(0).sum()
            else:
                total_paros = 0

            if "Espera Operario (min)" in df_filtrado.columns:
                total_espera = pd.to_numeric(
                    df_filtrado["Espera Operario (min)"], errors="coerce"
                ).fillna(0).sum()
            else:
                total_espera = 0

            st.markdown("### Resumen del filtrado")
            col_h1, col_h2, col_h3 = st.columns(3)
            col_h1.metric("Registros encontrados", total_registros)
            col_h2.metric("Total ciclo real", f"{total_ciclo:.2f} min")
            col_h3.metric("Total paros/espera", f"{(total_paros + total_espera):.2f} min")

            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

            buffer_excel = crear_excel_en_memoria(df_filtrado)
            st.download_button(
                label="📥 Descargar datos filtrados en Excel",
                data=buffer_excel,
                file_name=f"Historial_{planta}_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ============================================================
# 13. PESTAÑA DE ADMINISTRACIÓN
# ============================================================

with tab_administracion:
    st.markdown(
        '<div class="section-title">Administración y mantenimiento de datos</div>',
        unsafe_allow_html=True
    )

    st.warning("Zona protegida para el manejo de registros de planta.")

    pin_ingresado = st.text_input(
        "Ingresa el PIN de seguridad para habilitar acciones de administración",
        type="password",
        key=f"pin_admin_{planta}"
    )

    if pin_ingresado == PIN_EXPORTACION:
        st.success("PIN correcto. Acceso autorizado.")

        if os.path.exists(ARCHIVOS_EXCEL[planta]):
            with open(ARCHIVOS_EXCEL[planta], "rb") as archivo_binario:
                st.download_button(
                    label=f"📥 Descargar base de datos completa ({planta})",
                    data=archivo_binario,
                    file_name=ARCHIVOS_EXCEL[planta],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            if st.button("🗑️ Borrar historial de esta planta", type="secondary", use_container_width=True):
                try:
                    os.remove(ARCHIVOS_EXCEL[planta])
                    st.success("Historial eliminado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"No se pudo eliminar el archivo: {e}")
        else:
            st.info("No hay archivo de base de datos creado todavía para esta planta.")

    elif pin_ingresado != "":
        st.error("PIN incorrecto.")
