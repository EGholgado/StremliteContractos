import streamlit as st
import pandas as pd

# Título de la app
st.title("Análisis de Contratos por RUC")

# Cargar el archivo Parquet
@st.cache_data
def cargar_datos():
    return pd.read_parquet("Consolidado.parquet")

df = cargar_datos()

# Mostrar tabla original
st.subheader("Vista general del DataFrame")
st.dataframe(df, use_container_width=True)

# Filtro por RUC
rucs_unicos = df['RUC Origen'].dropna().unique()
ruc_seleccionado = st.selectbox("Selecciona un RUC para filtrar", sorted(rucs_unicos))

df_filtrado = df[df['RUC Origen'] == ruc_seleccionado]

# Mostrar resultados filtrados
st.subheader(f"Contratos para el RUC: {ruc_seleccionado}")
st.dataframe(df_filtrado, use_container_width=True)

# Mostrar métricas agregadas
st.subheader("Resumen")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Valor Proporcional GE", df_filtrado["Valor Proporcional GE"].replace({',': ''}, regex=True).astype(float).sum())

with col2:
    st.metric("Promedio mensual proporcional", df_filtrado["Valor Mensual proporcional"].replace({',': ''}, regex=True).astype(float).mean())

# Descargar el filtro como Excel
st.download_button(
    label="📥 Descargar datos filtrados",
    data=df_filtrado.to_excel(index=False, engine='openpyxl'),
    file_name=f'Contratos_{ruc_seleccionado}.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
