import pandas as pd 
import streamlit as st
import json
import plotly.express as px
from PIL import Image
import folium
from streamlit_folium import folium_static
import datetime as po
import matplotlib.pyplot as plt

rjson = "./data/data.json"

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
                "promedio": mediciones["promedio"],
                "maximo": mediciones["maximo"],
                "minimo": mediciones["minimo"],
                "peak": mediciones["peak"]
            }
        )

df = pd.DataFrame(data)

df["fecha"] = pd.to_datetime(df["fecha"])

fecha_inicio = pd.to_datetime("2025-05-02")
fecha_final = pd.to_datetime("2025-05-17")

todo = ["Alamar", "Residencia Estudiantil Bahia"]
todos = []

for ubic in todo:
    todos.append(
        df[
            (df["ubicacion"] == ubic) &
            (df["fecha"] >= fecha_inicio) &
            (df["fecha"] <= fecha_final)
        ]
        .groupby(["periodo"])["promedio"]
        .mean()
        .reset_index()
        .assign(ubicacion=ubic)
    )

if todos:
    df_final = pd.concat(todos, ignore_index=True)
    
    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>Comparación entre la Residencia y Alamar</h2>")

    
    fig = px.bar(
        df_final,
        x="periodo",
        y="promedio",
        color="periodo",
        color_discrete_map={
            "mañana": "#16610E",  
            "tarde": "#F97A00",   
            "noche": "#FED16A" 
        },
        facet_col="ubicacion"
    )
    fig.update_xaxes(title_text="Períodos")

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    fig.update_layout(
        xaxis_title="Períodos",
        yaxis_title="Nivel de ruido (dB)",
        legend_title="Período del día",
        template="plotly_white"
    )

    st.plotly_chart(fig)

st.markdown("""
            🔎 ¿Qué estamos viendo aquí?

Este gráfico compara los niveles de ruido registrados en dos lugares clave durante el mismo período de tiempo:
📍 Alamar y 📍 la Residencia Estudiantil Bahía.

La medición en Alamar se hizo cerca de la beca que está allá, o sea, bastante cerca del entorno donde viven estudiantes también.

La idea fue tomar 10 días (del 2 al 17 de mayo de 2025) y mirar cómo se comporta el ruido en esos lugares durante tres momentos del día:
🌅 mañana, ☀️ tarde y 🌙 noche.

🎯 Mi objetivo fue ver cómo se comporta el ruido en estos dos lugares durante el día.
Quería responder preguntas como:

— ¿Dónde hay más ruido?

— ¿Hay momentos más críticos en alguna de las dos ubicaciones?

💥 En resumen, busco entender cómo el entorno sonoro afecta la vida cotidiana, especialmente en lugares donde vivimos estudiantes.
                """)
st.markdown("---")
        
#---------------------

df["fecha"] = pd.to_datetime(df["fecha"])

residencia = df[df["ubicacion"] == "Residencia Estudiantil Bahia"]

residencia["dia_semana"] = residencia["fecha"].dt.day_name()
residencia["semana"] = residencia["fecha"].dt.isocalendar().week

residencia["dia_semana"] = pd.Categorical(residencia["dia_semana"],  ordered=True)

resumen = residencia.groupby(["semana", "dia_semana"])["promedio"].mean().reset_index()

fig = px.bar(
    resumen,
    x="dia_semana",
    y="promedio",
    color="semana",
    barmode="group",
    title="🔊 Tendencia semanal del ruido según el día de la semana\nResidencia Estudiantil (todas las semanas)",
    labels={"dia_semana": "Días", "promedio": "Promedio de ruido (dB)", "semana": "Semana"},
    color_discrete_sequence=px.colors.qualitative.Vivid
)

fig.update_layout(
    template="plotly_dark",
    xaxis_tickangle=-30,
    title_font_size=18,
    font=dict(size=14),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

