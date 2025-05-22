# dashboard_clinica.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Usuarios autorizados
USERS = {
    "admin": "1234",
    "cliente1": "pass123",
    "cliente2": "demo2024"
}

def login():
    st.title("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_btn = st.button("Ingresar")

    if login_btn:
        if USERS.get(username) == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success("Acceso concedido.")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
# Inicializar estado
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()  # Detiene ejecución hasta que se autentique


if st.button("Cerrar sesión"):
    st.session_state["logged_in"] = False
    st.experimental_rerun()



# Título
st.title("📊 Dashboard Clínico Odontológico")

# Subida del archivo
archivo = st.file_uploader("Carga el archivo CSV de atenciones", type="csv")

if archivo is not None:
    df = pd.read_csv(archivo, parse_dates=["Fecha"])

    # Filtros
    st.sidebar.header("Filtros")
    odontologos = st.sidebar.multiselect("Odontólogo", options=df["Odontólogo"].unique(), default=df["Odontólogo"].unique())
    fechas = st.sidebar.date_input("Rango de fechas", [df["Fecha"].min(), df["Fecha"].max()])
    
    # Aplicar filtros
    df = df[df["Odontólogo"].isin(odontologos)]
    df = df[(df["Fecha"] >= pd.to_datetime(fechas[0])) & (df["Fecha"] <= pd.to_datetime(fechas[1]))]

    # KPIs principales
    total_consultas = df[df["Asistió"] == "Sí"].shape[0]
    ingresos_totales = df[df["Asistió"] == "Sí"]["Costo"].sum()
    ticket_promedio = df[df["Asistió"] == "Sí"]["Costo"].mean()

    st.metric("🦷 Total Consultas", total_consultas)
    st.metric("💰 Ingresos Totales ($)", f"{ingresos_totales:.2f}")
    st.metric("🎟️ Ticket Promedio ($)", f"{ticket_promedio:.2f}")

    # Gráfico de ingresos por especialidad
    ingresos_especialidad = df[df["Asistió"] == "Sí"].groupby("Especialidad")["Costo"].sum()
    st.subheader("Ingresos por Especialidad")
    st.bar_chart(ingresos_especialidad)

    # Consultas por día
    st.subheader("Consultas por Día")
    consultas_dia = df[df["Asistió"] == "Sí"].groupby("Fecha").size()
    st.line_chart(consultas_dia)

    # Forma de pago
    st.subheader("Distribución por Forma de Pago")
    pagos = df[df["Asistió"] == "Sí"]["Forma_de_pago"].value_counts()
    st.pyplot(pagos.plot.pie(autopct='%1.1f%%', ylabel='').figure)

else:
    st.info("Carga un archivo para ver el dashboard.")
