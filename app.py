import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os

st.set_page_config(page_title="Control Operativo de Proceso", layout="wide")

# Inicialización de estados de los cronómetros
if "t_setup_start" not in st.session_state:
    st.session_state.t_setup_start = None
if "t_setup_elapsed" not in st.session_state:
    st.session_state.t_setup_elapsed = 0
if "t_setup_running" not in st.session_state:
    st.session_state.t_setup_running = False

if "t_prod_start" not in st.session_state:
    st.session_state.t_prod_start = None
if "t_prod_elapsed" not in st.session_state:
    st.session_state.t_prod_elapsed = 0
if "t_prod_running" not in st.session_state:
    st.session_state.t_prod_running = False

if "t_paro_start" not in st.session_state:
    st.session_state.t_paro_start = None
if "t_paro_elapsed" not in st.session_state:
    st.session_state.t_paro_elapsed = 0
if "t_paro_running" not in st.session_state:
    st.session_state.t_paro_running = False

# Funciones de control de tiempo
def get_time_str(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def update_times():
    now = time.time()
    if st.session_state.t_setup_running:
        st.session_state.t_setup_elapsed += now - st.session_state.t_setup_start
        st.session_state.t_setup_start = now
    if st.session_state.t_prod_running:
        st.session_state.t_prod_elapsed += now - st.session_state.t_prod_start
        st.session_state.t_prod_start = now
    if st.session_state.t_paro_running:
        st.session_state.t_paro_elapsed += now - st.session_state.t_paro_start
        st.session_state.t_paro_start = now

update_times()

st.title("ESTACIÓN 2: Cronometraje Operativo de Proceso y Tiempos Muertos")

# Formulario de parámetros
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        orden = st.text_input("Orden de Producción", key="orden_input")
        turno = st.selectbox("Turno", ["Día", "Noche", "Mixto"])
    with col2:
        maquina = st.selectbox("Máquina", ["Punzonadora", "Cizalla", "Dobladora", "Láser", "Prensa"])
        proyecto = st.text_input("Proyecto / Nombre de Pieza")
    with col3:
        material = st.selectbox("Material", ["Lámina CR", "Lámina HR", "Acero Inoxidable", "Aluminio", "Galvanizado"])
        calibre = st.selectbox("Calibre / Espesor", ["Calibre 18", "Calibre 16", "Calibre 14", "Calibre 12", "1/8 inch", "1/4 inch"])

st.markdown("---")
st.subheader("Tiempos Productivos / Operativos")

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("#### TIEMPO SETUP / PREPARACIÓN")
    st.markdown(f"### `{get_time_str(st.session_state.t_setup_elapsed)}`")
    c1, c2, c3 = st.columns(3)
    if c1.button("Iniciar Setup"):
        st.session_state.t_setup_start = time.time()
        st.session_state.t_setup_running = True
        st.rerun()
    if c2.button("Pausar Setup"):
        st.session_state.t_setup_running = False
        st.rerun()
    if c3.button("Reset Setup"):
        st.session_state.t_setup_running = False
        st.session_state.t_setup_elapsed = 0
        st.rerun()

with col_c2:
    st.markdown("#### TIEMPO PRODUCTIVO / OPERACIÓN")
    st.markdown(f"### `{get_time_str(st.session_state.t_prod_elapsed)}`")
    p1, p2, p3 = st.columns(3)
    if p1.button("Iniciar Producción"):
        st.session_state.t_prod_start = time.time()
        st.session_state.t_prod_running = True
        st.rerun()
    if p2.button("Pausar Producción"):
        st.session_state.t_prod_running = False
        st.rerun()
    if p3.button("Reset Producción"):
        st.session_state.t_prod_running = False
        st.session_state.t_prod_elapsed = 0
        st.rerun()

st.markdown("---")
st.subheader("Improductivos / Paros de Máquina")

col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown("#### TIEMPO PARO DE MÁQUINA")
    st.markdown(f"### `{get_time_str(st.session_state.t_paro_elapsed)}`")
    m1, m2, m3 = st.columns(3)
    if m1.button("Iniciar Paro"):
        st.session_state.t_paro_start = time.time()
        st.session_state.t_paro_running = True
        st.rerun()
    if m2.button("Pausar Paro"):
        st.session_state.t_paro_running = False
        st.rerun()
    if m3.button("Reset Paro"):
        st.session_state.t_paro_running = False
        st.session_state.t_paro_elapsed = 0
        st.rerun()

with col_p2:
    causa_paro = st.selectbox("Causa del Paro / Novedad", ["Ninguno", "Mantenimiento / Falla Mecánica", "Falta de Material", "Pausa Pausas Activas / Almuerzo", "Ajuste de Plano / Ingeniería", "Espera de Inspección Calidad"])
    observaciones = st.text_area("Observaciones Adicionales")

st.markdown("---")

if st.button("Guardar Registro Completo", type="primary"):
    if not orden:
        st.error("Por favor ingrese el número de Orden de Producción.")
    else:
        archivo = "Registro_Produccion.xlsx"
        nuevo_dato = {
            "Fecha": datetime.now().strftime("%Y-%m-%d"),
            "Orden": orden,
            "Turno": turno,
            "Máquina": maquina,
            "Proyecto": proyecto,
            "Material": material,
            "Calibre": calibre,
            "Tiempo_Setup": get_time_str(st.session_state.t_setup_elapsed),
            "Tiempo_Productivo": get_time_str(st.session_state.t_prod_elapsed),
            "Tiempo_Paro": get_time_str(st.session_state.t_paro_elapsed),
            "Causa_Paro": causa_paro,
            "Observaciones": observaciones,
            "Hora": datetime.now().strftime("%H:%M:%S")
        }
        
        df_nuevo = pd.DataFrame([nuevo_dato])
        if os.path.exists(archivo):
            df_existente = pd.read_excel(archivo)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final.to_excel(archivo, index=False)
        st.success(f"Confirmación: Registro para la Orden {orden} almacenado correctamente en {archivo}.")

# Tabla de historial
st.markdown("---")
st.subheader("Registros Guardados")
archivo = "Registro_Produccion.xlsx"
if os.path.exists(archivo):
    df_ver = pd.read_excel(archivo)
    st.dataframe(df_ver, use_container_width=True)
