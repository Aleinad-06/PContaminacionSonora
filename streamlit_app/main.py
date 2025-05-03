import pandas as pd 
import streamlit as st
import json
import os 
import folium
from streamlit_folium import folium_static, st_folium

rjson = "data.json"

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

st.text("Toda la Informacion")
    
df


maps = []
for ubimap in data:
    maps.append(
        {
            "nombre": ubimap["ubicacion"],
            "lat": ubimap["coordenadas"]["lat"],
            "lon": ubimap["coordenadas"]["lon"]        
        })

dfmaps = pd.DataFrame(maps)

mapa = folium.Map(location=(23.0540698, -82.345189), zoom_start=11)

for i in range(len(dfmaps)):
    folium.Marker(
        location=[dfmaps.loc[i, "lat"], dfmaps.loc[i, "lon"]],
        popup=dfmaps.loc[i, "nombre"]
    ).add_to(mapa)

folium_static(mapa, width=700)

