import streamlit as st
import pandas as pd
import json 
import random
from PIL import Image
import pydeck as pdk
import os

# ----------------------

st.set_page_config(page_title="¡Shhh... Que viene el Ruídologo!", layout="wide")
image = Image.open("../imagen/imagen1.gif")
st.image(image, caption="(●'◡'●)Creemos Conciencia")

# ----------------------

with open("../jsons/data.json", "r", encoding="utf-8") as f:
    inf = json.load(f)

data = []
for i in inf:   
    fecha = i["tiempo"]["fecha"]
    dia_semana = i["tiempo"]["dia_semana"]
    nombre_ubicacion = i["ubicacion"]["nombre"]
    coordenadas = i["ubicacion"]["coordenadas"]
    
    for hora in i["horarios"]:
        periodo = hora["periodo"]
        mediciones = hora["mediciones"]
        data.append({
            "fecha": fecha,
            "dia_semana": dia_semana,
            "ubicacion": nombre_ubicacion,
            "coordenadas": coordenadas,
            "periodo": periodo,
            "mediciones": mediciones 
        }) 

df = pd.DataFrame(data)

ubicaciones = []
for name in df["ubicacion"].unique():
    subdf = df[df["ubicacion"] == name]
    valores = [d["promedio"] for d in subdf["mediciones"] if isinstance(d, dict) and "promedio" in d]
    promedio = sum(valores) / len(valores) if valores else 0
    coordenadas = subdf.iloc[0]["coordenadas"]
    ubicaciones.append({
        "ubicacion": name,
        "lat": coordenadas["lat"],
        "lon": coordenadas["lon"],
        "promedio": promedio
    })

df_ubicaciones = pd.DataFrame(ubicaciones)

# ----------------------

with open("../jsons/preguntas.json", "r", encoding="utf-8") as f:
    preguntas_data = json.load(f)

preguntas = []
for p in preguntas_data:
    preguntas.append({
        "pregunta": p["pregunta"],    
        "opciones": p["opciones"],
        "respuesta": p["respuesta"],
        "pista": p["pista"],
        "audio": p["audio"],
        "valor": p.get("valor", 10)
    })

# ----------------------

if "puntaje" not in st.session_state:
    st.session_state["puntaje"] = 0
if "inicio" not in st.session_state:
    st.session_state["inicio"] = False
if "preguntas_usadas" not in st.session_state:
    st.session_state["preguntas_usadas"] = []

# ----------------------

if not st.session_state.inicio:
    st.markdown(""" ## 🕵️‍♂️ ¡Hola, Detective del Ruido!
🔊 ¿Escuchaste eso? No, no fue tu barriga... ¡es la ciudad gritando!

🎧 Hoy vas a usar tus súper oídos para investigar distintos rincones de La Habana y detectar cuáles tienen mayor contaminación sonora.

📍 Sigue pistas, escucha sonidos reales y demuestra que ningún ruido se te escapa.

🏆 Gana puntos, responde preguntas y conviértete en Maestro en Bulla.

🔔 ¡El ruido no descansa... y tú tampoco!
    """)
    audio = open("../musica/audio1.mp3", "rb")
    st.audio(audio.read(), format="audio/mp3")
    
    if st.button("🕵️ Comenzar la misión"):
        st.session_state["inicio"] = True
        st.rerun()

# ----------------------

else:
    st.markdown("## 🗺️ Mapa de detección sonora en La Habana")

    layer = pdk.Layer(
        "ScatterplotLayer",
        df_ubicaciones,
        opacity=0.8,
        get_position='[lon, lat]',
        get_radius=100,
        get_fill_color=[220, 139, 224],
        tooltip="ubicacion",
    )
    view_state = pdk.ViewState(
        latitude=23.1,
        longitude=-82.38,
        zoom=11
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
    
# ----------------------

st.markdown("---")
st.subheader("🎧 ¿Qué lugar es el más ruidoso?")

ubicaciones_unicas = df["ubicacion"].unique().tolist()
n = min(4, len(ubicaciones_unicas))  # asegura que no pidas más de los que hay
seleccionadas = random.sample(ubicaciones_unicas, n)
promedios = {u: df_ubicaciones[df_ubicaciones["ubicacion"] == u]["promedio"].values[0] for u in seleccionadas}
correcta = max(promedios, key=promedios.get)

df_ubicaciones["is_correct"] = df_ubicaciones["ubicacion"] == correcta

layer = pdk.Layer(
    "ScatterplotLayer",
    df_ubicaciones,
    pickable=True,
    opacity=0.9,
    get_position='[lon, lat]',
    get_radius='promedio * 20',
    get_fill_color="""
        (d.is_correct) ? [255, 0, 0] : [30, 144, 255]
    """,  
    tooltip=True,
)

view_state = pdk.ViewState(
    latitude=23.1,
    longitude=-82.38,
    zoom=13,
    pitch=0,
)

# ----------------------

eleccion = st.radio("¿Qué ubicación tiene más ruido?", seleccionadas)

if st.button("✅ Comprobar respuesta"):
    if eleccion == correcta:
        st.success("¡Correcto! 🎉")
        st.session_state["puntaje"] += 20
    else:
        st.error(f"Incorrecto. Era: {correcta}")
    st.info(f"Nivel de ruido en {correcta}: {promedios[correcta]:.2f} dB")

    # ---------------------- 
    
    audio_nombre = None
    for p in preguntas:
        if p["respuesta"] == correcta:
            audio_nombre = p["audio"].strip()
            print(audio_nombre)
            break

        if audio_nombre:
            ruta_audio = f"../musica/{audio_nombre}"
            print(audio_nombre)
            if st.button("🎵 Reproducir ambiente sonoro"):
                try:
                    with open(ruta_audio, "rb") as audio_r:
                        st.audio(audio_r.read(), format="audio/mp3")
                except FileNotFoundError:
                    st.warning(f"No se encontró el archivo de audio: {ruta_audio}")
        else:
            st.warning("No se encontró el nombre del archivo de audio para esta ubicación.")
        
    
        st.markdown(f"### 🏆 Puntaje actual: {st.session_state['puntaje']}")
        st.markdown("---")
        st.subheader("🧠 Trivia educativa")

        st.session_state.setdefault("siguiente_pregunta", True)
        st.session_state.setdefault("preguntas_usadas", [])
        st.session_state.setdefault("puntaje", 0)
        st.session_state.setdefault("pregunta_actual", None)

# ----------------------
    
        p = st.session_state.pregunta_actual

        if p:
            st.markdown(f"**{p['pregunta']}**")
            key_radio = f"radio_{hash(p['pregunta'])}"
            opcion = st.radio("pciones:", p["opciones"], key=key_radio)
            if st.button("📚 Comprobar trivia") and p["pregunta"] not in st.session_state.preguntas_usadas:
                if opcion == p["respuesta"]:
                    st.success("¡Correcto!")
                    st.session_state.puntaje += p["valor"]
                else:
                    st.warning("Incorrecto. Pista: " + p["pista"])
                                                                    
                    st.session_state.preguntas_usadas.append(p["pregunta"])
                    st.session_state.siguiente_pregunta = True

            if st.session_state.siguiente_pregunta:
                if st.button("▶️ Siguiente pregunta"):
                    preguntas_disponibles = [p for p in preguntas if p["pregunta"] not in st.session_state.preguntas_usadas]
                    if preguntas_disponibles:
                        st.session_state.pregunta_actual = random.choice(preguntas_disponibles)
                        st.session_state.siguiente_pregunta = False
                    else:
                        st.session_state.juego_terminado = True
                        st.session_state.siguiente_pregunta = False

            if st.session_state.get("juego_terminado", False):
                st.subheader("🎉 ¡Juego finalizado!")
                st.markdown(f"### Tu puntaje final es: **{st.session_state['puntaje']} puntos**")

                if st.session_state.puntaje >= 100:
                    st.success("🥳 ¡Eres un maestro del silencio!")
                elif 80 <= st.session_state.puntaje < 100:
                    st.info("¡Muy bien! Eres casi un experto del ruido.")
                elif 60 <= st.session_state.puntaje < 80:
                    st.warning("Estás en camino, pero necesitas afinar tus oídos.")
                else:
                    st.error("📉 Suspenso… El ruido te ganó esta vez. ¡Intenta otra vez!")

                if st.button("🔁 Reiniciar juego"):
                    st.session_state["puntaje"] = 0
                    st.session_state["preguntas_usadas"] = []
                    st.session_state["inicio"] = False
                    st.session_state["juego_terminado"] = False
                    st.rerun()
