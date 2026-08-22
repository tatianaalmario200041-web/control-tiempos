import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración inicial de la página
st.set_page_config(
    page_title="Control de Tiempos",
    page_icon="⏱️",
    layout="wide"
)

# Nombre del archivo Excel local
ARCHIVO_EXCEL = "Registro_Produccion.xlsx"

# Inicializar sesión si no existen los datos
if "registros" not in st.session_state:
    st.session_state["registros"] = []

st.title("⏱️ Control de Tiempos de Producción")

# Formulario principal
with st.form(key="form_tiempos", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        orden = st.text_input("Número de Orden de Producción", key="orden_input")
        operario = st.text_input("Nombre del Operario", key="operario_input")
        proceso = st.selectbox("Proceso / Estación", ["Setup / Preparación", "Tiempo Productivo", "Paro / Improductivo"])
        
    with col2:
        unidades = st.number_input("Cantidad de Unidades Producción", min_value=0, step=1, key="unidades_input")
        fecha = st.date_input("Fecha", datetime.now())
        observaciones = st.text_area("Observaciones", key="obs_input")

    submit_button = st.form_submit_button(label="Guardar Registro")

if submit_button:
    if not orden or not operario:
        st.error("Por favor completa los campos obligatorios: Orden y Operario.")
    else:
        # Estructura del nuevo registro
        nuevo_registro = {
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Orden": orden,
            "Operario": operario,
            "Proceso": proceso,
            "Unidades": unidades,
            "Observaciones": observaciones,
            "Hora_Registro": datetime.now().strftime("%H:%M:%S")
        }

        # Guardar en dataframe y exportar a Excel
        df_nuevo = pd.DataFrame([nuevo_registro])

        if os.path.exists(ARCHIVO_EXCEL):
            df_existente = pd.read_excel(ARCHIVO_EXCEL)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo

        df_final.to_excel(ARCHIVO_EXCEL, index=False)

        st.success(f"Confirmación: Registro para la Orden {orden} almacenado correctamente en {ARCHIVO_EXCEL}.")
        st.rerun()

# Visualización de datos registrados
st.subheader("📋 Registros Guardados")
if os.path.exists(ARCHIVO_EXCEL):
    df_ver = pd.read_excel(ARCHIVO_EXCEL)
    st.dataframe(df_ver, use_container_width=True)
else:
    st.info("Aún no hay registros almacenados.")
