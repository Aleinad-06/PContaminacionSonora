import pandas as pd
import streamlit as st
import json
import plotly.express as px
from PIL import Image
import folium
from streamlit_folium import folium_static
import datetime as dt

def load_data(filepath):
    """Carga los datos desde el archivo JSON"""
    with open(filepath, "r", encoding="utf-8") as file:
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
            data.append({
                "fecha": fecha,
                "dia_semana": dia_semana,
                "ubicacion": nombre_ubicacion,
                "coordenadas": coordenadas,
                "periodo": periodo,
                "promedio": mediciones["promedio"],
                "maximo": mediciones["maximo"],
                "minimo": mediciones["minimo"],
                "peak": mediciones["peak"]
            })
    
    df = pd.DataFrame(data)
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")
    return df

def show_main_header():
    """Muestra el encabezado principal de la aplicación"""
    st.html("<h1 style='font-size: 50px'>🔊 “Un Día con Ruido: Descubre cómo suena vivir en la <span style='color: #FF7601'> Residencia Bahía</span>”</h1>")
    st.markdown("¿Alguna vez te has preguntado cómo suena el lugar donde vives? Hoy puedes descubrirlo. "
                "Selecciona una fecha del último mes y explora cómo varió el **nivel de ruido** en la "
                "**Residencia Estudiantil Bahía**, durante la mañana, tarde y noche.")

def plot_daily_noise(df, date):
    """Grafica los niveles de ruido para un día específico"""
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
            st.html("<h1 style='font-size: 20px ; color: #E6521F'>😡 **¡Día ruidoso!** El pico de ruido fue muy alto. Tal vez fue una fiesta o mucho tráfico.</h1>")
        elif pico_maximo >= 65:
            st.html("<h1 style='font-size: 20px ; color: #FB9E3A'>😐 **Nivel moderado.** El ruido estuvo presente, pero no fue extremo.</h1>")
        else:
            st.html("<h1 style='font-size: 20px ; color: #FCEF91'>😊 **Día tranquilo.** La residencia tuvo niveles de ruido bastante bajos. ¡Aprovecha para descansar!</h1>")

        image = Image.open("./imagen/imagen4.jpg")
        st.image(image, use_container_width=True)

        st.divider()
        st.markdown("🧩 ¿Te sorprendió lo que viste? Este es solo **un día** en la vida sonora de la residencia. "
                    "Imagina todo lo que podríamos descubrir si más personas se suman a escuchar el entorno.")
        st.markdown("👉 Sigue explorando el ruido. ¡La ciencia también se escucha!")
    else:
        st.warning("⚠️ No hay datos para la fecha seleccionada. Solo están disponibles: Lunes, Miércoles, Viernes y Sábado.")

def create_map(data):
    """Crea un mapa con las ubicaciones de los sensores"""
    maps = []
    for ubimap in data:
        maps.append({
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

def plot_max_noise_evolution(df_ubinombre):
    """Grafica la evolución de los decibelios máximos por período"""
    if not df_ubinombre.empty:  
        df_grafico = df_ubinombre.pivot_table(index="fecha", columns="periodo", values="maximo").reset_index()
        
        st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>Evolución de los Decibelelios Máximo por el Periodo del Día<h2>")
       
        st.line_chart(
            df_grafico.set_index("fecha"),
            use_container_width=True,
            color=["#FF9F43", "#FF6B6B", "#48DBFB"],
            height=400
        )
        
        
def plot_peak_noise(df_ubinombre):
    """Grafica los picos máximos de ruido registrados"""
    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>📊Picos Máximos Registrados (peak)<h2>")
    st.line_chart(
        df_ubinombre.pivot_table(index="fecha", columns="periodo", values="peak").reset_index().set_index("fecha"), 
        use_container_width=True,
        color=["#EA047E", "#FF6D28", "#FCE700"],
        height=400
    )
    
    st.html("<h4>Sonido de la sirena</h4>")  
    audio = open("./musica/camion-de-bomberos.mp3", "rb")
    st.audio(audio.read(), format="audio/mp3")
    

def plot_min_noise_evolution(df_ubinombre):
    """Grafica la evolución de los decibelios mínimos por período"""
    st.html("<h2 style='color: #F1EFEC; font-family: Times ; text-align: center'>Evolución de los Decibeleios mínimo por el Periodo del Día (minimo)<h2>")
    st.line_chart(
        df_ubinombre.pivot_table(
            index="fecha", 
            columns="periodo",
            values="minimo").reset_index().set_index("fecha"),
        use_container_width=True,
        color=["#323EDD","#DC2ADE","#E8F044"],
        height=400
    )

def show_summary_metrics(df):
    """Muestra las métricas resumen"""
    st.subheader("Resumen")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Mayor nivel registrado (Peak)",
        f"{df['peak'].max()} dB", 
        help="Máximo pico de decibelios registrado en cualquier período")

    with col2:
        st.metric("Período más ruidoso en promedio",
        f"{df.groupby('periodo')['maximo'].mean().idxmax()} ({(df.groupby('periodo')['maximo'].mean().max()):.1f} dB)")
    
        st.metric("Menor nivel registrado",
        f"{df.groupby('periodo')['minimo'].mean().idxmin()} ({(df.groupby('periodo')['minimo'].mean().min()):.1f} dB)")

def plot_noise_limits(df):
    """Grafica los días que se superaron los límites de ruido"""
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

def plot_trend_noise(df_ubinombre):
    """Grafica la tendencia del nivel promedio de ruido"""
    df_trend = df_ubinombre.groupby(["fecha", "periodo"])["promedio"].mean().reset_index()
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

    

