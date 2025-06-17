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
    st.markdown("---")
    
    plot_peak_noise(df_ubinombre)
    st.markdown("---")
    
    plot_min_noise_evolution(df_ubinombre)
    st.markdown("---")
    
    show_summary_metrics(df)
    st.markdown("---")
    
    plot_noise_limits(df)
    st.markdown("---")
    
    plot_trend_noise(df_ubinombre)
    st.markdown("---")
    
    plot_comparison_residencia_alamar(df)
    st.markdown("---")
    
    plot_weekly_trend(df_ubinombre)