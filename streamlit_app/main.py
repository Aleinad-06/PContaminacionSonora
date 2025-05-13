import pandas as pd 
import streamlit as st
import json
import folium
from streamlit_folium import folium_static, st_folium

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

df_grafico = df.pivot_table(index= "fecha", columns= "periodo", values= "maximo").reset_index()

st.subheader("Evolución de los Decibeleios Máximo por el Periodo del Día")
st.area_chart(
    df_grafico.set_index("fecha"),
    use_container_width= True,
    color=["#FF9F43", "#FF6B6B", "#48DBFB"],
    height= 400
)

st.subheader("Picos Máximos Registrados (peak)")
st.line_chart(
    df.pivot_table(index= "fecha", columns= "periodo", values= "peak").reset_index().set_index("fecha"), 
    use_container_width= True,
    color=["#EA047E", "#FF6D28", "#FCE700"],
    height=400
)

st.subheader("Evolución de los Decibeleios mínimo por el Periodo del Día (minimo)")
st.line_chart(
    df.pivot_table(index= "fecha", columns= "periodo", values= "minimo").reset_index().set_index("fecha"),
    use_container_width= True,
    color= ["#323EDD","#DC2ADE","#E8F044"],
    height= 400
)

st.subheader("Análisis")
col1, col2 = st.columns(2)

with col1:
    st.metric("Mayor nivel registrado (Peak)", f"{df['peak'].max()} dB", 
              help="Máximo pico de decibelios registrado en cualquier período")

with col2:
    st.metric("Período más ruidoso en promedio",
              f"{df.groupby('periodo')['maximo'].mean().idxmax()} ({(df.groupby('periodo')['maximo'].mean().max()):.1f} dB)")   

st.markdown("""
**Leyenda:**
- 🟠 **Mañana:** 6:30 - 12:30
- 🔴 **Tarde:** 12:30 - 18:30
- 🔵 **Noche:** 18:30 - 6:30

**Niveles de referencia según OMS (2021):**
- <55 dB 🔊: Nivel recomendado para áreas residenciales durante el día 
- 55-65 dB ⚠️: Puede causar molestias y alteraciones del sueño
- >65 dB 🔴: Riesgo de enfermedades cardiovasculares con exposición prolongada
- >75 dB 🚨: Daño auditivo potencial según exposición

**Referencia nocturna especial:**
- <45 dB 🌙: Nivel recomendado para horario nocturno
  *(Para prevenir alteraciones del sueño - OMS)*
""")
    
# xd = ["mañana", "tarde", "noche"]
# phor = []
# mañana = []
# tarde = []
# noche = []

# for j in range(len(data)):
#     if data[j]["periodo"] in xd :
#         phor.append(data[j])
        
# for i in range(len(phor))  :
#     if phor[i]["periodo"] == "mañana":
#         mañana.append(
#             {
#                 "periodos": phor[i]["periodo"],
#                 "mediciones": phor[i]["mediciones"]
#             }
#         )
    
#     elif phor[i]["periodo"] == "tarde":
#         tarde.append(
#             {
#                 "periodos": phor[i]["periodo"],
#                 "mediciones": phor[i]["mediciones"]
#             }
#         )
    
#     else:
#         noche.append(
#             {
#                 "periodos": phor[i]["periodo"],
#                 "mediciones": phor[i]["mediciones"]
#             }
#         )
        
# dfm = st.dataframe(mañana)
# dft = st.dataframe(tarde)
# dfn = st.dataframe(noche)

 
