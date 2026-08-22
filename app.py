import streamlit as st
import pandas as pd
import datetime
import time
import os

st.set_page_config(
    page_title="Control de Producción y Métodos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado para estilo limpio
st.markdown("""
    <style>
    .main-header {
        color: #0f172a;
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 2px;
    }
    .sub-header {
        color: #475569;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .section-title {
        color: #1e293b;
        font-size: 16px;
        font-weight: 700;
        padding-bottom: 4px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 14px;
    }
    .timer-card-prod {
        background-color: #ffffff;
        border-left: 5px solid #2563eb;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .timer-card-stop {
        background-color: #ffffff;
        border-left: 5px solid #dc2626;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
        height: 38px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">CONTROL DE PRODUCCIÓN Y TOMA DE TIEMPOS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Acceso Centralizado Nube • Multi-Sede & Multi-Dispositivo</div>', unsafe_allow_html=True)

# Cronómetros en Session State
cronometros = ["Setup", "Ciclo Real", "Descargue", "Paros", "Espera Operario"]
for c in cronometros:
    if f"tiempo_{c}" not in st.session_state:
        st.session_state[f"tiempo_{c}"] = 0.0
    if f"corriendo_{c}" not in st.session_state:
        st.session_state[f"corriendo_{c}"] = False
    if f"inicio_{c}" not in st.session_state:
        st.session_state[f"inicio_{c}"] = None

# Variables de Formulario
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

# ESTACIÓN 1: PARAMETRIZACIÓN
with st.expander("ESTACIÓN 1: Parametrización de la Orden y Material", expanded=True):
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

# ESTACIÓN 2: CRONÓMETROS
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
                <span style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Tiempo {nombre}</span>
                <div style="font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 2px;">{minutos:02d}:{segundos:02d} <span style="font-size: 12px; font-weight: 500;">min</span></div>
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
        motivo_paro = st.text_input("Motivo Principal de Paro", placeholder="Ej: Ajuste de herramental", key="motivo_paro_input")

# Refresco dinámico
alguno_activo = any(st.session_state[f"corriendo_{c}"] for c in cronometros)
if alguno_activo:
    time.sleep(1)
    st.rerun()

st.markdown("---")

# RESUMEN METRICO
st.markdown('<div class="section-title">Consolidado Métrico del Lote</div>', unsafe_allow_html=True)
k1, k2, k3 = st.columns(3)

tiempo_total = round(t_setup + t_ciclo + t_descargue + t_paros + t_espera, 2)
tiempo_productivo = round(t_setup + t_ciclo + t_descargue, 2)
eficiencia = round((tiempo_productivo / tiempo_total * 100), 1) if tiempo_total > 0 else 100.0

k1.metric("Tiempo Total (min)", f"{tiempo_total}")
k2.metric("Tiempo Neto Productivo (min)", f"{tiempo_productivo}")
k3.metric("Eficiencia (OEE)", f"{eficiencia}%")

st.markdown("<br>", unsafe_allow_html=True)

# GUARDADO DE DATOS
if st.button("GUARDAR REGISTRO COMPLETO", use_container_width=True, type="primary"):
    if not orden or not maquina:
        st.error("Error: Los campos 'Orden' y 'Máquina' son obligatorios.")
    else:
        archivo_excel = "Registro_Produccion.xlsx"
        material_completo = f"{material} - {calibre}"
        proyecto_modalidad = f"{proyecto} ({tipo_trabajo} - {cant_laminas} láminas)"
        
        nuevo_registro = {
            "Orden": str(orden),
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Turno": str(turno),
            "Máquina": str(maquina),
            "Proyecto": str(proyecto_modalidad),
            "Material": str(material_completo),
            "Setup (min)": float(t_setup),
            "Ciclo Real (min)": float(t_ciclo),
            "Descargue (min)": float(t_descargue),
            "Paros (min)": float(t_paros),
            "Espera Operario (min)": float(t_espera),
            "Motivo Paro": str(motivo_paro)
        }
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        if os.path.exists(archivo_excel):
            df_ex = pd.read_excel(archivo_excel)
            df_final = pd.concat([df_ex, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final.to_excel(archivo_excel, index=False)
        st.success(f"Confirmación: Registro para la Orden {orden} almacenado correctamente.")
        limpiar_formulario()
        time.sleep(1)
        st.rerun()

# MOSTRAR REGISTROS
st.markdown("---")
st.markdown('<div class="section-title">Registros Guardados</div>', unsafe_allow_html=True)
archivo_excel = "Registro_Produccion.xlsx"
if os.path.exists(archivo_excel):
    df_ver = pd.read_excel(archivo_excel)
    st.dataframe(df_ver, use_container_width=True)
else:
    st.info("Aún no hay registros almacenados.")
