import pandas as pd 
import streamlit as st
import json
import plotly.express as px
from PIL import Image
import folium
from streamlit_folium import folium_static


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

df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")

st.html("<h1 style= 'font-size: 50px'>🔊 “Un Día con Ruido: Descubre cómo suena vivir en la <span style= 'color: #FF7601'> Residencia Bahía</span>”</h1>")

st.markdown("¿Alguna vez te has preguntado cómo suena el lugar donde vives? Hoy puedes descubrirlo. "
            "Selecciona una fecha del último mes y explora cómo varió el **nivel de ruido** en la "
            "**Residencia Estudiantil Bahía**, durante la mañana, tarde y noche.")

date = st.date_input("""Selecciona el día para explorar cómo se comportó el ruido    
                     ***Del 23 abr al 6 jun***""",
                     value=pd.to_datetime("2025-05-23"))
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
        st.html("<h1 style= 'font-size: 20px ; color: #E6521F'>😡 **¡Día ruidoso!** El pico de ruido fue muy alto. Tal vez fue una fiesta o mucho tráfico.</h1>")
    elif pico_maximo >= 65:
        st.html("<h1 style= 'font-size: 20px ; color: #FB9E3A'>😐 **Nivel moderado.** El ruido estuvo presente, pero no fue extremo.</h1>")
    else:
        st.html("<h1 style= 'font-size: 20px ; color: #FCEF91'>😊 **Día tranquilo.** La residencia tuvo niveles de ruido bastante bajos. ¡Aprovecha para descansar!</h1>")

    image = Image.open("./imagen/imagen4.jpg")
    st.image(image, use_container_width=True)

    st.markdown("---")
    st.markdown("🧩 ¿Te sorprendió lo que viste? Este es solo **un día** en la vida sonora de la residencia. "
                "Imagina todo lo que podríamos descubrir si más personas se suman a escuchar el entorno.")
    st.markdown("👉 Sigue explorando el ruido. ¡La ciencia también se escucha!")

else:
    st.warning("⚠️ No hay datos para la fecha seleccionada. Solo están disponibles: Lunes, Miércoles, Viernes y Sábado.")



#-----------------------


st.html("<h2 style='color: #FF7601' >⬇️Y porque no ver algo mas interesante⬇️</h2>")
mostrar_analisis = st.button("Veamos los Análisis😲")

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
    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>Evolución de los Decibelelios Máximo por el Periodo del Día<h2>")
    st.area_chart(
        df_grafico.set_index("fecha"),
        use_container_width= True,
        color=["#FF9F43", "#FF6B6B", "#48DBFB"],
        height= 400
    )
    st.markdown("""Durante el periodo observado, se evidencian variaciones notables en los niveles máximos de ruido según el momento del día.
                
🔵 La tarde domina con los picos más constantes y elevados, lo que sugiere una actividad intensa en ese horario.

🔴 La noche presenta algunos picos aislados, probablemente asociados a eventos puntuales o comportamientos anómalos.

🟠 La mañana muestra fluctuaciones irregulares, aunque generalmente por debajo de los niveles de la tarde.

Este comportamiento indica que el ruido ambiental varía significativamente según el período del día,
con la tarde como el tramo más ruidoso de forma sostenida.

🎯 Objetivo: Visualizar cómo varían los niveles máximos de decibelios por período del día y
detectar cuál de ellos tiende a registrar los valores más altos de forma sistemática.""")
    
    st.markdown("---")

#-----------------------

    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>📊Picos Máximos Registrados (peak)<h2>")
    st.line_chart(
        df.pivot_table(index= "fecha", columns= "periodo", values= "peak").reset_index().set_index("fecha"), 
        use_container_width= True,
        color=["#EA047E", "#FF6D28", "#FCE700"],
        height=400
    )
    
    st.markdown("""Los valores más altos de decibelios (picos) varían diariamente, con algunas fechas destacando por registrar niveles extremos.

💥 La tarde nuevamente sobresale con varios picos por encima de los 100 dB, lo cual sugiere eventos anómalos o momentos de alta actividad.

🌙 La noche y la mañana presentan también algunos valores elevados, lo que refuerza la idea de que los picos no siempre ocurren en horarios previsibles.

📌 Este análisis ayuda a detectar eventos atípicos o peligrosos para la salud auditiva, incluso si solo duran unos segundos.

🎯 Objetivo: Que el usuario pueda observar con más detalle el comportamiento de los picos sonoros por día, 
reconociendo cuándo ocurren situaciones inusuales y entendiendo mejor la dinámica real del ruido en su entorno.""")
    
    st.html(
        "<h4>Sonido de la sirena</h4>"
    )  
    audio = open("./musica/camion-de-bomberos.mp3", "rb")
    st.audio(audio.read(), format="audio/mp3")
    
    st.html(
        "<h4>Sonido del portazo</h4>"
    )
    # audio1 = open("./musica/.mp3", "rb")
    # st.audio(audio.read(), format="audio/mp3")
    
    st.markdown("---")
    
#-------------------------
    
    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>Evolución de los Decibeleios mínimo por el Periodo del Día (minimo)<h2>")
    st.line_chart(
        df.pivot_table(index= "fecha", columns= "periodo", values= "minimo").reset_index().set_index("fecha"),
        use_container_width= True,
        color= ["#323EDD","#DC2ADE","#E8F044"],
        height= 400
    )

    st.markdown("""Los niveles mínimos de decibeles se mantienen elevados a lo largo del periodo analizado,
                sin registrar caídas notables que indiquen momentos de verdadero silencio.
                
🔵 En la mañana se observan más fluctuaciones, destacando una leve baja el 23 de mayo (42 dB), posiblemente reflejando un instante de menor actividad.

🟣 La noche, sorprendentemente, no es la más silenciosa, manteniéndose cerca de los 50 dB de forma constante.

🟡 La tarde varía más, pero tampoco desciende a niveles bajos.

En resumen, el gráfico evidencia que el ruido es constante y persistente durante todos los períodos del día.

🎯 Objetivo: Permitir al usuario identificar si existen momentos de verdadero silencio durante el día y
comprender la persistencia del ruido ambiente, incluso en horarios tradicionalmente más tranquilos.""")

    st.markdown("---") 
       
#-----------------------

    st.subheader("Resumen")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Mayor nivel registrado (Peak)",
        f"{df['peak'].max()} dB", 
        help="Máximo pico de decibelios registrado en cualquier período")

    with col2:
        st.metric("Período más ruidoso en promedio",
        f"{df.groupby("periodo")["maximo"].mean().idxmax()} ({(df.groupby("periodo")["maximo"].mean().max()):.1f} dB)")
    
        st.metric("Menor nivel registrado",
        f"{df.groupby("periodo")["minimo"].mean().idxmin()} ({(df.groupby("periodo")["minimo"].mean().min()):.1f} dB)")
    
    st.markdown("---")
    
#------------------------------
    
    condiciones = []
    
    for i in range(len(df)):
        periodo = df.iloc[i]["periodo"]
        promedio = df.iloc[i]["promedio"]
        
        if periodo == "mañana" and promedio > 55:
            condiciones.append(True)
        elif periodo == "tarde" and promedio > 65:
            condiciones.append(True)
        elif periodo == "noche" and promedio > 45:
            condiciones.append(True)
        else:
            condiciones.append(False) 
    df["supera_limites"] = condiciones
    
    limites_por_periodo = df[df["supera_limites"]].groupby("periodo")["fecha"].nunique().reset_index(name="dias_superados")

    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>🌡️ Días en que se superaron los límites de ruido por período<h2>")
    fig = px.bar(
        limites_por_periodo,
        x="periodo",
        y="dias_superados",
        color="periodo",
        color_discrete_map={
            "mañana": "#FFD166",  
            "tarde": "#DC2525",   
            "noche": "#0B1D51" 
            },
        labels={"dias_superados": "Cantidad de días"}
    )
    st.plotly_chart(fig)

    st.markdown("""
    📌 Este gráfico muestra ***cuántas veces se superaron los niveles de ruido saludables***,
    según la OMS, para cada período del día: 
    (Teniendo una gran incidencia en la "mañana" y en la "noche")

    - **🌅 Mañana**: límite 55 dB
    - **🌞 Tarde**: límite 65 dB
    - **🌙 Noche**: límite 45 dB

    🎯 El objetivo es identificar en qué momentos del día el ambiente fue más ruidoso y si existe algún patrón recurrente de exposición a niveles sonoros potencialmente peligrosos.
    """)
    
    st.markdown("---")
    
#------------------------

    df_trend = df.groupby(["fecha", "periodo"])["promedio"].mean().reset_index()

    df_trend["fecha"] = pd.to_datetime(df_trend["fecha"], format="%y-%m-%d")
    df_trend = df_trend.sort_values("fecha")

    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>📈 Tendencia del nivel promedio de ruido por período<h2>")
    fig = px.line(
        df_trend,
        x="fecha",
        y="promedio",
        color="periodo",
        markers=True,
        line_shape="spline"
    )

    
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Nivel de ruido (dB)",
        legend_title="Período del día",
        template="plotly_white"
    )
    
    st.plotly_chart(fig)

    st.markdown("""
                Estuve midiendo el ruido en la Residencia durante más de un mes, en tres momentos: mañana, tarde y noche.
Y este gráfico me lo confirmó: no hay silencio real… en ningún momento.

🔵 En la mañana, el ruido sube y baja como una montaña rusa. Algunos días arranca tranquilo, otros parece que el día empieza con bocinas.

🟡 La tarde es la campeona del escándalo. Hay picos por encima de los 70 dB —eso equivale a tener tráfico intenso todo el tiempo. Sí, así como lo oyes (o lo sufres).

🟣 La noche decepciona. Pensé que sería el momento de más calma, pero se mantiene firme sobre los 55 dB. El descanso, al parecer, también tiene banda sonora.

📉 Lo que más me impactó es que no hay un solo día donde el ruido baje realmente. Siempre hay algo sonando, pitando, zumbando… aunque no lo registremos.

🎯 ¿Qué buscaba con esto? Saber si había momentos de verdadero silencio.
Y la respuesta fue clara: no los hay.
                """)
    
    st.markdown("---")
    
#----------------------------
    
    