import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Análisis de Contratos", layout="wide")
st.title("📊 Análisis de Contratos por RUC")

@st.cache_data
def cargar_datos():
    df = pd.read_parquet("Consolidado.parquet")
    df['RUC Origen'] = df['RUC Origen'].astype(str).str.strip()
    # Convertir "Valor Proporcional GE" de string con comas a float
    df['Valor Proporcional GE'] = df['Valor Proporcional GE'].str.replace(',', '').astype(float)
    # Asegurar que fecha sea datetime
    df['fecha_de_firma_de_contrato'] = pd.to_datetime(df['fecha_de_firma_de_contrato'], errors='coerce')
    return df

df = cargar_datos()

# Sidebar - filtro de RUC
st.sidebar.header("Filtros")
rucs_unicos = sorted(df['RUC Origen'].dropna().unique())
ruc_seleccionado = st.sidebar.selectbox("Selecciona un RUC", rucs_unicos)

# Filtrar datos
df_filtrado = df[df['RUC Origen'] == ruc_seleccionado]

# Mostrar tabla a la derecha en layout ancho
st.subheader(f"Contratos para RUC: {ruc_seleccionado}")

# Tabla
st.dataframe(df_filtrado, use_container_width=True)

# Preparar datos para gráfico
df_graf = df_filtrado.copy()
df_graf['AñoMes'] = df_graf['fecha_de_firma_de_contrato'].dt.to_period('M').astype(str)

# Agrupar y sumar "Valor Proporcional GE" por mes
df_graf_agrupado = df_graf.groupby('AñoMes')['Valor Proporcional GE'].sum().reset_index()

# Gráfico de barras con Altair
bar_chart = alt.Chart(df_graf_agrupado).mark_bar(color='#4a90e2').encode(
    x=alt.X('AñoMes', sort=None, title='Mes - Año'),
    y=alt.Y('Valor Proporcional GE', title='Suma Valor Proporcional GE'),
    tooltip=['AñoMes', 'Valor Proporcional GE']
).properties(
    width=700,
    height=400,
    title="Suma de Valor Proporcional GE por Mes y Año"
)

st.altair_chart(bar_chart, use_container_width=True)
