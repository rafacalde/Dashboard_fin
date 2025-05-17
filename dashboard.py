import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Financiero", layout="centered")
st.title("📊 Dashboard Financiero para Pequeños Negocios")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Verificación de columnas necesarias
        required_cols = ['Mes', 'Ventas', 'Costos', 'Gastos Operativos']
        if not all(col in df.columns for col in required_cols):
            st.error(f"El archivo debe contener las columnas: {', '.join(required_cols)}")
        else:
            # Cálculo de KPIs
            df['Ganancia Bruta'] = df['Ventas'] - df['Costos']
            df['Ganancia Neta'] = df['Ganancia Bruta'] - df['Gastos Operativos']
            df['Margen Neto (%)'] = round((df['Ganancia Neta'] / df['Ventas']) * 100, 2)

            st.success("✅ Datos procesados correctamente")

            # Mostrar tabla
            st.subheader("📋 Resumen de Datos")
            st.dataframe(df)

            # Mostrar métricas totales
            total_ventas = df['Ventas'].sum()
            total_neta = df['Ganancia Neta'].sum()
            promedio_margen = df['Margen Neto (%)'].mean()

            col1, col2, col3 = st.columns(3)
            col1.metric("Ventas Totales", f"${total_ventas:,.2f}")
            col2.metric("Ganancia Neta", f"${total_neta:,.2f}")
            col3.metric("Margen Neto Prom.", f"{promedio_margen:.2f}%")

            # Gráficos
            st.subheader("📈 Gráficos de Tendencia")
            fig, ax = plt.subplots()
            df.plot(x='Mes', y=['Ventas', 'Costos', 'Ganancia Neta'], marker='o', ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Descargar resultados
            st.subheader("⬇️ Descargar resultados")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar como CSV", csv, "resultados_financieros.csv", "text/csv")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo con las columnas: Mes, Ventas, Costos, Gastos Operativos")
