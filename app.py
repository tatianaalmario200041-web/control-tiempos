import streamlit as st
import pandas as pd
import datetime
import time
import os
import io

st.set_page_config(
    page_title="Control de Producción y Métodos",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Profesionales
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        color: #0f172a;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    
    .sub-title {
        color: #64748b;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 18px;
    }
    
    .card-header {
        background-color: #f8fafc;
        border-left: 4px solid #0284c7;
        padding: 8px 12px;
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
        border-radius: 0 6px 6px 0;
        margin-bottom: 15px;
    }
    
    /* Cronómetros */
    .timer-container-prod {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #2563eb;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    
    .timer-container-stop {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #dc2626;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    
    .timer-label {
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .timer-digits {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0 8px 0;
    }
    
    .timer-unit {
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
    }

    /* Estilos Botones Custom */
    div.stButton > button {
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        height: 36px !important;
        transition: all 0.2s ease !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">CONTROL DE PRODUCCIÓN Y TOMA DE TIEMPOS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Planta Operativa • Captura de Tiempos & Métodos en Vivo</div>', unsafe_allow_html=True)

# Listas oficiales tomadas del módulo Parámetros y Catálogos
MAQUINAS_LIST = [
    "Punzonadora Trumpf Trumatic 2000R",
    "Cortadora Láser CNC (MT 36) - F 3015",
    "Plegadora Durma CNC",
    "Dobladora Dener",
    "Soldadura MIG",
    "Soldadura PUNTO",
    "Horno Pintura",
    "Soldadura LASER"
]

MATERIALES_LIST = [
    "CR (Cold Rolled)",
    "HR (Hot Rolled)",
    "Acero Inoxidable",
    "Aluminio"
]

CALIBRES_LIST = [
    "0.9 mm", "1.2 mm", "1.5 mm", "2.0 mm", "2.5 mm", "3.0 mm",
    "C14", "C16", "C18", "C20", "C22"
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
    "Otro / Imprevisto",
    "Espera de material / Sin orden trab"
]

# Inicialización Session State
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

# PARÁMETROS DE LA ORDEN
with st.expander("DATOS GENERALES DE LA ORDEN", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        orden = st.text_input("ORDEN / PEDIDO")
        fecha = st.date_input("FECHA", datetime.date.today())
        turno = st.selectbox("TURNO", ["Día", "Tarde", "Noche"])
        maquina = st.selectbox("MAQUINA", MAQUINAS_LIST)
    
    with c2:
        nombre_general = st.text_input("NOMBRE GENERAL/producto", placeholder="Ej: BARRA ALTA TIPO COWORKING...")
        detalle_pieza = st.text_input("DETALLE PIEZA/LOTE", placeholder="Ej: LOTE 10 UNIDADES")
        material = st.selectbox("MATERIAL", MATERIALES_LIST)

    with c3:
        calibre = st.selectbox("CALIBRE", CALIBRES_LIST)
        cant_general = st.number_input("CANTIDAD GENERAL", min_value=1, step=1, value=1)
        cant_piezas_ok = st.number_input("CANTIDAD PIEZAS OK", min_value=0, step=1, value=1)

    with c4:
        tiempo_estandar = st.number_input("TIEMPO CICLO ESTÁNDAR (MIN)", min_value=0.0, step=0.1, value=0.0, help="Opcional: Si lo asigna Programación/Ingeniería")

# CRONOMETRAJE EN PISO
with st.expander("CRONOMETRAJE EN PISO DE PLANTA", expanded=True):
    
    def render_cronometro(nombre, clave, es_paros=False):
        tiempo_actual = st.session_state[f"tiempo_{clave}"]
        if st.session_state[f"corriendo_{clave}"]:
            tiempo_actual += time.time() - st.session_state[f"inicio_{clave}"]
        
        minutos = int(tiempo_actual // 60)
        segundos = int(tiempo_actual % 60)
        
        card_class = "timer-container-stop" if es_paros else "timer-container-prod"
        
        st.markdown(f'''
            <div class="{card_class}">
                <div class="timer-label">{nombre}</div>
                <div class="timer-digits">{minutos:02d}:{segundos:02d} <span class="timer-unit">min</span></div>
            </div>
        ''', unsafe_allow_html=True)
        
        b1, b2, b3 = st.columns([1, 1, 1])
        with b1:
            if st.button("▶ Iniciar", key=f"start_{clave}", type="primary" if not st.session_state[f"corriendo_{clave}"] else "secondary"):
                if not st.session_state[f"corriendo_{clave}"]:
                    st.session_state[f"inicio_{clave}"] = time.time()
                    st.session_state[f"corriendo_{clave}"] = True
                    st.rerun()
        with b2:
            if st.button("⏸ Pausar", key=f"pause_{clave}"):
                if st.session_state[f"corriendo_{clave}"]:
                    st.session_state[f"tiempo_{clave}"] += time.time() - st.session_state[f"inicio_{clave}"]
                    st.session_state[f"corriendo_{clave}"] = False
                    st.rerun()
        with b3:
            if st.button("🔄 Reiniciar", key=f"reset_{clave}"):
                st.session_state[f"tiempo_{clave}"] = 0.0
                st.session_state[f"corriendo_{clave}"] = False
                st.rerun()
                
        return round(tiempo_actual / 60.0, 2)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="card-header">TIEMPOS PRODUCTIVOS</div>', unsafe_allow_html=True)
        t_setup = render_cronometro("SETUP (MIN)", "Setup", es_paros=False)
        t_ciclo = render_cronometro("CICLO REAL (MIN)", "Ciclo Real", es_paros=False)
        t_descargue = render_cronometro("DESCARGUE (POSTCORTE) (MIN)", "Descargue", es_paros=False)

    with col_right:
        st.markdown('<div class="card-header">TIEMPOS IMPRODUCTIVOS / PAROS</div>', unsafe_allow_html=True)
        t_espera = render_cronometro("OPERARIO EN ESPERA (MIN)", "Espera Operario", es_paros=True)
        t_paros = render_cronometro("MUERTO / PAROS (MIN)", "Paros", es_paros=True)
        motivo_paro = st.selectbox("MOTIVO PRINCIPAL PARO", MOTIVOS_PARO_LIST)

# Refresco dinámico
alguno_activo = any(st.session_state[f"corriendo_{c}"] for c in cronometros)
if alguno_activo:
    time.sleep(1)
    st.rerun()

st.markdown("---")

# GUARDADO Y MATRIZ DE DATOS
if st.button("💾 GUARDAR REGISTRO Y PREPARAR EXCEL", use_container_width=True, type="primary"):
    if not orden or not maquina:
        st.error("Error: Los campos 'ORDEN / PEDIDO' y 'MAQUINA' son requeridos.")
    else:
        archivo_excel = "Registro_Produccion.xlsx"
        
        nuevo_registro = {
            "ORDEN / PEDIDO": str(orden),
            "FECHA": fecha.strftime("%Y-%m-%d"),
            "TURNO": str(turno),
            "MAQUINA": str(maquina),
            "NOMBRE GENERAL/producto": str(nombre_general),
            "DETALLE PIEZA/LOTE": str(detalle_pieza),
            "MATERIAL": str(material),
            "CALIBRE": str(calibre),
            "CANTIDAD GENERAL": int(cant_general),
            "CANTIDAD PIEZAS OK": int(cant_piezas_ok),
            "TIEMPO SETUP (MIN)": float(t_setup),
            "TIEMPO CICLO ESTÁNDAR (MIN)": float(tiempo_estandar),
            "TIEMPO CICLO REAL (MIN)": float(t_ciclo),
            "TIEMPO OPERARIO EN ESPERA (MIN)": float(t_espera),
            "TIEMPO MUERTO / PAROS (MIN)": float(t_paros),
            "TIEMPO DESCARGUE (POSTCORTE) (MIN)": float(t_descargue),
            "MOTIVO PRINCIPAL PARO": str(motivo_paro)
        }
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        if os.path.exists(archivo_excel):
            df_ex = pd.read_excel(archivo_excel)
            df_final = pd.concat([df_ex, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final.to_excel(archivo_excel, index=False)
        resetear_cronometros()
        st.success(f"¡Registro exitoso! Orden {orden} consolidada en la matriz.")

# VISTA PREVIA Y EXPORTACIÓN
st.markdown('<div class="card-header">REGISTROS CRONOMETRADOS (HISTORIAL EXPORTABLE)</div>', unsafe_allow_html=True)
archivo_excel = "Registro_Produccion.xlsx"

if os.path.exists(archivo_excel):
    df_ver = pd.read_excel(archivo_excel)
    st.dataframe(df_ver, use_container_width=True)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_ver.to_excel(writer, index=False, sheet_name='Registro de Producción')
    buffer.seek(0)
    
    st.download_button(
        label="📥 DESCARGAR EXCEL PARA PEGAR EN ARCHIVO MAESTRO",
        data=buffer,
        file_name="Registro_Produccion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("Aún no hay registros tomados en este turno.")
