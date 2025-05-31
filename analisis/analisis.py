import pandas as pd 
import streamlit as st
import json
import datetime
import plotly.express as px
from PIL import Image

rjson = "../jsons/data.json"

inf = []

with open(rjson, "r", encoding="utf-8") as file:
    inf = json.load(file)

data = []

for i in inf:

    fecha = i["tiempo"]["fecha"]
    dia_semana = i["tiempo"]["dia_semana"]
    nombre_ubicacion = i["ubicacion"]["nombre"]
    coordenadas = i["ubicacion"]["coordenadas"]
    
    for horarios in i["horarios"]:
        periodo = horarios["periodo"]
        mediciones = horarios["mediciones"]      
        data.append(
            {
                "fecha": fecha,
                "dia_semana": dia_semana,
                "ubicacion": nombre_ubicacion,
                "coordenadas": coordenadas,
                "periodo": periodo,
                "mediciones": mediciones
            }
        )

df = pd.DataFrame(data)
df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")

st.title("Distribución del ruido por día")
st.sidebar.header("Hola Hola")
date = st.sidebar.date_input(
    "Selecciona el día para que veas cómo se comportó el ruido",
    min_value=datetime.date(2025, 4, 23),
    max_value=datetime.date(2025, 5, 23)
)

dia = df[df["fecha"].dt.date == date]

mediciones = []
maximos = []
minimos = []
peaks = []
periodos = []

if not dia.empty:
    for idx, fila in dia.iterrows():
        medicion = fila["mediciones"]
        if isinstance(medicion, dict) and all(k in medicion for k in ["promedio", "maximo", "minimo", "peak"]):
            periodos.append(fila["periodo"])
            mediciones.append(medicion["promedio"])
            maximos.append(medicion["maximo"])
            minimos.append(medicion["minimo"])
            peaks.append(medicion["peak"])

    if periodos:
        datos = pd.DataFrame({
            "periodo": periodos,
            "promedio": mediciones,
            "maximo": maximos,
            "minimo": minimos,
            "peak": peaks
        })

        datos_melt = datos.melt(id_vars="periodo", var_name="Tipo", value_name="Nivel (dB)")

        fig = px.line(
            datos_melt,
            x="periodo",
            y="Nivel (dB)",
            color="Tipo",
            markers=True,
            title=f"Niveles de ruido el {date.strftime('%Y-%m-%d')}",
            labels={"periodo": "Periodo del día"},
            color_discrete_map={
                "promedio": "blue",
                "maximo": "orange",
                "minimo": "green",
                "peak": "red"
            }
        )
        fig.update_layout(template="plotly_dark", xaxis=dict(tickangle=45))
        st.plotly_chart(fig)
        image = Image.open("../imagen/imagen4.jpg")
        st.image(image, )
else:
    st.warning("No hay datos para la fecha seleccionada. Solo son Los días (Lunes, Miércoles, Viernes, Sábado)")
