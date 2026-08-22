import streamlit as st
import pandas as pd
import datetime
import time
import os
import io

# Configuración de Página
st.set_page_config(
    page_title="Control de Tiempos & Métodos | Planta",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de Nivel Ingeniería
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Encabezado Principal */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 20px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #334155;
    }
    
    .main-title {
        color: #ffffff;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 500;
        margin-top: 4px;
    }
    
    /* Headers de Sección */
    .section-header {
        background-color: #f1f5f9;
        border-left: 5px solid #2563eb;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 800;
        color: #0f172a;
        border-radius: 0 8px 8px 0;
        margin-bottom: 16px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .section-header-red {
        background-color: #fef2f2;
        border-left: 5px solid #dc2626;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 800;
        color: #991b1b;
        border-radius: 0 8px 8px 0;
        margin-bottom: 16px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Cards Cronómetros */
    .timer-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    
    .timer-card-running {
        background: #f0fdf4;
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
    }

    .timer-label {
        font-size: 11px;
        font-weight: 800;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    
    .timer-digits {
        font-family: 'JetBrains Mono', monospace;
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        margin: 2px 0 8px 0;
        letter-spacing: -1px;
    }
    
    .timer-unit {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
    }

    /* Botones personalizados */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        height: 42px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Footer */
    .footer-credits {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        background: #f8fafc;
        border-top: 1px solid #e2e8f0;
        border-radius: 8px;
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
    }
    .footer-credits span {
        color: #0284c7;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <div class="main-title">⏱️ SISTEMA DE CAPTURA Y TOMA DE TIEMPOS DE PRODUCCIÓN</div>
        <div class="sub-title">Ingeniería de Métodos, Tiempos Estándar y Muestreo en Planta</div>
    </div>
""", unsafe_allow_html=True)

# Catalogos Predeterminados
MAQUINAS_LIST = [
    "Punzonadora Trumpf Trumatic 2000R",
    "Cortadora Láser CNC (MT 36) - F 3015",
    "Plegadora Durma CNC",
    "Dobladora Dener",
    "Soldadura MIG",
    "Soldadura PUNTO",
    "Horno Pintura",
    "Soldadura LASER",
    "Otra Máquina / Estación"
]

MATERIALES_LIST = [
    "CR (Cold Rolled)",
    "HR (Hot Rolled)",
    "Acero Inoxidable",
    "Aluminio",
    "Galvanizado",
    "Otro Material"
]

CALIBRES_LIST = [
    "0.9 mm (C20)", "1.2 mm (C18)", "1.5 mm (C16)", "1.9 mm (C14)", 
    "2.5 mm (C12)", "3.0 mm (1/8\")", "4.5 mm (3/16\")", "6.0 mm (1/4\")",
    "✍️ OTRO / LIBRE (Escribir al tomar tiempos)"
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

# Inicialización Session State para Cronómetros
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

# PARÁMETROS DE LA ORDEN DE TRABAJO
with st.expander("📌 PARÁMETROS GENERALES Y ESPECIFICACIONES DE LA OP", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        orden = st.text_input("ORDEN / OP / PEDIDO", placeholder="Ej: OP-10450")
        fecha = st.date_input("FECHA DE TOMA", datetime.date.today())
        turno = st.selectbox("TURNO OPERATIVO", ["Día", "Tarde", "Noche"])
        maquina = st.selectbox("MÁQUINA / EQUIPO", MAQUINAS_LIST)
    
    with c2:
        nombre_general = st.text_input("PRODUCTO / DESCRIPCIÓN", placeholder="Ej: BARRA ALTA TIPO COWORKING")
        detalle_pieza = st.text_input("DETALLE DE PIEZA / LOTE", placeholder="Ej: ESTRUCTURA BASE LOTE 10 UN")
        material = st.selectbox("TIPO DE MATERIAL", MATERIALES_LIST)

    with c3:
        calibre_sel = st.selectbox("CALIBRE DE LÁMINA / ESTRUCTURA", CALIBRES_LIST)
        
        # Opción flexible para escribir calibres no registrados
        if calibre_sel == "✍️ OTRO / LIBRE (Escribir al tomar tiempos)":
            calibre = st.text_input("ESPECIFIQUE CALIBRE LIBRE", placeholder="Ej: 8.0 mm / Calibre 22 Especial")
        else:
            calibre = calibre_sel
            
        cant_general = st.number_input("CANTIDAD TOTAL LOTE", min_value=1, step=1, value=1)

    with c4:
        cant_piezas_ok = st.number_input("PIEZAS PROCESADAS OK", min_value=0, step=1, value=1)
        tiempo_estandar = st.number_input("TIEMPO ESTÁNDAR ESTIMADO (MIN)", min_value=0.0, step=0.1, value=0.0, help="Opcional")

# ÁREA DE CRONOMETRAJE EN VIVO
with st.expander("⏱️ CAPTURA DE TIEMPOS EN VIVO (MODO PLANTA)", expanded=True):
    
    def render_cronometro(nombre, clave):
        esta_corriendo = st.session_state[f"corriendo_{clave}"]
        tiempo_acumulado = st.session_state[f"tiempo_{clave}"]
        
        if esta_corriendo:
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
        
        # BOTÓN UNIFICADO: Alterna entre Iniciar y Pausar
        with b_toggle:
            label_btn = "⏸ PAUSAR TIEMPO" if esta_corriendo else "▶ INICIAR TIEMPO"
            tipo_btn = "primary" if not esta_corriendo else "secondary"
            
            if st.button(label_btn, key=f"toggle_{clave}", type=tipo_btn, use_container_width=True):
                if esta_corriendo:
                    # Pausar y congelar el acumulado
                    st.session_state[f"tiempo_{clave}"] += time.time() - st.session_state[f"inicio_{clave}"]
                    st.session_state[f"corriendo_{clave}"] = False
                else:
                    # Iniciar conteo
                    st.session_state[f"inicio_{clave}"] = time.time()
                    st.session_state[f"corriendo_{clave}"] = True
                st.rerun()

        # Botón pequeño de reinicio
        with b_reset:
            if st.button("🔄", key=f"reset_{clave}", help="Reiniciar este cronómetro a cero", use_container_width=True):
                st.session_state[f"tiempo_{clave}"] = 0.0
                st.session_state[f"corriendo_{clave}"] = False
                st.rerun()
                
        return round(tiempo_actual / 60.0, 2)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-header">⚙️ TIEMPOS PRODUCTIVOS Y OPERATIVOS</div>', unsafe_allow_html=True)
        t_setup = render_cronometro("TIEMPO DE SETUP / MONTAJE (MIN)", "Setup")
        t_ciclo = render_cronometro("TIEMPO DE CICLO REAL (MIN)", "Ciclo Real")
        t_descargue = render_cronometro("TIEMPO DE DESCARGUE / POSTCORTE (MIN)", "Descargue")

    with col_right:
        st.markdown('<div class="section-header-red">⚠️ TIEMPOS IMPRODUCTIVOS Y PAROS</div>', unsafe_allow_html=True)
        t_espera = render_cronometro("OPERARIO EN ESPERA / OCIOSIDAD (MIN)", "Espera Operario")
        t_paros = render_cronometro("TIEMPO MUERTO / PARO MÁQUINA (MIN)", "Paros")
        motivo_paro = st.selectbox("MOTIVO PRINCIPAL DEL PARO", MOTIVOS_PARO_LIST)

# Refresco dinámico automático si hay algún cronómetro activo
if any(st.session_state[f"corriendo_{c}"] for c in cronometros):
    time.sleep(1)
    st.rerun()

st.markdown("---")

# GUARDADO Y CONSOLIDACIÓN DE DATOS
if st.button("💾 GUARDAR REGISTRO Y CONSOLIDAR EN EXCEL", use_container_width=True, type="primary"):
    if not orden or not maquina:
        st.error("⚠️ Atención: Debes ingresar al menos la 'ORDEN / OP' y seleccionar la 'MÁQUINA' antes de guardar.")
    else:
        archivo_excel = "Registro_Produccion.xlsx"
        
        nuevo_registro = {
            "ORDEN / PEDIDO": str(orden),
            "FECHA": fecha.strftime("%Y-%m-%d"),
            "TURNO": str(turno),
            "MAQUINA": str(maquina),
            "NOMBRE GENERAL/PRODUCTO": str(nombre_general),
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
        st.success(f"✅ ¡Registro guardado exitosamente! Orden {orden} almacenada correctamente.")

# VISTA PREVIA Y EXPORTACIÓN DEL HISTORIAL
st.markdown('<div class="section-header">📊 HISTORIAL DE TIEMPOS REGISTRADOS (MATRIZ EXCEL)</div>', unsafe_allow_html=True)
archivo_excel = "Registro_Produccion.xlsx"

if os.path.exists(archivo_excel):
    df_ver = pd.read_excel(archivo_excel)
    st.dataframe(df_ver, use_container_width=True)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_ver.to_excel(writer, index=False, sheet_name='Matriz de Tiempos')
    buffer.seek(0)
    
    st.download_button(
        label="📥 DESCARGAR MATRIZ COMPLETA EN EXCEL (.XLSX)",
        data=buffer,
        file_name="Registro_Produccion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("Aún no se han consolidado registros en la sesión actual.")

# CRÉDITOS Y FIRMA PROFESIONAL
st.markdown("""
    <div class="footer-credits">
        ⚙️ Sistema de Control de Tiempos y Métodos de Producción <br>
        Desarrollado por <span>Tatiana Almario • Asistente de Costos y Métodos</span>
    </div>
""", unsafe_allow_html=True)
