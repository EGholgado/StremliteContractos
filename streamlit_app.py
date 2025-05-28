import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Análisis de Contratos por RUC")

@st.cache_data
def cargar_datos():
    df = pd.read_parquet("Consolidado.parquet")
    df['RUC Origen'] = df['RUC Origen'].astype(str).str.strip()
    df['Valor Proporcional GE'] = pd.to_numeric(df['Valor Proporcional GE'].str.replace(',', ''), errors='coerce')
    df['fecha_de_firma_de_contrato'] = pd.to_datetime(df['fecha_de_firma_de_contrato'], errors='coerce')
    return df

df = cargar_datos()

st.title("📊 Análisis de Contratos por RUC")

# Layout con columnas
col1, col2 = st.columns([1, 3])

with col1:
    st.header("Filtros")

    rucs_disponibles = df['RUC Origen'].dropna().unique().tolist()
    rucs_disponibles.sort()

    ruc_seleccionado = st.selectbox("Selecciona RUC Origen", options=["Todos"] + rucs_disponibles)

    # Filtrar según selección
    if ruc_seleccionado != "Todos":
        df_filtrado = df[df['RUC Origen'] == ruc_seleccionado]
    else:
        df_filtrado = df.copy()

with col2:
    st.header("Datos")

    st.dataframe(df_filtrado, use_container_width=True)

    # Agrupar por año-mes y sumar valor proporcional
    df_filtrado['Año-Mes'] = df_filtrado['fecha_de_firma_de_contrato'].dt.to_period('M').astype(str)
    resumen_mes = df_filtrado.groupby('Año-Mes')['Valor Proporcional GE'].sum().reset_index()

    # Graficar barras
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(resumen_mes['Año-Mes'], resumen_mes['Valor Proporcional GE'], color='skyblue')
    ax.set_xticklabels(resumen_mes['Año-Mes'], rotation=45, ha='right')
    ax.set_xlabel("Año-Mes")
    ax.set_ylabel("Valor Proporcional GE")
    ax.set_title("Valor Proporcional GE por Mes y Año")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)
