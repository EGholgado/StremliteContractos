import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

st.set_page_config(layout="wide", page_title="Análisis de Contratos por RUC")

@st.cache_data
def cargar_datos(nombre):
    df = pd.read_parquet(nombre)
    df['RUC'] = df['RUC'].astype(str).str.strip()
    df['Razón Social'] = df['Razón Social'].astype(str).str.strip()
    return df

# Cargar datos
df = cargar_datos("Consolidado.parquet")
df_mensual = cargar_datos("DataMensualContrato.parquet")

st.title("📊 Análisis de Contratos Oesce")

# Sidebar Filtros
rucs = sorted(df['RUC'].dropna().unique())
razones = sorted(df['Razón Social'].dropna().unique())

ruc_sel = st.sidebar.selectbox("Seleccionar RUC", options=["Todos"] + rucs)
razon_sel = st.sidebar.selectbox("Seleccionar Razón Social", options=["Todos"] + razones)

# Años disponibles (basado en df_mensual)
df_mensual['Año'] = df_mensual['Fecha Periodo'].dt.year
años_disponibles = sorted(df_mensual['Año'].unique())

años_seleccionados = st.sidebar.multiselect(
    "Seleccionar Año(s)",
    options=años_disponibles,
    default=años_disponibles,
)

# Aplicar filtros a Consolidado
df_filtrado = df.copy()
if ruc_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['RUC'] == ruc_sel]
if razon_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Razón Social'] == razon_sel]

# Mostrar tabla
st.header("📋 Tabla de Datos")
st.dataframe(df_filtrado.style.format({
    'Fecha de Firma de Contrato': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '',
    'Fecha Prevista de FIn de Contrato': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '',
    '% Participación RUC': lambda x: f"{x:,.2f} %" if pd.notnull(x) else '',
    'Monto del Contrato Original': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
    'Valor Proporcional GE': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
    'Plazo en Meses': lambda x: f"{x:,.2f}" if pd.notnull(x) else '',
}), use_container_width=True)

# ---------------------- GRÁFICO ----------------------
st.header("📈 Evolución Mensual de Contratos")

df_grafico = df_mensual.copy()

# Filtros de gráfico
if ruc_sel != "Todos":
    df_grafico = df_grafico[df_grafico['RUC'] == ruc_sel]
if razon_sel != "Todos":
    df_grafico = df_grafico[df_grafico['Razón Social'] == razon_sel]
if años_seleccionados:
    df_grafico = df_grafico[df_grafico['Fecha Periodo'].dt.year.isin(años_seleccionados)]

# Agrupar por mes y sumar
df_grafico = df_grafico.groupby(["Periodo", "Fecha Periodo"], as_index=False)["Valor Mensual proporcional"].sum()
df_grafico = df_grafico.sort_values("Fecha Periodo")

# Formatear eje Y en miles o millones
def formato_miles_millones(x, pos):
    if x >= 1e6:
        return f'{x * 1e-6:.1f} M'
    elif x >= 1e3:
        return f'{x * 1e-3:.0f} K'
    else:
        return f'{x:.0f}'

# Gráfico
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(df_grafico["Periodo"], df_grafico["Valor Mensual proporcional"], color="#3E8ED0")
ax.set(xlabel="Periodo", ylabel="Valor Mensual proporcional (S/.)", title="Evolución Mensual de Contratos")
ax.yaxis.set_major_formatter(ticker.FuncFormatter(formato_miles_millones))
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', linestyle='--', alpha=0.5)

max_val = df_grafico["Valor Mensual proporcional"].max()
if max_val == 0 or pd.isna(max_val):
    max_val = 1
ax.set_ylim(0, max_val * 1.1)

fig.tight_layout()
st.pyplot(fig)
