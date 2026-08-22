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
    initial_sidebar_state="collapsed"
)

# Estilos CSS Nivel Ingeniería
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header principal compacto */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 16px 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    
    .main-title {
        color: #ffffff;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.3px;
        margin: 0;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 500;
        margin-top: 2px;
    }
    
    /* Cards Cronómetros */
    .timer-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .timer-card-running {
        background: #f0fdf4;
        border: 2px solid #22c55e;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(34, 197, 94, 0.12);
    }

    .timer-label {
        font-size: 11px;
        font-weight: 800;
        color: #475569;
        text-transform: uppercase;
    }
    
    .timer-digits {
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 800;
        color: #0f172a;
        margin: 2px 0 6px 0;
    }
    
    .timer-unit {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
    }

    .section-header {
        background-color: #f1f5f9;
        border-left: 4px solid #0284c7;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 800;
        color: #0f172a;
        border-radius: 0 6px 6px 0;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    .section-header-red {
        background-color: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 800;
        color: #991b1b;
        border-radius: 0 6px 6px 0;
        margin-bottom: 12px;
        text-transform: uppercase;
    }

    div.stButton > button {
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        height: 40px !important;
    }

    .footer-credits {
        text-align: center;
        padding: 15px;
        margin-top: 25px;
        background: #f8fafc;
        border-top: 1px solid #e2e8f0;
        border-radius: 6px;
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

# Encabezado
st.markdown("""
    <div class="header-container">
        <div class="main-title">⏱️ CONTROL DE TIEMPOS Y MÉTODOS DE PRODUCCIÓN</div>
        <div class="sub-title">Captura en Vivo y Muestreo Estándar en Planta</div>
    </div>
""", unsafe_allow_html=True)

# Listas Predeterminadas
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
    "0.9 mm (C20)", "1.2 mm (C18)", "1.5 mm (C16)", "1.9 mm (C14)", 
    "2.5 mm (C12)", "3.0 mm (1/8\")", "4.5 mm (3/16\")", "6.0 mm (1/4\")",
    "✍️ OTRO / LIBRE (Escribir en vivo)"
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

# Session State para Cronómetros
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

# PARÁMETROS ORGANIZADOS EN 3 COLUMNAS LIMPIAS
with st.expander("📌 DATOS DE LA ORDEN DE TRABAJO (OP)", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        orden = st.text_input("Orden / OP", placeholder="Ej: 2345678")
        fecha = st.date_input("Fecha de Toma", datetime.date.today())
        turno = st.selectbox("Turno", ["Día", "Tarde", "Noche"])
        maquina = st.selectbox("Máquina / Estación", MAQUINAS_LIST)
    
    with col2:
        nombre_general = st.text_input("Proyecto / Producto", placeholder="Ej: Mesa de Juntas")
        detalle_pieza = st.text_input("Detalle Pieza / Nesting", placeholder="Ej: Nesting Completo - 1 láminas")
        material = st.selectbox("Material", MATERIALES_LIST)
        
        calibre_sel = st.selectbox("Calibre", CALIBRES_LIST)
        if calibre_sel == "✍️ OTRO / LIBRE (Escribir en vivo)":
            calibre = st.text_input("Especificar Calibre Manual", placeholder="Ej: 4.5 mm / 1/4\"")
        else:
            calibre = calibre_sel

    with col3:
        cant_general = st.number_input("Cantidad Lote Total", min_value=1, step=1, value=1)
        cant_piezas_ok = st.number_input("Piezas Procesadas OK", min_value=0, step=1, value=1)
        tiempo_estandar = st.number_input("Tiempo Estándar (Min)", min_value=0.0, step=0.1, value=0.0)

# ÁREA DE CRONOMETRAJE EN VIVO
with st.expander("⏱️ TOMADOR DE TIEMPOS EN VIVO", expanded=True):
    
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
        
        with b_toggle:
            label_btn = "⏸ PAUSAR" if esta_corriendo else "▶ INICIAR"
            tipo_btn = "primary" if not esta_corriendo else "secondary"
            
            if st.button(label_btn, key=f"toggle_{clave}", type=tipo_btn, use_container_width=True):
                if esta_corriendo:
                    st.session_state[f"tiempo_{clave}"] += time.time() - st.session_state[f"inicio_{clave}"]
                    st.session_state[f"corriendo_{clave}"] = False
                else:
                    st.session_state[f"inicio_{clave}"] = time.time()
                    st.session_state[f"corriendo_{clave}"] = True
                st.rerun()

        with b_reset:
            if st.button("🔄", key=f"reset_{clave}", help="Reiniciar cronómetro", use_container_width=True):
                st.session_state[f"tiempo_{clave}"] = 0.0
                st.session_state[f"corriendo_{clave}"] = False
                st.rerun()
                
        return round(tiempo_actual / 60.0, 2)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-header">⚙️ TIEMPOS PRODUCTIVOS</div>', unsafe_allow_html=True)
        t_setup = render_cronometro("SETUP / MONTAJE (MIN)", "Setup")
        t_ciclo = render_cronometro("CICLO REAL (MIN)", "Ciclo Real")
        t_descargue = render_cronometro("DESCARGUE / POSTCORTE (MIN)", "Descargue")

    with col_right:
        st.markdown('<div class="section-header-red">⚠️ TIEMPOS IMPRODUCTIVOS / PAROS</div>', unsafe_allow_html=True)
        t_espera = render_cronometro("OPERARIO EN ESPERA (MIN)", "Espera Operario")
        t_paros = render_cronometro("MUERTO / PARO MÁQUINA (MIN)", "Paros")
        motivo_paro = st.selectbox("MOTIVO PRINCIPAL DEL PARO", MOTIVOS_PARO_LIST)

# Refresco de cronómetros
if any(st.session_state[f"corriendo_{c}"] for c in cronometros):
    time.sleep(1)
    st.rerun()

st.markdown("---")

# GUARDADO DE REGISTRO Y CÁLCULO DE EFICIENCIA (%)
if st.button("💾 GUARDAR REGISTRO Y ACTUALIZAR EXCEL", use_container_width=True, type="primary"):
    if not orden or not maquina:
        st.error("⚠️ Ingrese la 'Orden / OP' y seleccione la 'Máquina' para guardar.")
    else:
        archivo_excel = "Registro_Produccion.xlsx"
        
        # Mapeo de columnas estandarizadas
        nuevo_registro = {
            "Orden": str(orden),
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Turno": str(turno),
            "Máquina": str(maquina),
            "Proyecto": str(nombre_general),
            "Detalle Pieza": str(detalle_pieza),
            "Material": str(material),
            "Calibre": str(calibre),
            "Cantidad Lote": int(cant_general),
            "Piezas OK": int(cant_piezas_ok),
            "Setup (min)": float(t_setup),
            "Tiempo Estándar (min)": float(tiempo_estandar),
            "Ciclo Real (min)": float(t_ciclo),
            "Espera Operario (min)": float(t_espera),
            "Paro Máquina (min)": float(t_paros),
            "Descargue (min)": float(t_descargue),
            "Motivo Paro": str(motivo_paro)
        }
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        
        if os.path.exists(archivo_excel):
            try:
                df_ex = pd.read_excel(archivo_excel)
                df_final = pd.concat([df_ex, df_nuevo], ignore_index=True)
            except:
                df_final = df_nuevo
        else:
            df_final = df_nuevo
            
        # Depurar filas completamente vacías
        df_final = df_final.dropna(subset=["Orden"])
        df_final.to_excel(archivo_excel, index=False)
        
        st.success(f"✅ ¡Registro de la Orden {orden} guardado y matriz depurada correctamente!")

        # --- ANÁLISIS DE EFICIENCIA EN VIVO DE ESTE REGISTRO ---
        tiempo_total = float(t_setup) + float(t_ciclo) + float(t_descargue) + float(t_espera) + float(t_paros)
        tiempo_productivo = float(t_ciclo)
        tiempo_improductivo = float(t_espera) + float(t_paros)

        if tiempo_total > 0:
            eficiencia = (tiempo_productivo / tiempo_total) * 100
            desperdicio = (tiempo_improductivo / tiempo_total) * 100
            
            st.markdown('<div class="section-header">📈 ANÁLISIS DE EFICIENCIA DEL REGISTRO CAPTURADO</div>', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tiempo Total Operativo", f"{tiempo_total:.1f} min")
            m2.metric("Tiempo Productivo", f"{tiempo_productivo:.1f} min")
            m3.metric("Eficiencia (Valor Agregado)", f"{eficiencia:.1f}%")
            m4.metric("Desperdicio (Paros/Espera)", f"{desperdicio:.1f}%")
            
            if eficiencia >= 75:
                st.info("🟢 **Excelente desempeño:** Operación con alta productividad.")
            elif 50 <= eficiencia < 75:
                st.warning("🟠 **Desempeño medio:** Revisar tiempos de alistamiento (setup) y esperas.")
            else:
                st.error("🔴 **Alerta de eficiencia:** Alto porcentaje de tiempo improductivo detectado.")

        resetear_cronometros()

# MOSTRAR MATRIZ Y FILTRAR FILAS VACÍAS
st.markdown('<div class="section-header">📊 HISTORIAL Y MATRIZ DE TIEMPOS DE PLANTA</div>', unsafe_allow_html=True)
archivo_excel = "Registro_Produccion.xlsx"

if os.path.exists(archivo_excel):
    df_ver = pd.read_excel(archivo_excel)
    
    # Limpieza visual en pantalla
    df_ver_limpio = df_ver.dropna(subset=["Orden"]).reset_index(drop=True)
    st.dataframe(df_ver_limpio, use_container_width=True)
    
    # MÓDULO DE DESCARGA PROTEGIDO CON CONTRASEÑA
    st.markdown("---")
    st.markdown("🔒 **Exportación Protegida de Datos (Ingeniería de Costos)**")
    
    col_pass, col_btn = st.columns([1, 2])
    
    with col_pass:
        clave_ingresada = st.text_input("Ingresa la clave para autorizar la descarga:", type="password", placeholder="Escribe el PIN aquí...")
    
    with col_btn:
        st.write("") # Espaciador visual para alinear con el input
        st.write("")
        if clave_ingresada.strip().upper() == "TATIANA":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_ver_limpio.to_excel(writer, index=False, sheet_name='Tiempos')
            buffer.seek(0)
            
            st.download_button(
                label="📥 DESCARGAR MATRIZ COMPLETA EN EXCEL (.XLSX)",
                data=buffer,
                file_name="Registro_Produccion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        elif clave_ingresada != "":
            st.error("❌ Clave incorrecta. Acceso denegado a la descarga de la matriz.")
        else:
            st.warning("🔑 Ingresa la contraseña autorizada para habilitar el botón de descarga.")

else:
    st.info("Aún no hay registros consolidados.")

# Pie de página
st.markdown("""
    <div class="footer-credits">
        Desarrollado por <span>Tatiana Almario • Asistente de Costos y Métodos</span>
    </div>
""", unsafe_allow_html=True)
