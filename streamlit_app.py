import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Análisis de Contratos por RUC")

@st.cache_data
def cargar_datos():
    df = pd.read_parquet("Consolidado.parquet")
    df['RUC'] = df['RUC'].astype(str).str.strip()
    df['Razón Social'] = df['Razón Social'].astype(str).str.strip()
    df['RUC - Razón Social'] = df['RUC'] + " - " + df['Razón Social']

    df_mensual = pd.read_parquet("DataMensualContrato.parquet")
    df_mensual['Año'] = df_mensual['Fecha Periodo'].dt.year
    df_mensual['RUC'] = df_mensual['RUC'].astype(str).str.strip()
    df_mensual['Razón Social'] = df_mensual['Razón Social'].astype(str).str.strip()
    df_mensual['RUC - Razón Social'] = df_mensual['RUC'] + " - " + df_mensual['Razón Social']
    return df, df_mensual

df, df_mensual = cargar_datos()

st.title("Análisis de Contratos OSCE")

# === Menús con opción "Todos" ===
ruc_opciones = ["Todos"] + sorted(df['RUC - Razón Social'].dropna().unique())
años_opciones = ["Todos"] + sorted(df_mensual['Año'].dropna().unique())

# Menú de RUCs
ruc_seleccionados = st.sidebar.multiselect(
    "Seleccionar RUC - Razón Social",
    options=ruc_opciones,
    default=["Todos"]
)

# Menú de Años
años_seleccionados = st.sidebar.multiselect(
    "Seleccionar Año(s)",
    options=años_opciones,
    default=["Todos"]
)

# Reemplazar "Todos" internamente
ruc_final = sorted(df['RUC - Razón Social'].dropna().unique()) if "Todos" in ruc_seleccionados else ruc_seleccionados
años_final = sorted(df_mensual['Año'].dropna().unique()) if "Todos" in años_seleccionados else años_seleccionados

# === Filtrado de datos ===
df_filtrado = df[df['RUC - Razón Social'].isin(ruc_final)]
df_filtrado = df_filtrado[
    (df_filtrado['Fecha de Firma de Contrato'].dt.year <= max(años_final)) &
    (df_filtrado['Fecha Prevista de FIn de Contrato'].dt.year >= min(años_final))
]

# === Mostrar tabla ===
df_mostrar = df_filtrado.drop(columns=["RUC - Razón Social"])
st.header("📋 Tabla de Datos")
st.dataframe(df_mostrar.style.format({
    'Fecha de Firma de Contrato': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '',
    'Fecha Prevista de FIn de Contrato': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '',
    '% Participación RUC': lambda x: f"{x:,.2f} %" if pd.notnull(x) else '',
    'Monto del Contrato Original': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
    'Valor Proporcional GE': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
    'Plazo en Meses': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
}), use_container_width=True)

# === Gráfico de evolución mensual ===
st.header("📈 Evolución Mensual de Contratos")

df_grafico = df_mensual[df_mensual['RUC - Razón Social'].isin(ruc_final)]
df_grafico = df_grafico[df_grafico['Fecha Periodo'].dt.year.isin(años_final)]

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



