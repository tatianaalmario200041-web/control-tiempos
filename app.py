import streamlit as st
import pandas as pd
import datetime
import time
import os
import io
import json
import pytz

# Configuración de Zona Horaria (Bogotá - Colombia UTC-5)
ZONA_BOGOTA = pytz.timezone('America/Bogota')

def obtener_hora_bogota():
    return datetime.datetime.now(ZONA_BOGOTA).strftime("%H:%M:%S")

def obtener_fecha_bogota():
    return datetime.datetime.now(ZONA_BOGOTA).date()

# Configuración de Página
st.set_page_config(
    page_title="Control de Tiempos & Métodos | Planta Multi-Proceso",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar Estado de Planta en Session State
if "planta_activa" not in st.session_state:
    st.session_state["planta_activa"] = "Metalmecánica"

planta_seleccionada = st.session_state["planta_activa"]

# Definición de Colores Dinámicos por Planta
if planta_seleccionada == "Metalmecánica":
    COLOR_BORDER = "#0284c7"
    COLOR_BADGE_BG = "rgba(56, 189, 248, 0.18)"
    COLOR_BADGE_TEXT = "#38bdf8"
    COLOR_BADGE_BORDER = "rgba(56, 189, 248, 0.4)"
    COLOR_RUNNING_BG = "#f0f9ff"
    COLOR_RUNNING_BORDER = "#0284c7"
    COLOR_RUNNING_SHADOW = "rgba(2, 132, 199, 0.15)"
    COLOR_HEADER_BG = "#f0f9ff"
    COLOR_HEADER_BORDER = "#0284c7"
    COLOR_HEADER_TEXT = "#0369a1"
    COLOR_PRIMARY_BTN = "#0284c7"
    COLOR_PRIMARY_HOVER = "#0369a1"
else:  # Maderas
    COLOR_BORDER = "#ea580c"
    COLOR_BADGE_BG = "rgba(249, 115, 22, 0.18)"
    COLOR_BADGE_TEXT = "#f97316"
    COLOR_BADGE_BORDER = "rgba(249, 115, 22, 0.4)"
    COLOR_RUNNING_BG = "#fff7ed"
    COLOR_RUNNING_BORDER = "#f97316"
    COLOR_RUNNING_SHADOW = "rgba(249, 115, 22, 0.15)"
    COLOR_HEADER_BG = "#fff7ed"
    COLOR_HEADER_BORDER = "#ea580c"
    COLOR_HEADER_TEXT = "#9a3412"
    COLOR_PRIMARY_BTN = "#ea580c"
    COLOR_PRIMARY_HOVER = "#c2410c"

# Estilos CSS Nivel Corporativo Dinámicos
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    /* Eliminar espacio superior nativo de Streamlit */
    [data-testid="stHeader"] {{
        display: none !important;
    }}
    
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }}

    [data-testid="stElementToolbar"] {{
        display: none !important;
    }}

    /* Barra Superior Unificada */
    .top-bar-container {{
        background: linear-gradient(135deg, #1c1917 0%, #292524 100%);
        border-left: 5px solid {COLOR_BORDER};
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}

    .main-title {{
        color: #ffffff;
        font-size: 18px;
        font-weight: 800;
        letter-spacing: 0.2px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
        text-transform: uppercase;
    }}

    .sub-title {{
        color: #a8a29e;
        font-size: 11px;
        font-weight: 500;
        margin-top: 3px;
    }}

    .badge-plant {{
        background: {COLOR_BADGE_BG};
        color: {COLOR_BADGE_TEXT};
        border: 1px solid {COLOR_BADGE_BORDER};
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }}

    /* Botones de Selección de Planta */
    div[data-testid="stHorizontalBlock"] .stButton > button {{
        border-radius: 6px !important;
        font-weight: 800 !important;
        font-size: 12px !important;
        height: 42px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Estilos Primarios Dinámicos */
    button[kind="primary"] {{
        background-color: {COLOR_PRIMARY_BTN} !important;
        border-color: {COLOR_PRIMARY_BTN} !important;
        color: #ffffff !important;
    }}
    
    button[kind="primary"]:hover {{
        background-color: {COLOR_PRIMARY_HOVER} !important;
        border-color: {COLOR_PRIMARY_HOVER} !important;
    }}

    /* Cards de Cronómetro */
    .timer-card {{
        background: #ffffff;
        border: 1px solid #e7e5e4;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}
    
    .timer-card-running {{
        background: {COLOR_RUNNING_BG};
        border: 2px solid {COLOR_RUNNING_BORDER};
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px {COLOR_RUNNING_SHADOW};
    }}

    .timer-label {{
        font-size: 11px;
        font-weight: 800;
        color: #57534e;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    
    .timer-digits {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 800;
        color: #1c1917;
        margin: 2px 0 6px 0;
    }}
    
    .timer-unit {{
        font-size: 12px;
        font-weight: 600;
        color: #78716c;
    }}

    .section-header {{
        background-color: {COLOR_HEADER_BG};
        border-left: 4px solid {COLOR_HEADER_BORDER};
        padding: 6px 12px;
        font-size: 11px;
        font-weight: 800;
        color: {COLOR_HEADER_TEXT};
        border-radius: 0 4px 4px 0;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .section-header-red {{
        background-color: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 6px 12px;
        font-size: 11px;
        font-weight: 800;
        color: #991b1b;
        border-radius: 0 4px 4px 0;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .footer-credits {{
        text-align: center;
        padding: 12px;
        margin-top: 20px;
        background: #fafaf9;
        border-top: 1px solid #e7e5e4;
        border-radius: 6px;
        color: #78716c;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    
    .footer-credits span {{
        color: {COLOR_PRIMARY_BTN};
        font-weight: 800;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. HEADER COMPACTO Y SELECTOR DE PLANTA
# ---------------------------------------------------------
col_head, col_sw1, col_sw2 = st.columns([2.4, 1, 1])

with col_sw1:
    if st.button("PLANTA METALMECÁNICA", use_container_width=True, type="primary" if planta_seleccionada == "Metalmecánica" else "secondary"):
        st.session_state["planta_activa"] = "Metalmecánica"
        st.rerun()

with col_sw2:
    if st.button("PLANTA DE MADERAS", use_container_width=True, type="primary" if planta_seleccionada == "Maderas" else "secondary"):
        st.session_state["planta_activa"] = "Maderas"
        st.rerun()

with col_head:
    badge_text = "METALMECÁNICA" if planta_seleccionada == "Metalmecánica" else "MADERAS"
    st.markdown(f"""
        <div class="top-bar-container">
            <div>
                <div class="main-title">
                    CONTROL DE TIEMPOS Y MÉTODOS 
                    <span class="badge-plant">{badge_text}</span>
                </div>
                <div class="sub-title">Captura en Vivo y Muestreo Estándar de Producción</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Asignar Parámetros según la Planta Activa
if planta_seleccionada == "Metalmecánica":
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
        "3.0 mm (1/8\")", 
        "4.5 mm (3/16\")", 
        "6.0 mm (1/4\")",
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

# ---------------------------------------------------------
# 2. GESTIÓN DE OPERARIOS Y ESTADO DE SESIÓN
# ---------------------------------------------------------
if "hora_inicio_registro" not in st.session_state or st.session_state["hora_inicio_registro"] is None:
    st.session_state["hora_inicio_registro"] = obtener_hora_bogota()

def cargar_operarios():
    operarios = []
    if os.path.exists(ARCHIVO_OPERARIOS):
        try:
            with open(ARCHIVO_OPERARIOS, "r", encoding="utf-8") as f:
                operarios = json.load(f)
        except:
            operarios = []
    
    if os.path.exists(ARCHIVO_EXCEL):
        try:
            df = pd.read_excel(ARCHIVO_EXCEL)
            if "Operario" in df.columns:
                nombres_excel = df["Operario"].dropna().astype(str).str.strip().unique().tolist()
                for item in nombres_excel:
                    if item and item not in operarios:
                        operarios.append(item)
        except:
            pass
            
    return sorted(list(set(operarios)))

def guardar_operarios(lista_operarios):
    with open(ARCHIVO_OPERARIOS, "w", encoding="utf-8") as f:
        json.dump(sorted(list(set(lista_operarios))), f, ensure_ascii=False, indent=4)

st.session_state["lista_operarios"] = cargar_operarios()

cronometros = ["Setup", "Ciclo Real", "Descargue", "Paros", "Espera Operario"]
for c in cronometros:
    if f"tiempo_{c}" not in st.session_state:
        st.session_state[f"tiempo_{c}"] = 0.0
    if f"corriendo_{c}" not in st.session_state:
        st.session_state[f"corriendo_{c}"] = False
    if f"inicio_{c}" not in st.session_state:
        st.session_state[f"inicio_{c}"] = None

def resetear_cronometros():
    for c in cronometros:
        st.session_state[f"tiempo_{c}"] = 0.0
        st.session_state[f"corriendo_{c}"] = False
        st.session_state[f"inicio_{c}"] = None
    st.session_state["hora_inicio_registro"] = obtener_hora_bogota()

# ---------------------------------------------------------
# 3. FORMULARIO DE ORDEN DE TRABAJO (OP)
# ---------------------------------------------------------
with st.expander(f"DATOS DE LA ORDEN DE TRABAJO (OP) - PLANTA {planta_seleccionada.upper()}", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        opciones_operario = ["Seleccionar...", "Registrar Nuevo Operario..."] + st.session_state["lista_operarios"]
        
        c_sel, c_del = st.columns([5, 1])
        with c_sel:
            operario_sel = st.selectbox("Operario / Tomador de Tiempos", opciones_operario)
        
        with c_del:
            st.write("") 
            st.write("")
            if operario_sel not in ["Seleccionar...", "Registrar Nuevo Operario..."] and operario_sel:
                if st.button("ELIMINAR", help=f"Eliminar '{operario_sel}' de la lista guardada"):
                    st.session_state["lista_operarios"].remove(operario_sel)
                    guardar_operarios(st.session_state["lista_operarios"])
                    st.toast(f"Operario '{operario_sel}' eliminado de la lista.")
                    st.rerun()

        if operario_sel == "Registrar Nuevo Operario...":
            operario = st.text_input("Nombre y Apellido Completo", placeholder="Ej: Juan Pérez").strip()
        elif operario_sel != "Seleccionar...":
            operario = operario_sel
        else:
            operario = ""

        orden = st.text_input("Orden / OP", placeholder="Ej: OP-2026-001")
        fecha = st.date_input("Fecha de Toma", obtener_fecha_bogota())
        turno = st.selectbox("Turno", ["Día", "Tarde", "Noche"])
    
    with col2:
        maquina = st.selectbox("Máquina / Estación", MAQUINAS_LIST)
        nombre_general = st.text_input("Proyecto / Producto", placeholder="Ej: Estantería Módulo B")
        detalle_pieza = st.text_input("Detalle Pieza / Nesting", placeholder="Ej: Lateral Izquierdo 18mm")
        material = st.selectbox("Material", MATERIALES_LIST)

    with col3:
        calibre_sel = st.selectbox("Espesor / Calibre", CALIBRES_LIST)
        if calibre_sel == "OTRO / LIBRE (Escribir en vivo)":
            calibre = st.text_input("Especificar Espesor Manual", placeholder="Ej: 15 mm / 5/8\"")
        else:
            calibre = calibre_sel

        cant_general = st.number_input("Cantidad Lote Total", min_value=1, step=1, value=1)
        cant_piezas_ok = st.number_input("Piezas Procesadas OK", min_value=0, step=1, value=1)
        tiempo_estandar = st.number_input("Tiempo Estándar (Min)", min_value=0.0, step=0.1, value=0.0)

# ---------------------------------------------------------
# 4. CRONOMETRAJE EN VIVO
# ---------------------------------------------------------
with st.expander("TOMADOR DE TIEMPOS EN VIVO", expanded=True):
    
    def render_cronometro(nombre, clave):
        esta_corriendo = st.session_state[f"corriendo_{clave}"]
        tiempo_acumulado = st.session_state[f"tiempo_{clave}"]
        
        if esta_corriendo and st.session_state[f"inicio_{clave}"] is not None:
            tiempo_actual = tiempo_acumulado + (time.time() - st.session_state[f"inicio_{clave}"])
        else:
            tiempo_actual = tiempo_acumulado
        
        minutos = int(tiempo_actual // 60)
        segundos = int(tiempo_actual % 60)
        
        card_class = "timer-card-running" if esta_corriendo else "timer-card"
        
        st.markdown(f'''
            <div class="{card_class}">
                <div class="timer-label">{nombre}</div>
                <div class="timer-digits">{minutos:02d}:{segundos:02d} <span class="timer-unit">min</span></div>
            </div>
        ''', unsafe_allow_html=True)
        
        b_toggle, b_reset = st.columns([3, 1])
        
        with b_toggle:
            label_btn = "PAUSAR" if esta_corriendo else "INICIAR"
            tipo_btn = "primary" if not esta_corriendo else "secondary"
            
            if st.button(label_btn, key=f"toggle_{clave}", type=tipo_btn, use_container_width=True):
                if esta_corriendo:
                    st.session_state[f"tiempo_{clave}"] += time.time() - st.session_state[f"inicio_{clave}"]
                    st.session_state[f"corriendo_{clave}"] = False
                    st.session_state[f"inicio_{clave}"] = None
                else:
                    st.session_state[f"inicio_{clave}"] = time.time()
                    st.session_state[f"corriendo_{clave}"] = True
                st.rerun()

        with b_reset:
            if st.button("RESET", key=f"reset_{clave}", help="Reiniciar cronómetro", use_container_width=True):
                st.session_state[f"tiempo_{clave}"] = 0.0
                st.session_state[f"corriendo_{clave}"] = False
                st.session_state[f"inicio_{clave}"] = None
                st.rerun()
                
        return round(tiempo_actual / 60.0, 2)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-header">TIEMPOS PRODUCTIVOS</div>', unsafe_allow_html=True)
        t_setup = render_cronometro("SETUP / MONTAJE (MIN)", "Setup")
        t_ciclo = render_cronometro("CICLO REAL (MIN)", "Ciclo Real")
        t_descargue = render_cronometro("DESCARGUE / POSTCORTE (MIN)", "Descargue")

    with col_right:
        st.markdown('<div class="section-header-red">TIEMPOS IMPRODUCTIVOS / PAROS</div>', unsafe_allow_html=True)
        t_espera = render_cronometro("OPERARIO EN ESPERA (MIN)", "Espera Operario")
        t_paros = render_cronometro("MUERTO / PARO MÁQUINA (MIN)", "Paros")
        motivo_paro = st.selectbox("MOTIVO PRINCIPAL DEL PARO", MOTIVOS_PARO_LIST)

st.markdown("---")

# ---------------------------------------------------------
# 5. GUARDADO DE REGISTRO EN EXCEL
# ---------------------------------------------------------
if st.button(f"GUARDAR REGISTRO EN EXCEL (PLANTA {planta_seleccionada.upper()})", use_container_width=True, type="primary"):
    if not orden or not maquina:
        st.error("Ingrese la 'Orden / OP' y seleccione la 'Máquina' para guardar.")
    elif not operario:
        st.error("Ingrese o seleccione el nombre del 'Operario / Tomador de Tiempos'.")
    else:
        if operario not in st.session_state["lista_operarios"]:
            st.session_state["lista_operarios"].append(operario)
            guardar_operarios(st.session_state["lista_operarios"])

        hora_inicio = st.session_state.get("hora_inicio_registro", obtener_hora_bogota())
        hora_fin = obtener_hora_bogota()

        nuevo_registro = {
            "Planta": str(planta_seleccionada),
            "Operario": str(operario),
            "Orden": str(orden),
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Turno": str(turno),
            "Máquina": str(maquina),
            "Proyecto": str(nombre_general),
            "Detalle Pieza": str(detalle_pieza),
            "Material": str(material),
            "Espesor/Calibre": str(calibre),
            "Cantidad Lote": int(cant_general),
            "Piezas OK": int(cant_piezas_ok),
            "Setup (min)": float(t_setup),
            "Tiempo Estándar (min)": float(tiempo_estandar),
            "Ciclo Real (min)": float(t_ciclo),
            "Espera Operario (min)": float(t_espera),
            "Paro Máquina (min)": float(t_paros),
            "Descargue (min)": float(t_descargue),
            "Motivo Paro": str(motivo_paro),
            "Hora Inicio": str(hora_inicio),
            "Hora Fin": str(hora_fin)
        }
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        
        if os.path.exists(ARCHIVO_EXCEL):
            try:
                df_ex = pd.read_excel(ARCHIVO_EXCEL)
                df_final = pd.concat([df_ex, df_nuevo], ignore_index=True)
            except:
                df_final = df_nuevo
        else:
            df_final = df_nuevo
            
        cols_resto = [col for col in df_final.columns if col not in ["Hora Inicio", "Hora Fin"]]
        df_final = df_final[cols_resto + ["Hora Inicio", "Hora Fin"]]
        
        df_final = df_final.dropna(subset=["Orden"])
        df_final.to_excel(ARCHIVO_EXCEL, index=False)
        
        st.success(f"Registro de la Orden {orden} en Planta {planta_seleccionada} guardado con éxito.")

        tiempo_total = float(t_setup) + float(t_ciclo) + float(t_descargue) + float(t_espera) + float(t_paros)
        tiempo_productivo = float(t_ciclo)
        tiempo_improductivo = float(t_espera) + float(t_paros)

        if tiempo_total > 0:
            eficiencia = (tiempo_productivo / tiempo_total) * 100
            desperdicio = (tiempo_improductivo / tiempo_total) * 100
            
            st.markdown('<div class="section-header">ANÁLISIS DE EFICIENCIA DEL REGISTRO CAPTURADO</div>', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tiempo Total Operativo", f"{tiempo_total:.1f} min")
            m2.metric("Tiempo Productivo", f"{tiempo_productivo:.1f} min")
            m3.metric("Eficiencia (Valor Agregado)", f"{eficiencia:.1f}%")
            m4.metric("Desperdicio (Paros/Espera)", f"{desperdicio:.1f}%")

        resetear_cronometros()
        st.rerun()

# ---------------------------------------------------------
# 6. HISTORIAL Y EXPORTACIÓN
# ---------------------------------------------------------
st.markdown(f'<div class="section-header">HISTORIAL Y MATRIZ DE TIEMPOS - PLANTA {planta_seleccionada.upper()}</div>', unsafe_allow_html=True)

if os.path.exists(ARCHIVO_EXCEL):
    df_ver = pd.read_excel(ARCHIVO_EXCEL)
    df_ver_limpio = df_ver.dropna(subset=["Orden"]).reset_index(drop=True)
    
    cols_resto = [col for col in df_ver_limpio.columns if col not in ["Hora Inicio", "Hora Fin"]]
    df_ver_limpio = df_ver_limpio[cols_resto + ["Hora Inicio", "Hora Fin"]]
    
    st.dataframe(df_ver_limpio, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("DEPARTAMENTO DE COSTOS - Base de datos protegida")
    
    col_pass, col_btn = st.columns([1, 2])
    
    with col_pass:
        clave_ingresada = st.text_input("Ingresa el PIN de autorización para descargar:", type="password", placeholder="Ingresa PIN...", key="pin_download")
        borrar_tras_descarga = st.checkbox("Limpiar / Borrar historial tras exportar", value=True)

    with col_btn:
        st.write("") 
        st.write("")
        if clave_ingresada.strip() == "190520":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_ver_limpio.to_excel(writer, index=False, sheet_name=f'Tiempos_{planta_seleccionada[:5]}')
            buffer.seek(0)
            
            nombre_archivo_descarga = f"Registro_{planta_seleccionada.replace(' ', '_')}_{datetime.date.today()}.xlsx"
            
            descargado = st.download_button(
                label=f"DESCARGAR MATRIZ {planta_seleccionada.upper()}",
                data=buffer,
                file_name=nombre_archivo_descarga,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
            
            if descargado and borrar_tras_descarga:
                if os.path.exists(ARCHIVO_EXCEL):
                    os.remove(ARCHIVO_EXCEL)
                st.success(f"Historial de Planta {planta_seleccionada} borrado correctamente.")
                time.sleep(1)
                st.rerun()

        elif clave_ingresada != "":
            st.error("PIN incorrecto. Acceso denegado.")
        else:
            st.warning("Ingresa la contraseña autorizada para habilitar la descarga.")

else:
    st.info(f"Aún no hay registros consolidados para Planta {planta_seleccionada}.")

# Pie de página
st.markdown("""
    <div class="footer-credits">
        Desarrollado por <span>Tatiana Almario • Asistente de Costos y Métodos</span>
    </div>
""", unsafe_allow_html=True)

# Bucle de refresco
if any(st.session_state[f"corriendo_{c}"] for c in cronometros):
    time.sleep(1)
    st.rerun()
