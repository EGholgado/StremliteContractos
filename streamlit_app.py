import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Análisis de Contratos por RUC")

@st.cache_data
def cargar_datos():
    df = pd.read_parquet("Consolidado.parquet")
    df['RUC'] = df['RUC'].astype(str).str.strip()
    df['Razón Social'] = df['Razón Social'].astype(str).str.strip()

    df_mensual = pd.read_parquet("DataMensualContrato.parquet")
    df_mensual['RUC'] = df_mensual['RUC'].astype(str).str.strip()
    df_mensual['Razón Social'] = df_mensual['Razón Social'].astype(str).str.strip()

    return df, df_mensual

df, df_mensual = cargar_datos()

st.title("Análisis de Contratos OSCE")

rucs = sorted(df['RUC'].dropna().unique())
razones = sorted(df['Razón Social'].dropna().unique())

ruc_sel = st.sidebar.selectbox("Seleccionar RUC", options=["Todos"] + rucs)
razon_sel = st.sidebar.selectbox("Seleccionar Razón Social", options=["Todos"] + razones)

df_mensual['Año'] = df_mensual['Fecha Periodo'].dt.year
años_disponibles = sorted(df_mensual['Año'].unique())

años_seleccionados = st.sidebar.multiselect(
    "Seleccionar Año(s)",
    options=años_disponibles,
    default=años_disponibles,
)

df_filtrado = df.copy()

if ruc_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['RUC'] == ruc_sel]
if razon_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Razón Social'] == razon_sel]

if años_seleccionados:
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha de Firma de Contrato'].dt.year <= max(años_seleccionados)) &
        (df_filtrado['Fecha Prevista de FIn de Contrato'].dt.year >= min(años_seleccionados))
    ]

st.header("📋 Tabla de Datos")
st.dataframe(df_filtrado.style.format({
    'Fecha de Firma de Contrato': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '',
    'Fecha Prevista de FIn de Contrato': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '',
    '% Participación RUC': lambda x: f"{x:,.2f} %" if pd.notnull(x) else '',
    'Monto del Contrato Original': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
    'Valor Proporcional GE': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
    'Plazo en Meses': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
}), use_container_width=True)


st.header("📈 Evolución Mensual de Contratos")

df_grafico = df_mensual.copy()
if ruc_sel != "Todos":
    df_grafico = df_grafico[df_grafico['RUC'] == ruc_sel]
if razon_sel != "Todos":
    df_grafico = df_grafico[df_grafico['Razón Social'] == razon_sel]
if años_seleccionados:
    df_grafico = df_grafico[df_grafico['Fecha Periodo'].dt.year.isin(años_seleccionados)]


df_resumen = df_grafico.groupby(["Periodo", "Fecha Periodo", "RUC"], as_index=False)["Valor Mensual proporcional"].sum()
df_resumen = df_resumen.sort_values("Fecha Periodo")


fig = px.bar(
    df_resumen,
    x="Periodo",
    y="Valor Mensual proporcional",
    color="RUC",
    hover_data={"Valor Mensual proporcional": ":,.2f", "RUC": True},
    labels={"Valor Mensual proporcional": "Valor (S/.)"},
    title="Evolución Mensual de Contratos",
)

fig.update_layout(
    xaxis_title="Periodo",
    yaxis_title="Valor Mensual proporcional (S/.)",
    legend_title="RUC",
    xaxis_tickangle=-45,
    hovermode="x unified",
    bargap=0.2,
    height=500,
)

st.plotly_chart(fig, use_container_width=True)
