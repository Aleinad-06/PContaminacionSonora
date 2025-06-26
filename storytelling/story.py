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



st.html("<h1 style= 'color: #E9A319; font-family: Times: text-agoin: center; font-size: 50px'>🌞 Bahía  vs. 🌙 Alamar: Dónde Reside el Ruido.❓ Será 🌞 o 🌙 </h1>")
st.html("""<h3>
        Durante semanas, estuve rodeada de ruido.
<br>
No era nuevo. Estaba ahí desde siempre.
<br>
Pero esta vez no lo ignoré.
<br>
Esta vez quise escucharlo de verdad.
<br>
Con la app en mano y curiosidad a tope, salí a buscarlo.
<br>
¿Dónde era más intenso? ¿Cuándo se hacía notar?
<br>
Y así comenzó esta historia.
<br>
Una historia donde el protagonista es invisible… pero imposible de callar.
<br><br>
    <span style= 'color: #00CAFF; font-family: Times  '> - 🏢 Residencia Bahía: Epicentro social con tráfico constante </span>
<br><br>
    <span style= 'color: #B0DB9C ; font-family: Times '> - 🌳 Residencia Alamar: Zona residencial alejada del bullicio </span>
<br><br>
➡️¿Quiénes son los protagonistas de la novela?
<br><br>
👣 Ven 🫴 conmigo y te enseño</h3>""")

st.html("<h2 style= 'color: #E9A319; font-family: Times: text-agoin: center; font-size: 45px'>📊 Hallazgos</h2>")

st.html("""<h3>
            ¿Cuándo hace más escándalo? – El momento del caos 
    <br><br>
    El día apenas empieza y ya el Ruido está en modo DJ.
    <br>
    En la Residencia Bahía, la mañana fue el horario más ruidoso.
    <br>
    Justo cuando uno solo quiere cinco minutos más de sueño…
    <br>
    los decibeles se disparan como si fuera carnaval.
    <br><br>
    Incluso el pico de ruido más alto registrado ocurrió en plena mañana.
    <br>
    No, no fue de noche.
    <br>
    Y no, no había fiesta.
    <br>
    Era la rutina diaria.
    <br><br>
    Así que si pensabas que estabas exagerando al quejarte… no. Tenías razón.
            </h3>""")
df["fecha"] = pd.to_datetime(df["fecha"])

fecha_inicio = pd.to_datetime("2025-05-02")
fecha_final = pd.to_datetime("2025-05-17")

df_filtrado = df[df["fecha"].between(fecha_inicio, fecha_final)]

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

st.divider()
        
#---------------------

st.html("""<h3>
🌐 Dos mundos sonoros
<br><br>
También medí en Alamar, para comparar.
<br> 
Y ahí me di cuenta de algo curioso:
<br> 
el ruido también tiene personalidad.
<br><br>
<span style='color: #00CAFF; font-family: Times'>🔊 En Bahía, el sonido es intenso, persistente, casi desafiante.</span>
<br> 
<span style='color: #B0DB9C; font-family: Times'>🔈 En Alamar, en cambio, el ambiente es más relajado.</span>
<br><br>
Sí, hay ruidos, pero parecen pedir permiso.
<br>
Nada que ver con la Bahía, donde el Ruido entra como si fuera su casa. 🏠💥
<br>
📉 Los números lo confirman: <strong>promedios más bajos, menos picos extremos</strong>,
<br> 
y hasta momentos en los que se podía respirar algo parecido al silencio. 😌
</h3>""")


bahia = df_filtrado[df_filtrado["ubicacion"] == "Residencia Estudiantil Bahia"].copy()
alamar = df_filtrado[df_filtrado["ubicacion"] == "Residencia Estudiantil Alamar"].copy()

def procesar_residencia(data):
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
    stats_bahia = bahia['promedio'].describe().rename('Bahía').agg(["mean", "min", "50%", "max"])
    stats_alamar = alamar['promedio'].describe().rename('Alamar').agg(["mean", "min", "50%", "max"])
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

st.html("""<h3>
📏 Las reglas que no se cumplen
<br><br>
Hay un límite saludable de ruido para vivir: 
<span style='color: #00CAFF; font-family: Times'>📉 55 decibelios según la OMS</span>.
<br>
<span style='color: red; font-family: Times'>🚨 Spoiler: no lo respetamos.</span>
<br>
Día tras día, medí niveles que superaban los 60,
<br>
y más de una vez… <span style='color: yellow; font-family: Times'>⚠️ se disparaban por encima de los 70.</span>
<br><br>
Niveles que no solo afectan el descanso 😴,
<br>
sino también la salud mental 🧠, la concentración 🎯 y el rendimiento académico 📚.
<br><br>
Y hasta ahora, lo dejábamos pasar como si no existiera. 🙈
</h3>""")


st.html("""<h3>
<span style='color: #E9A319; font-family: Times; font-size: 50px'>🧏 Escuchar también es actuar</span>
<br><br>

📊 Medirlo fue solo el primer paso.
<br>
Después vinieron los gráficos, el juego, la historia...
<br>
Todo para que el Ruido —ese que a veces se siente pero no se ve— tuviera por fin rostro, cifras y voz.
<br><br>

🎙️ Porque no se trata solo de "ruido molesto".
<br>
Estamos hablando de un enemigo cotidiano que afecta cómo dormimos, cómo pensamos, cómo vivimos.
<br><br>

👂 Yo aprendí a escucharlo de verdad, no solo a soportarlo.
<br>
Aprendí que el exceso de decibeles no solo perturba, también desgasta.
<br>
Y cuando el ruido se vuelve rutina, sus efectos se vuelven invisibles... pero permanentes.
<br><br>

😵‍💫 Ansiedad. 😓 Falta de concentración. 💤 Sueño interrumpido.
<br>
Y lo peor: normalizamos todo eso.
<br><br>

Pero cuando lo medimos, lo graficamos, lo comparamos…
<br>
dejó de ser una queja para convertirse en evidencia.
<br><br>

👩‍💻 Este proyecto es mi forma de hacer visible lo que muchos ya intuían.
<br>
Un intento de decir: “mira, no es solo percepción… está pasando y aquí están los datos que lo prueban”.
<br><br>

🌍 No es un lujo hablar de contaminación sonora. Es una necesidad.
<br>
No necesitamos vivir en completo silencio, pero sí con respeto al descanso de los demás.
<br>
Con conciencia de que cada bocina, cada motor, cada grito... suma.
<br><br>

Y si llegaste hasta aquí, ya diste el primer paso. 🚶‍♀️
<br>
Ahora, te invito a dar el siguiente: 
escuchar con más intención, actuar con más empatía, y hablar del ruido sin miedo.
<br><br>

Porque el Ruido no se detiene solo...<br>
pero sí podemos aprender a bajarle el volumen.
<br><br>

🎧 Gracias por escuchar. Literalmente.
</h3>""")





