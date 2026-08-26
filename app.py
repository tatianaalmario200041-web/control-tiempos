import streamlit as st
import pandas as pd
import datetime
import pytz
from io import BytesIO

# Configuración de la zona horaria de Colombia
TZ_BOGOTA = pytz.timezone('America/Bogota')

st.set_page_config(page_title="Control de Tiempos de Planta", layout="wide")
st.title("⏱️ Sistema de Control de Tiempos y Eficiencia")

# Inicialización del estado global de la sesión
if 'registros' not in st.session_state:
    st.session_state.registros = []

# --- SECCIÓN: Registro de Tiempos ---
st.sidebar.header("Datos de la Operación")
operario = st.sidebar.selectbox("Seleccione Operario:", ["Operario 1", "Operario 2", "Operario 3"])
proceso = st.sidebar.text_input("Proceso / Orden de Trabajo:", "Corte / Ensamble")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Registrar Evento")
    tipo_evento = st.selectbox("Tipo de Tiempo:", ["Setup", "Ciclo Real", "Descargue", "Paro / Tiempo Muerto"])
    duracion_min = st.number_input("Duración (minutos):", min_value=0.1, step=0.5, value=1.0)
    
    if st.button("💾 Guardar Registro"):
        hora_actual = datetime.datetime.now(TZ_BOGOTA).strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.registros.append({
            "Fecha/Hora": hora_actual,
            "Operario": operario,
            "Proceso": proceso,
            "Tipo de Tiempo": tipo_evento,
            "Duración (min)": duracion_min
        })
        st.success(f"Registro guardado a las {hora_actual}")

with col2:
    st.subheader("Historial Actual")
    if st.session_state.registros:
        df = pd.DataFrame(st.session_state.registros)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay registros capturados en la sesión actual.")

# --- SECCIÓN: Descarga de Matriz de Datos ---
st.markdown("---")
st.subheader("🔒 Descarga del Reporte de Producción (Protegido)")

pin_ingresado = st.text_input("Ingrese PIN de Administrador:", type="password")
PIN_CORRECTO = "1234"  # Cambia este PIN por tu clave deseada

if st.button("Descargar Excel y Limpiar Historial"):
    if pin_ingresado == PIN_CORRECTO:
        if len(st.session_state.registros) > 0:
            df_export = pd.DataFrame(st.session_state.registros)
            
            # Generación del archivo Excel en memoria
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Tiempos_Produccion')
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Confirmar y Descargar Archivo Excel",
                data=excel_data,
                file_name=f"Reporte_Tiempos_{datetime.datetime.now(TZ_BOGOTA).strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            # Limpieza automática tras la descarga
            st.session_state.registros = []
            st.warning("El historial de la sesión ha sido limpiado tras preparar el archivo.")
        else:
            st.error("No hay registros acumulados para descargar.")
    else:
        st.error("PIN incorrecto. Acceso denegado para exportación de matriz.")
