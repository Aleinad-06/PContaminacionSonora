import pandas as pd
import streamlit as st
from biblioteca import *

rjson = "./data/data.json"
df = load_data(rjson)

show_main_header()

date = st.date_input("""Selecciona el día para explorar cómo se comportó el ruido    
                     ***Del 23 abr al 6 jun***""",
                     value=pd.to_datetime("2025-05-23"))

plot_daily_noise(df, date)

st.html("<h2 style='color: #FF7601'>⬇️Y porque no ver algo mas interesante⬇️</h2>")
mostrar_analisis = st.button("Veamos los Análisis😲")

if mostrar_analisis:
    map_data = df.to_dict('records')
    
    create_map(map_data)

    st.markdown("---")
    
    df_ubinombre = df[df["ubicacion"] == "Residencia Estudiantil Bahia"]
    
    plot_max_noise_evolution(df_ubinombre)
    st.markdown("""Durante el periodo observado, se evidencian variaciones notables en los niveles máximos de ruido según el momento del día.
                    
🔵 La tarde domina con los picos más constantes y elevados, lo que sugiere una actividad intensa en ese horario.

🔴 La noche presenta algunos picos aislados, probablemente asociados a eventos puntuales o comportamientos anómalos.

🟠 La mañana muestra fluctuaciones irregulares, aunque generalmente por debajo de los niveles de la tarde.

Este comportamiento indica que el ruido ambiental varía significativamente según el período del día,
con la tarde como el tramo más ruidoso de forma sostenida.

🎯 Objetivo: Visualizar cómo varían los niveles máximos de decibelios por período del día y
detectar cuál de ellos tiende a registrar los valores más altos de forma sistemática.""")
    
    st.markdown("---")
    
    plot_peak_noise(df_ubinombre)
    
    st.markdown("""Los valores más altos de decibelios (picos) varían diariamente, con algunas fechas destacando por registrar niveles extremos.

💥 La tarde nuevamente sobresale con varios picos por encima de los 100 dB, lo cual sugiere eventos anómalos o momentos de alta actividad.

🌙 La noche y la mañana presentan también algunos valores elevados, lo que refuerza la idea de que los picos no siempre ocurren en horarios previsibles.

📌 Este análisis ayuda a detectar eventos atípicos o peligrosos para la salud auditiva, incluso si solo duran unos segundos.

🎯 Objetivo: Que el usuario pueda observar con más detalle el comportamiento de los picos sonoros por día, 
reconociendo cuándo ocurren situaciones inusuales y entendiendo mejor la dinámica real del ruido en su entorno.""")
    
    st.markdown("---")
    
    plot_min_noise_evolution(df_ubinombre)
    st.markdown("""Los niveles mínimos de decibeles se mantienen elevados a lo largo del periodo analizado,
                sin registrar caídas notables que indiquen momentos de verdadero silencio.
                
🔵 En la mañana se observan más fluctuaciones, destacando una leve baja el 23 de mayo (42 dB), posiblemente reflejando un instante de menor actividad.

🟣 La noche, sorprendentemente, no es la más silenciosa, manteniéndose cerca de los 50 dB de forma constante.

🟡 La tarde varía más, pero tampoco desciende a niveles bajos.

En resumen, el gráfico evidencia que el ruido es constante y persistente durante todos los períodos del día.

🎯 Objetivo: Permitir al usuario identificar si existen momentos de verdadero silencio durante el día y
comprender la persistencia del ruido ambiente, incluso en horarios tradicionalmente más tranquilos.""")
    
    st.markdown("---")
    
    show_summary_metrics(df)
    st.markdown("---")
    
    plot_noise_limits(df)
    
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
    
    plot_trend_noise(df_ubinombre)
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
