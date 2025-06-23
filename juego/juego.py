import streamlit as st
import pandas as pd
import json 
import random
from PIL import Image
import pydeck as pdk

# ----------------------

image = Image.open("./imagen/imagen1.gif")
st.image(image, caption="(●'◡'●)Creemos Conciencia")

# ----------------------

with open("./data/bahia.json", "r", encoding="utf-8") as f:
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

with open("./data/preguntas.json", "r", encoding="utf-8") as f:
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
with open("./data/ubicaciones_extra.json", "r", encoding="utf-8") as f:
    ubicaciones_extras = json.load(f)

ubicaciones_ext = []
for u in ubicaciones_extras:
    ubicaciones_ext.append(
        {
            "ubicacion": u["nombre"],
            "lat": u["coordenadas"]["lat"],
            "lon": u["coordenadas"]["lon"],
            "promedio": u["promedio"]
        }
    )

df_ubicaciones_extra = pd.DataFrame(ubicaciones_ext)

df_todas_ubicaciones = pd.concat([df_ubicaciones, df_ubicaciones_extra], ignore_index=True)

# ----------------------

if not st.session_state.inicio:
    st.markdown(""" ## 🕵️‍♂️ ¡Hola, Detective del Ruido!
🔊 ¿Escuchaste eso? No, no fue tu barriga.. ¡es la ciudad gritando!

🎧 Hoy vas a usar tus súper oídos para investigar distintos rincones de La Habana y detectar cuáles tienen mayor contaminación sonora.

📍 Sigue pistas, escucha sonidos reales y demuestra que ningún ruido se te escapa.

🏆 Gana puntos, responde preguntas y conviértete en Maestro en Bulla.

🔔 ¡El ruido no descansa.. y tú tampoco!
    """)
    audio = open("./musica/inicio.mp3", "rb")
    st.audio(audio.read(), format="audio/mp3")
    
    if st.button("🕵️ Comenzar la misión"):
        st.session_state["inicio"] = True
        st.rerun()

# ----------------------

else:
    st.markdown("## 🗺️ Mapa de detección sonora en La Habana")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_todas_ubicaciones,
        get_position='[lon, lat]',
        get_color='[200, 25, 0]',
        get_radius=150,
        pickable=True,
    )
    view_state = pdk.ViewState(
    latitude=df_todas_ubicaciones["lat"].mean(),
    longitude=df_todas_ubicaciones["lon"].mean(),
    zoom=11,
    pitch=0
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
    st.markdown("---")
    
#---------------------------

    if "seleccionadas" not in st.session_state:
        ubicaciones = df_todas_ubicaciones["ubicacion"].unique().tolist()
        n = min(5, len(ubicaciones))
        seleccionadas = random.sample(ubicaciones, n)

        promedios = {u: df_todas_ubicaciones[df_todas_ubicaciones["ubicacion"] == u]["promedio"].values[0] for u in seleccionadas}
        correcta = max(promedios, key=promedios.get)

        st.session_state.seleccionadas = seleccionadas
        st.session_state.promedios = promedios
        st.session_state.correcta = correcta
        st.session_state.respuesta_ruido = None

#---------------------------

    st.markdown("### 🔍 Selecciona la ubicación que crees que tiene más ruido")

    eleccion = st.radio(
        "¿Qué ubicación tiene más ruido?",
        st.session_state.seleccionadas,
        index=None,
        key="eleccion_ruido"
    )

    if st.button("✅ Comprobar respuesta") and eleccion:
        st.session_state.respuesta_ruido = eleccion

    if st.session_state.get("respuesta_ruido"):
        eleccion = st.session_state.respuesta_ruido
        correcta = st.session_state.correcta
        promedios = st.session_state.promedios

        if eleccion == correcta:
            st.success("¡Correcto! 🎉")
            if not st.session_state.get("puntaje_ruido_sumado"):
                st.session_state["puntaje"] += 20
                st.session_state["puntaje_ruido_sumado"] = True
        else:
            st.error(f"Incorrecto. La ubicación con más ruido era: **{correcta}**")

        st.info(f"🔊 Nivel de ruido en {correcta}: {promedios[correcta]:.2f} dB")

        st.markdown(f"### 🏆 Puntaje actual: {st.session_state['puntaje']}")
        st.divider()


# ----------------------

        image = Image.open("./imagen/imagen2.jpeg")
        st.image(image, caption="El grito no es solo de molestia, es una señal: la ciudad está demasiado ruidosa. ¿La estás escuchando?")

        st.subheader("🧠 Trivia educativa")

        if "pregunta_actual" not in st.session_state or st.session_state.get("respuesta_trivia") is not None:
            preguntas_disponibles = [p for p in preguntas if p["pregunta"] not in st.session_state.preguntas_usadas]

            if preguntas_disponibles:
                pregunta_actual = random.choice(preguntas_disponibles)
                st.session_state.pregunta_actual = pregunta_actual
                st.session_state.respuesta_trivia = None
                st.session_state.preguntas_usadas.append(pregunta_actual["pregunta"])
            else:
                st.session_state.pregunta_actual = None

        pregunta_actual = st.session_state.get("pregunta_actual")

        if pregunta_actual:
            st.markdown(f"**{pregunta_actual['pregunta']}**")
            opcion = st.radio(
                "Opciones:",
                pregunta_actual["opciones"],
                key=pregunta_actual["pregunta"],
                index=None  
            )

            if st.button("📚 Comprobar trivia") and opcion:
                st.session_state.respuesta_trivia = opcion
                if opcion == pregunta_actual["respuesta"]:
                    st.success("¡Correcto!")
                    st.session_state["puntaje"] += pregunta_actual["valor"]
                else:
                    st.warning("Incorrecto. Pista: " + pregunta_actual["pista"])

                if 'audio_reproducido' not in st.session_state:
                    st.audio(f"./musica/{pregunta_actual['audio']}")
                    st.session_state.audio_reproducido = True
                    st.stop() 
                else:
                    st.warning("🔇 Audio no disponible para esta pregunta.")
                    
    # ----------------------

        elif pregunta_actual is None:
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
                st.session_state.pop("pregunta_actual", None)
                st.session_state.pop("respuesta_trivia", None)
                st.rerun()
