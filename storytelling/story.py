import pandas as pd 
import streamlit as st
import json
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout="wide")

bahia = "./data/bahia.json"
alamar = "./data/alamar.json"

def cargar_datos(ruta_json, nombre_residencia):
    with open(ruta_json, "r", encoding="utf-8") as file:
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

    return pd.DataFrame(data)

df_bahia = cargar_datos(bahia, "Residencia Estudiantil Bahia")
df_alamar = cargar_datos(alamar, "Residencia Estudiantil Alamar")

df = pd.concat([df_bahia, df_alamar], ignore_index=True)



st.html("<h1 style= 'color: #E9A319; font-family: Times: text-agoin: center; font-size: 50px'>🌞 Bahía  vs. 🌙 Alamar: Dónde Reside el Ruido❓Serán 🌞 o 🌙 </h1>")
st.markdown("""Cada decibelio cuenta en nuestra vida académica. 
        Según la OMS, superar los 55 dB de día o 45 dB de noche no es solo molesto, 
        sino perjudicial para nuestra salud y rendimiento. 
        
Del 2 al 17 de mayo de 2025, medí rigurosamente el ambiente acústico en:


    🏢 Residencia Bahía: El corazón vibrante de la vida estudiantil

    🌳 Residencia Alamar: El refugio tradicional de los que buscan tranquilidad
 
Descubrimos patrones que explican por qué muchos llegan cansados a clases.""")

df["fecha"] = pd.to_datetime(df["fecha"])

fecha_inicio = pd.to_datetime("2025-05-02")
fecha_final = pd.to_datetime("2025-05-17")

df_filtrado = df[(df["fecha"] >= fecha_inicio) & (df["fecha"] <= fecha_final)]

opcion = st.selectbox("Selecciona que deseas Visualizar", ["maximo", "minimo","peak"])

todo = ["Residencia Estudiantil Alamar", "Residencia Estudiantil Bahia"]
todos = []

for ubic in todo:
    todos.append(
        df_filtrado[df_filtrado["ubicacion"] == ubic]
        .groupby(["periodo"])[opcion]
        .mean()
        .reset_index()
        .assign(ubicacion=ubic)
    )

if todos:
    df_final = pd.concat(todos, ignore_index=True)
    
    st.html("<h2 style='color: #C3FF93; font-family: Times ; text-align: center'>^_~👌Comportamiento entre Residencias</h2>")

    
    fig = px.bar(
        df_final,
        x="periodo",
        y=opcion,
        color="periodo",
        color_discrete_map={
            "mañana": "#16610E",  
            "tarde": "#F97A00",   
            "noche": "#FED16A" 
        },
        facet_col="ubicacion"
    )
    fig.update_xaxes(title_text=opcion)

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    fig.update_layout(
        yaxis_title="Nivel de ruido ({opcion}) (dB)",
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
st.divider()
        
#---------------------

bahia = df_filtrado[df_filtrado["ubicacion"] == "Residencia Estudiantil Bahia"].copy()
alamar = df_filtrado[df_filtrado["ubicacion"] == "Residencia Estudiantil Alamar"].copy()

def procesar_residencia(data):
    # Método más robusto para obtener nombres de días en español
    data["dia_semana"] = data["fecha"].dt.strftime('%A')
    dias_traduccion = {
        'Monday': 'Lunes',
        'Wednesday': 'Miércoles',
        'Friday': 'Viernes',
        'Saturday': 'Sábado'
    }
    data["dia_semana"] = data["dia_semana"].map(dias_traduccion)
    
    data["semana"] = data["fecha"].dt.isocalendar().week
    dias_orden = ['Lunes', 'Miércoles', 'Viernes', 'Sábado']
    data["dia_semana"] = pd.Categorical(data["dia_semana"], categories=dias_orden)
    return data

bahia = procesar_residencia(bahia)
alamar = procesar_residencia(alamar)
print(alamar)
with st.expander("🔍 Análisis Comparativo"):
    col1, col2 = st.columns(2)
    
    with col1:
        resumen_bahia = bahia.groupby(["semana", "dia_semana"])["promedio"].mean().reset_index()
        
        fig_bahia = px.bar(resumen_bahia, 
                           x="dia_semana",
                           y="promedio",
                           color="semana",
                           barmode="group",
                           title="🔊 Residencia Bahía - Tendencia semanal por día",
                           labels={"dia_semana": "Día", "promedio": "Promedio (dB)", "semana": "Semana"},
                           color_continuous_scale=px.colors.sequential.Viridis)
        
        fig_bahia.update_layout(template="plotly_dark", xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_bahia, use_container_width=True)

        heatmap_data = bahia.pivot_table(index='dia_semana',
                                         columns='periodo',
                                         values='promedio', 
                                         aggfunc='mean')
        
        fig_heat = px.imshow(heatmap_data, labels=dict(x="Período",
                                                        y="Día",
                                                        color="Decibeles"),
                                                        title="🕒 Patrones horarios - Residencia Bahía", 
                                                        color_continuous_scale='thermal')
        
        st.plotly_chart(fig_heat, use_container_width=True)

    with col2:
        resumen_alamar = alamar.groupby(["semana", "dia_semana"])["promedio"].mean().reset_index()
        
        fig_alamar = px.bar(resumen_alamar,
                            x="dia_semana", 
                            y="promedio",
                            color="semana",
                            barmode="group",
                            title="🔇 Residencia Alamar - Tendencia semanal por día",
                            labels={"dia_semana": "Día", "promedio": "Promedio (dB)", "semana": "Semana"},
                            color_continuous_scale=px.colors.sequential.Pinkyl)
        
        fig_alamar.update_layout(template="plotly_dark", xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_alamar, use_container_width=True)

        heatmap_data_alamar = alamar.pivot_table(index='dia_semana', 
                                                 columns='periodo', 
                                                 values='promedio', 
                                                 aggfunc='mean')
        
        fig_heat_alamar = px.imshow(heatmap_data_alamar, labels=dict(x="Período",
                                                                    y="Día", 
                                                                    color="Decibeles"),
                                                                    title="🕒 Patrones horarios - Residencia Alamar", 
                                                                    color_continuous_scale='ice')
        
        st.plotly_chart(fig_heat_alamar, use_container_width=True)

#--------------------------

with st.expander("📊 Análisis Estadístico Comparativo"):
    st.html("<h1  style='color: #0065F8; font-family: Times ; text-align: center'>Comparación estadística entre <span style='color: #B6F500'>Residencias<span></h1>")
    stats_bahia = bahia['promedio'].describe().rename('Bahía').agg(["count","mean", "min", "50%", "max"])
    stats_alamar = alamar['promedio'].describe().rename('Alamar').agg(["count","mean", "min", "50%", "max"])
    stats_comparativas = pd.concat([stats_bahia, stats_alamar], axis=1)
    st.dataframe(stats_comparativas.style.format("{:.2f}").background_gradient(cmap='Blues'))

    fig_dist = px.box(pd.concat([bahia.assign(Residencia="Bahía"), 
                                 alamar.assign(Residencia="Alamar")]),
                      x="Residencia", 
                      y="promedio", 
                      color="Residencia",
                      points="all",
                      title="📊 Distribución comparativa de niveles de ruido",
    color_discrete_map= {"Alamar": "#D2FF72","Bahía": "#73EC8B "})
    
    st.plotly_chart(fig_dist)

#-----------------------------

with st.expander("📈 Evolución Temporal"):
    fig_evo = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig_evo.add_trace(go.Scatter(x=bahia.groupby('fecha')['promedio'].mean().index,
                                 y=bahia.groupby('fecha')['promedio'].mean(),
                                 name="Bahía", line=dict(color='#FFAF00')), row=1, col=1)
    
    fig_evo.add_trace(go.Scatter(x=alamar.groupby('fecha')['promedio'].mean().index,
                                 y=alamar.groupby('fecha')['promedio'].mean(),
                                 name="Alamar", line=dict(color='#06D001')), row=2, col=1)
    
    fig_evo.update_layout(height=600, title_text="📈 Evolución Temporal Comparada", template="plotly_dark")
    st.plotly_chart(fig_evo, use_container_width=True)
