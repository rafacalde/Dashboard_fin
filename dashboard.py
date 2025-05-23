# dashboard_clinica.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd




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

    if st.button("Ingresar"):
        if USERS.get(username) == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
        else:
            st.error("Usuario o contraseña incorrectos.")
# Inicializar estado
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Mostrar login solo si no ha iniciado sesión
if not st.session_state["logged_in"]:
    login()
    st.stop()


# ----------------- CARGA DE DATOS DESDE GOOGLE SHEETS -----------------
import pandas as pd

@st.cache_data
def cargar_datos():
    file_id = "1joOz_ZxUDgfZZ-r3F0XjdNsUoSmXJEBg"  # <-- cambia esto por tu ID
    url = f"https://drive.google.com/uc?id={file_id}"
    df = pd.read_csv(url)
    return df

# Título
st.title("📊 Dashboard Clínico Odontológico")

# Subida del archivo
archivo = st.file_uploader("Carga el archivo CSV de atenciones", type="csv")

# ----------------- DASHBOARD -----------------
st.title("📊 Dashboard Clínico Odontológico")

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
