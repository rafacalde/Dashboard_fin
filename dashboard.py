# dashboard_clinica.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------- LOGIN --------------------
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

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# -------------------- CONEXIÓN A GOOGLE SHEETS --------------------
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def conectar_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    creds_dict = st.secrets["gcp_service_account"]
    
    # La clave privada puede tener problemas con \n, reemplazamos si es necesario:
    if '\\n' in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

st.write(st.secrets.keys())  # Esto te dirá si 'gcp_service_account' está presente


client = conectar_sheets()
spreadsheet_id = "1wgQf8IZFSVoSPLrluOVrjygDVh_0QqJsDOpKUHozBz8"
sheet = client.open_by_key(spreadsheet_id).worksheet("Pacientes")




# -------------------- CARGA DE DATOS CSV DESDE DRIVE --------------------
@st.cache_data
def cargar_datos():
    file_id = "1joOz_ZxUDgfZZ-r3F0XjdNsUoSmXJEBg"  # Tu ID de archivo
    url = f"https://drive.google.com/uc?id={file_id}"
    df = pd.read_csv(url)

    # Verificamos si la columna 'Fecha' existe antes de convertirla
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")  # evita errores si hay fechas mal escritas
    else:
        st.warning("⚠️ El archivo no contiene una columna llamada 'Fecha'. Algunas funciones podrían no funcionar.")
    return df

def guardar_paciente(nombre, edad, motivo):
    client = conectar_sheets()
    sheet = client.open("nombre_de_tu_paciente").worksheet("Pacientes")
    nueva_fila = [nombre, edad, motivo]
    sheet.append_row(nueva_fila)





# -------------------- INTERFAZ PRINCIPAL --------------------
st.title("📊 Dashboard Clínico Odontológico")


menu = st.sidebar.radio("Selecciona una opción", ["Visualización", "Agregar paciente"])

# -------------------- VISUALIZACIÓN --------------------
if menu == "Visualización":
    st.subheader("📈 Visualización de datos clínicos")

    st.sidebar.header("Filtros")
    odontologos = st.sidebar.multiselect("Odontólogo", options=df["Odontólogo"].unique(), default=df["Odontólogo"].unique())
    fechas = st.sidebar.date_input("Rango de fechas", [df["Fecha"].min(), df["Fecha"].max()])

    df_filtrado = df[df["Odontólogo"].isin(odontologos)]
    df_filtrado = df_filtrado[(df_filtrado["Fecha"] >= pd.to_datetime(fechas[0])) & (df_filtrado["Fecha"] <= pd.to_datetime(fechas[1]))]

    total_consultas = df_filtrado[df_filtrado["Asistió"] == "Sí"].shape[0]
    ingresos_totales = df_filtrado[df_filtrado["Asistió"] == "Sí"]["Costo"].sum()
    ticket_promedio = df_filtrado[df_filtrado["Asistió"] == "Sí"]["Costo"].mean()

    st.metric("🦷 Total Consultas", total_consultas)
    st.metric("💰 Ingresos Totales ($)", f"{ingresos_totales:.2f}")
    st.metric("🎟️ Ticket Promedio ($)", f"{ticket_promedio:.2f}")

    ingresos_especialidad = df_filtrado[df_filtrado["Asistió"] == "Sí"].groupby("Especialidad")["Costo"].sum()
    st.subheader("Ingresos por Especialidad")
    st.bar_chart(ingresos_especialidad)

    st.subheader("Consultas por Día")
    consultas_dia = df_filtrado[df_filtrado["Asistió"] == "Sí"].groupby("Fecha").size()
    st.line_chart(consultas_dia)

    st.subheader("Distribución por Forma de Pago")
    pagos = df_filtrado[df_filtrado["Asistió"] == "Sí"]["Forma_de_pago"].value_counts()
    st.pyplot(pagos.plot.pie(autopct='%1.1f%%', ylabel='').figure)

# -------------------- FORMULARIO PARA AGREGAR PACIENTE --------------------
elif menu == "Agregar paciente":
    st.subheader("📝 Agregar nuevo paciente")

    with st.form("form_paciente"):
        nombre = st.text_input("Nombre del paciente")
        edad = st.number_input("Edad", min_value=0, max_value=120, step=1)
        motivo = st.text_area("Motivo de consulta")

        submitted = st.form_submit_button("Guardar")
        if submitted:
            if nombre and motivo:
                guardar_paciente(nombre, edad, motivo)
                st.success(f"✅ Paciente {nombre} guardado con éxito.")
            else:
                st.error("Por favor completa todos los campos.")
