import pandas as pd 
import streamlit as st
import json
import plotly.express as px
from PIL import Image
import folium
from streamlit_folium import folium_static

rjson = "../data/data.json"

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

df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")

st.title("🔊 “Un Día con Ruido: Descubre cómo suena vivir en la Residencia Bahía”")

st.markdown("¿Alguna vez te has preguntado cómo suena el lugar donde vives? Hoy puedes descubrirlo. "
            "Selecciona una fecha del último mes y explora cómo varió el **nivel de ruido** en la "
            "**Residencia Estudiantil Bahía**, durante la mañana, tarde y noche.")

date = st.date_input("Selecciona el día para explorar cómo se comportó el ruido", value=pd.to_datetime("2025-05-23"))
dia = df[df["fecha"].dt.date == date]


if not dia.empty:
    datos = dia[["periodo", "promedio", "maximo", "minimo", "peak"]]

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

    pico_maximo = datos["peak"].max()
    if pico_maximo >= 80:
        st.markdown("😡 **¡Día ruidoso!** El pico de ruido fue muy alto. Tal vez fue una fiesta o mucho tráfico.")
    elif pico_maximo >= 65:
        st.markdown("😐 **Nivel moderado.** El ruido estuvo presente, pero no fue extremo.")
    else:
        st.markdown("😊 **Día tranquilo.** La residencia tuvo niveles de ruido bastante bajos. ¡Aprovecha para descansar!")

    image = Image.open("../imagen/imagen4.jpg")
    st.image(image, use_container_width=True)

    st.markdown("---")
    st.markdown("🧩 ¿Te sorprendió lo que viste? Este es solo **un día** en la vida sonora de la residencia. "
                "Imagina todo lo que podríamos descubrir si más personas se suman a escuchar el entorno.")
    st.markdown("👉 Sigue explorando el ruido. ¡La ciencia también se escucha!")

else:
    st.warning("⚠️ No hay datos para la fecha seleccionada. Solo están disponibles: Lunes, Miércoles, Viernes y Sábado.")



#-----------------------


st.title("Y Porque no ver algo más interesante")
mostrar_analisis = st.button("Veamos los Análisis")

if mostrar_analisis:
    
#--------------------

    maps = []
    for ubimap in data:
        maps.append(
            {
                "nombre": ubimap["ubicacion"],
                "lat": ubimap["coordenadas"]["lat"],
                "lon": ubimap["coordenadas"]["lon"]        
            }
        )

    dfmaps = pd.DataFrame(maps)

    mapa = folium.Map(location=(23.0540698, -82.345189), zoom_start=11)

    for i in range(len(dfmaps)):
        folium.Marker(
            location=[dfmaps.loc[i, "lat"], dfmaps.loc[i, "lon"]],
            popup=dfmaps.loc[i, "nombre"]
        ).add_to(mapa)

    folium_static(mapa, width=700)


#---------------------

    df_grafico = df.pivot_table(index= "fecha", columns= "periodo", values= "maximo").reset_index()
    st.subheader("Evolución de los Decibelelios Máximo por el Periodo del Día")
    st.area_chart(
        df_grafico.set_index("fecha"),
        use_container_width= True,
        color=["#FF9F43", "#FF6B6B", "#48DBFB"],
        height= 400
    )

    st.subheader("📊Picos Máximos Registrados (peak)")
    st.line_chart(
        df.pivot_table(index= "fecha", columns= "periodo", values= "peak").reset_index().set_index("fecha"), 
        use_container_width= True,
        color=["#EA047E", "#FF6D28", "#FCE700"],
        height=400
    )
    
    st.markdown("""A lo largo del periodo analizado en la Residencia Estudiantil Bahía,
                se registraron los valores peak de ruido correspondientes a diferentes momentos del día. 
                Estos picos reflejan los instantes de mayor intensidad sonora en cada jornada,
                lo cual permite identificar variaciones y posibles anomalías en el ambiente acústico.

🔊 En uno de los días, el peak superó los 100 dB, debido al paso de un camión de bomberos con la sirena encendida.
Este evento puntual generó una anomalía sonora significativa dentro del registro general.

🎯 El propósito de este análisis es que el usuario pueda observar con más detalle el comportamiento de los picos sonoros por día,
reconociendo cuándo ocurren situaciones inusuales y entendiendo mejor la dinámica real del ruido en su entorno.""")
    
    st.html(
        "<h4>Sonido de la sirena</h4>"
    )  
    audio = open("../musica/camion-de-bomberos.mp3", "rb")
    st.audio(audio.read(), format="audio/mp3")
       
    st.subheader("Evolución de los Decibeleios mínimo por el Periodo del Día (minimo)")
    st.line_chart(
        df.pivot_table(index= "fecha", columns= "periodo", values= "minimo").reset_index().set_index("fecha"),
        use_container_width= True,
        color= ["#323EDD","#DC2ADE","#E8F044"],
        height= 400
    )

    st.subheader("Análisis")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Mayor nivel registrado (Peak)", f"{df['peak'].max()} dB", 
        help="Máximo pico de decibelios registrado en cualquier período")

    with col2:
        st.metric("Período más ruidoso en promedio",
        f"{df.groupby('periodo')['maximo'].mean().idxmax()} ({(df.groupby('periodo')['maximo'].mean().max()):.1f} dB)")

    st.markdown("""
    **Leyenda:**
    -  **Mañana:** 6:30 - 12:30
    -  **Tarde:** 12:30 - 18:30
    -  **Noche:** 18:30 - 6:30

    **Niveles de referencia según OMS :**
    - <55 dB 🔊: Nivel recomendado para áreas residenciales durante el día 
    - 55-65 dB ⚠️: Puede causar molestias y alteraciones del sueño
    - >65 dB 🔴: Riesgo de enfermedades cardiovasculares con exposición prolongada
    - >75 dB 🚨: Daño auditivo potencial según exposición

    **Referencia nocturna especial:**
    - <45 dB 🌙: Nivel recomendado para horario nocturno
    *(Para prevenir alteraciones del sueño - OMS)*
    """)
    
