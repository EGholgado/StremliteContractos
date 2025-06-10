import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Análisis de Contratos por RUC")

@st.cache_data
def cargar_datos():
    df = pd.read_parquet("Consolidado.parquet")
    df.reset_index(drop=True, inplace=True)
    df['RUC'] = df['RUC'].astype(str).str.strip()
    df['Razón Social'] = df['Razón Social'].astype(str).str.strip()
    df['RUC - Razón Social'] = df['RUC'] + " - " + df['Razón Social']

    df_mensual = pd.read_parquet("DataMensualContrato.parquet")
    df_mensual.reset_index(drop=True, inplace=True)
    df_mensual['Año'] = df_mensual['Fecha Periodo'].dt.year
    df_mensual['RUC'] = df_mensual['RUC'].astype(str).str.strip()
    df_mensual['Razón Social'] = df_mensual['Razón Social'].astype(str).str.strip()
    
    df_mensual['RUC - Razón Social'] = df_mensual['RUC'] + " - " + df_mensual['Razón Social']
    return df, df_mensual

df, df_mensual = cargar_datos()
df_mensual['Razón Social'] = df_mensual['Razón Social'].astype(str).str.strip()

st.title("Análisis de Contratos OSCE")

ruc_opciones = ["Todos"] + sorted(df['RUC - Razón Social'].dropna().unique())
años_opciones = ["Todos"] + sorted(df_mensual['Año'].dropna().unique())

ruc_seleccionados = st.sidebar.multiselect(
    "Seleccionar RUC - Razón Social",
    options=ruc_opciones,
    default=[])

años_seleccionados = st.sidebar.multiselect(
    "Seleccionar Año(s)",
    options=años_opciones,
    default=[])

ruc_final = sorted(df['RUC - Razón Social'].dropna().unique()) if "Todos" in ruc_seleccionados else ruc_seleccionados
años_final = sorted(df_mensual['Año'].dropna().unique()) if "Todos" in años_seleccionados else años_seleccionados

df_filtrado = df[df['RUC - Razón Social'].isin(ruc_final)]

if años_final:
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha de Firma de Contrato'].dt.year >= min(años_final)) &
        (df_filtrado['Fecha de Firma de Contrato'].dt.year <= max(años_final))]


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

    st.header("📈 Evolución Mensual de Contratos")

    df_grafico = df_mensual[df_mensual['RUC - Razón Social'].isin(ruc_final)]
    df_grafico = df_grafico[df_grafico['Fecha Periodo'].dt.year.isin(años_final)]

    df_resumen = df_grafico.groupby(["Fecha Periodo", "RUC", "Razón Social"], as_index=False).agg({
        "Valor Mensual proporcional": "sum",
        "Contratos": "sum"
    })

    df_resumen['Fuente'] = 'Real'
    df_resumen = df_resumen.sort_values("Fecha Periodo")

    figbar01 = px.bar(
        df_resumen,
        x="Fecha Periodo", 
        y="Valor Mensual proporcional",
        color="Razón Social",
        hover_data={"Valor Mensual proporcional": ":,.2f", "RUC": True, "Contratos":True},
        labels={"Valor Mensual proporcional": "Valor (S/.)"},
        title="Evolución Mensual de Contratos apilados",
    )

    figbar01.update_layout(
        xaxis_title="Periodo",
        yaxis_title="Valor Mensual proporcional (S/.)",
        legend_title="Razón Social",
        xaxis_tickformat="%Y %B",
        xaxis_tickangle=-45,
        hovermode="x unified",
        bargap=0.2,
        height=500,
    )

    st.plotly_chart(figbar01, use_container_width=True)

    figbar02 = px.bar(
        df_resumen,
        x="Fecha Periodo", 
        y="Valor Mensual proporcional",
        color="Razón Social",
        hover_data={"Valor Mensual proporcional": ":,.2f", "RUC": True, "Contratos":True},
        labels={"Valor Mensual proporcional": "Valor (S/.)"},
        title="Evolución Mensual de Contratos agrupados",
    )

    figbar02.update_layout(
        xaxis_title="Periodo",
        yaxis_title="Valor Mensual proporcional (S/.)",
        legend_title="Razón Social",
        xaxis_tickformat="%Y %B",
        xaxis_tickangle=-45,
        barmode="group",
        bargap=0.2,
        height=500,
    )

    st.plotly_chart(figbar02, use_container_width=True)

    on = st.toggle("Activar proyección")

    if on:
        st.header("✏️ Proyección manual")
        
        VarNum = st.text_input("Ingresar cantidad de contratos a proyectar", 0)
        VarNum = int(VarNum)
        if VarNum < 0 or VarNum > 10:
            VarNum = st.text_input("Ingresar un número válido", 0)

        VarNum = int(VarNum)
        if VarNum > 0:
            st.text("Tabla de Ingreso de Datos")
            columnas = ["RUC", "Fecha de Firma de Contrato", "Fecha Prevista de FIn de Contrato", "Monto del Contrato Original", "% Participación RUC", "Contratos"]
            
            df_vacio = pd.DataFrame({
                "RUC": ["" for _ in range(VarNum)],
                "Fecha de Firma de Contrato": [pd.NaT for _ in range(VarNum)],
                "Fecha Prevista de FIn de Contrato": [pd.NaT for _ in range(VarNum)],
                "Monto del Contrato Original": [0.0 for _ in range(VarNum)],
                "% Participación RUC": [0.0 for _ in range(VarNum)],
                "Contratos": ["" for _ in range(VarNum)],
            })

            df_editado = st.data_editor(
                df_vacio,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Fecha de Firma de Contrato": st.column_config.DateColumn("Fecha de Firma de Contrato"),
                    "Fecha Prevista de FIn de Contrato": st.column_config.DateColumn("Fecha Prevista de FIn de Contrato"),
                }
            )
            
            onn = st.toggle("Clic para mostrar los cálculos")

            if onn:
                df_editado['Fecha de Firma de Contrato'] = pd.to_datetime(df_editado['Fecha de Firma de Contrato'], dayfirst=True, errors='coerce')
                df_editado['Fecha Prevista de FIn de Contrato'] = pd.to_datetime(df_editado['Fecha Prevista de FIn de Contrato'], dayfirst=True, errors='coerce')

                df_editado['Valor Mensual proporcional'] = df_editado['Monto del Contrato Original'] * df_editado['% Participación RUC'] / 100
                df_editado['Nro de dias'] = (df_editado['Fecha Prevista de FIn de Contrato'] - df_editado['Fecha de Firma de Contrato']).dt.days
                df_editado['Valor Mensual proporcional'] = (df_editado['Valor Mensual proporcional']/df_editado['Nro de dias'])*30
                df_editado['Valor Mensual proporcional'] = pd.to_numeric(df_editado['Valor Mensual proporcional'].astype(str).str.replace(',', ''),errors='coerce').fillna(0)

                fecha_inicio = df_editado['Fecha de Firma de Contrato'].min()
                fecha_fin = df_editado['Fecha Prevista de FIn de Contrato'].max()
                fechas_periodos = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='M')

                registro = []

                for periodo in fechas_periodos:
                    contratos_activos = df_editado[
                        (df_editado['Fecha de Firma de Contrato'] <= periodo) &
                        (df_editado['Fecha Prevista de FIn de Contrato'] >= periodo)
                    ].copy()
                    contratos_activos['Fecha Periodo'] = periodo
                    contratos_activos['Fuente'] = 'Proyectado'
                    contratos_activos = contratos_activos[['RUC', 'Fecha Periodo', 'Valor Mensual proporcional', 'Contratos', "Fuente"]]
                    registro.append(contratos_activos)
                
                df_mensual = pd.concat(registro, ignore_index=True)
                df_agregado = df_mensual.groupby(
                    ['RUC', 'Fecha Periodo'],
                    as_index=False
                )['Valor Mensual proporcional'].sum()

                df_conteo = df_mensual.groupby(['RUC', 'Fecha Periodo'])['Contratos'].nunique().reset_index()
                df_agregado = pd.merge(df_agregado, df_conteo, on=['RUC', 'Fecha Periodo'], how='left')
                df_agregado['Contratos'] = df_agregado['Contratos'].fillna(0).astype(int)
                df_agregado['Valor Mensual proporcional'] = df_agregado['Valor Mensual proporcional'].fillna(0)
                df_agregado['Fuente'] = 'Proyectado'
                
                RucRazon = df_filtrado[['RUC', 'Razón Social']].drop_duplicates()
                
                df_total = pd.concat([df_resumen, df_agregado], axis=0)
                df_total = df_total.groupby(['RUC', 'Fecha Periodo', 'Fuente'], as_index=False).sum()
                df_total = df_total.merge(RucRazon, on='RUC', how='left')

                fig = px.bar(
                    df_total,
                    x="Fecha Periodo",
                    y="Valor Mensual proporcional",
                    color="RUC",
                    pattern_shape="Fuente",
                    hover_data={
                        "Valor Mensual proporcional": ":,.2f",
                        "RUC": True,
                        "Contratos": True,
                        "Fuente": True
                    },
                    labels={"Valor Mensual proporcional": "Valor (S/.)"},
                    title="Evolución Mensual de Contratos",
                )

                fig.update_layout(
                    xaxis_title="Periodo",
                    yaxis_title="Valor Mensual proporcional (S/.)",
                    legend_title="RUC",
                    xaxis_tickformat="%Y %B",
                    xaxis_tickangle=-45,
                    hovermode="x unified",
                    bargap=0.2,
                    barmode="stack",
                    height=500,
                )

                st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Por favor selecciona al menos un año")