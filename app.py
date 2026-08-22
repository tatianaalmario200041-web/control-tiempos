import streamlit as st
import pandas as pd
import datetime
import time
import os

# Configuración de página amplia e interfaz corporativa
st.set_page_config(
    page_title="Sistema de Control de Producción y Métodos",
    layout="wide"
)

# CSS Personalizado: Títulos grandes, bordes estilizados, tarjetas e indicadores de color
st.markdown("""
    <style>
    /* Estilo General */
    .main { background-color: #f4f6f9; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }
    
    /* Encabezados Principales Grandes */
    .main-header {
        color: #0f172a;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    .sub-header {
        color: #475569;
        font-size: 15px;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .section-title {
        color: #1e293b;
        font-size: 22px;
        font-weight: 700;
        padding-bottom: 6px;
        border-bottom: 2px solid #cbd5e1;
        margin-bottom: 16px;
    }
    
    /* Tarjetas de Estaciones y Bordes */
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
    }
    
    /* Tarjetas de Cronómetros */
    .timer-card-prod {
        background-color: #ffffff;
        border-left: 5px solid #2563eb;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .timer-card-stop {
        background-color: #ffffff;
        border-left: 5px solid #dc2626;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 12px;
    }
    
    /* Botones de Control */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
        height: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado Principal del Sistema
st.markdown('<div class="main-header">CONTROL DE PRODUCCIÓN Y TOMA DE TIEMPOS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Módulo Industrial de Monitoreo de Procesos, Tiempos Muertos y Materiales</div>', unsafe_allow_html=True)

# Inicialización de cronómetros
cronometros = ["Setup", "Ciclo Real", "Descargue", "Paros", "Espera Operario"]
for c in cronometros:
    if f"tiempo_{c}" not in st.session_state:
        st.session_state[f"tiempo_{c}"] = 0.0
    if f"corriendo_{c}" not in st.session_state:
        st.session_state[f"corriendo_{c}"] = False
    if f"inicio_{c}" not in st.session_state:
        st.session_state[f"inicio_{c}"] = None

# Variables para reseteo automático del formulario
if "orden_input" not in st.session_state:
    st.session_state["orden_input"] = ""
if "motivo_paro_input" not in st.session_state:
    st.session_state["motivo_paro_input"] = ""

def limpiar_formulario():
    st.session_state["orden_input"] = ""
    st.session_state["motivo_paro_input"] = ""
    for c in cronometros:
        st.session_state[f"tiempo_{c}"] = 0.0
        st.session_state[f"corriendo_{c}"] = False
        st.session_state[f"inicio_{c}"] = None

# ESTACIÓN 1: PARAMETRIZACIÓN DE LA ORDEN Y MATERIALES
with st.expander("ESTACIÓN 1: Parametrización de la Orden y Especificación de Material", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        orden = st.text_input("Orden / Pedido", key="orden_input")
        turno = st.selectbox("Turno Operativo", ["Día", "Tarde", "Noche"], key="turno_select")
        maquina = st.selectbox("Máquina / Centro de Costo", ["Punzonadora", "Dobladora", "Cizalla", "Corte Láser", "Ensamble", "Pintura"], key="maquina_select")
    
    with col2:
        fecha = st.date_input("Fecha", datetime.date.today(), key="fecha_input")
        proyecto = st.selectbox("Proyecto / Nombre General", ["Mesa de Juntas", "Gabinete Industrial", "Estructura Modular", "Panel Perforado", "Mueble Metálico", "Otro / Específico"], key="proyecto_select")
        tipo_trabajo = st.selectbox("Modalidad de Trabajo", ["Nesting Completo", "Despiece Individual", "Lote Muestra", "Reproceso"], key="tipo_trabajo_select")

    with col3:
        material = st.selectbox("Material Base", ["Lámina CR (Cold Rolled)", "Lámina HR (Hot Rolled)", "Acero Inoxidable", "Aluminio", "Galvanizado"], key="material_select")
        calibre = st.selectbox("Calibre / Espesor", ["Calibre 18", "Calibre 20", "Calibre 22", "Calibre 1/8\"", "Calibre 3/16\"", "Calibre 1/4\""], key="calibre_select")
        cant_laminas = st.number_input("Cantidad de Láminas", min_value=1, step=1, value=1, key="cant_laminas_input")

# ESTACIÓN 2: MEDIPROCESO DE TIEMPOS MEDIANTE CRONÓMETROS
with st.expander("ESTACIÓN 2: Cronometraje Operativo de Proceso y Tiempos Muertos", expanded=True):
    
    def render_cronometro(nombre, clave, es_paros=False):
        tiempo_actual = st.session_state[f"tiempo_{clave}"]
        if st.session_state[f"corriendo_{clave}"]:
            tiempo_actual += time.time() - st.session_state[f"inicio_{clave}"]
        
        minutos = int(tiempo_actual // 60)
        segundos = int(tiempo_actual % 60)
        
        card_class = "timer-card-stop" if es_paros else "timer-card-prod"
        
        st.markdown(f'''
            <div class="{card_class}">
                <span style="font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase;">Tiempo {nombre}</span>
                <div style="font-size: 26px; font-weight: 800; color: #0f172a; margin-top: 2px;">{minutos:02d}:{segundos:02d} <span style="font-size: 14px; font-weight: 500;">min</span></div>
            </div>
        ''', unsafe_allow_html=True)
        
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Iniciar", key=f"start_{clave}"):
                if not st.session_state[f"corriendo_{clave}"]:
                    st.session_state[f"inicio_{clave}"] = time.time()
                    st.session_state[f"corriendo_{clave}"] = True
                    st.rerun()
        with b2:
            if st.button("Pausar", key=f"pause_{clave}"):
                if st.session_state[f"corriendo_{clave}"]:
                    st.session_state[f"tiempo_{clave}"] += time.time() - st.session_state[f"inicio_{clave}"]
                    st.session_state[f"corriendo_{clave}"] = False
                    st.rerun()
        with b3:
            if st.button("Reiniciar", key=f"reset_{clave}"):
                st.session_state[f"tiempo_{clave}"] = 0.0
                st.session_state[f"corriendo_{clave}"] = False
                st.rerun()
                
        return round(tiempo_actual / 60.0, 2)

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="section-title">Tiempos Productivos Operativos</div>', unsafe_allow_html=True)
        t_setup = render_cronometro("Setup / Separación", "Setup", es_paros=False)
        t_ciclo = render_cronometro("Ciclo Real Machining", "Ciclo Real", es_paros=False)
        t_descargue = render_cronometro("Descargue y Verificación", "Descargue", es_paros=False)

    with col_b:
        st.markdown('<div class="section-title">Improductivos / Paros de Máquina</div>', unsafe_allow_html=True)
        t_paros = render_cronometro("Paros de Máquina", "Paros", es_paros=True)
        t_espera = render_cronometro("Tiempo Muerto / Espera Operario", "Espera Operario", es_paros=True)
        motivo_paro = st.text_input("Motivo Principal de Paro", placeholder="Ej: Ajuste de herramental / Cambio de matriz", key="motivo_paro_input")

# Refresco activo del segundero
alguno_activo = any(st.session_state[f"corriendo_{c}"] for c in cronometros)
if alguno_activo:
    time.sleep(1)
    st.rerun()

st.markdown("---")

# RESUMEN TÉCNICO DE INGENIERÍA
st.markdown('<div class="section-title">Consolidado Métrico del Lote</div>', unsafe_allow_html=True)
k1, k2, k3 = st.columns(3)

tiempo_total = round(t_setup + t_ciclo + t_descargue + t_paros + t_espera, 2)
tiempo_productivo = round(t_setup + t_ciclo + t_descargue, 2)
eficiencia = round((tiempo_productivo / tiempo_total * 100), 1) if tiempo_total > 0 else 100.0

k1.metric("Tiempo Total Lote (min)", f"{tiempo_total}")
k2.metric("Tiempo Neto Productivo (min)", f"{tiempo_productivo}")
k3.metric("Eficiencia Proceso (OEE)", f"{eficiencia}%")

st.markdown("<br>", unsafe_allow_html=True)

# ACCIÓN DE REGISTRO A BASE DE DATOS
if st.button("GUARDAR REGISTRO EN BASE DE DATOS EXCEL", use_container_width=True, type="primary"):
    if not orden or not maquina:
        st.error("Error de Validación: Los campos 'Orden' y 'Máquina' son obligatorios.")
    else:
        archivo_excel = "Registro_Produccion.xlsx"
        
        material_completo = f"{material} - {calibre}"
        proyecto_modalidad = f"{proyecto} ({tipo_trabajo} - {cant_laminas} láminas)"
        
        nuevo_registro = {
            "Orden": orden,
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Turno": turno,
            "Máquina": maquina,
            "Proyecto": proyecto_modalidad,
            "Material": material_completo,
            "Setup (min)": t_setup,
            "Ciclo Real (min)": t_ciclo,
            "Descargue (min)": t_descargue,
            "Paros (min)": t_paros,
            "Espera Operario (min)": t_espera,
            "Motivo Paro": motivo_paro
        }
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        
        if os.path.exists(archivo_excel):
            df_existente = pd.read_excel(archivo_excel)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final.to_excel(archivo_excel, index=False)
        st.success(f"Confirmación: Registro para la Orden {orden} almacenado correctamente en {archivo_excel}.")
        
        # Limpieza de campos y recarga
        limpiar_formulario()
        time.sleep(1)
        st.rerun()
