import pandas as pd
import matplotlib.pyplot as plt
import json
import streamlit as st
import seaborn as sns
import time
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
df

mediciones = df.groupby("periodo")[["promedio", "maximo", "minimo", "peak"]].mean()
mediciones.plot(kind="bar", figsize=(10, 6))
plt.title("Decibeles por Periodo")
plt.xlabel("Periodo")
plt.ylabel("Decibeles (dB)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)  # Cuadrícula horizontal opcional
plt.tight_layout()
plt.show()



st.title("Mapa de Calor: Promedio de Decibeles por Horario y Ubicación")
df_filtrado = df[df["dia_semana"].isin(["Viernes", "Sabado"])]
heatmap_data = df_filtrado.pivot_table(
    index= "ubicacion",
    columns= "periodo",
    values= "promedio",
    aggfunc= "mean"
)

st.dataframe(heatmap_data)

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(
    heatmap_data,
    annot=True,             
    fmt=".1f",              
    cmap="YlOrRd",          
    linewidths=0.5,         
    ax=ax
)

plt.title("Promedio de Decibeles en la Residencia Estudiantil Bahía y Periodo (El Fin de Semana)", pad=20)
plt.xlabel("Periodo (Horario)")
plt.ylabel("Ubicación")
plt.xticks(rotation=45)    

st.pyplot(fig)

df_filtrado = df[df["dia_semana"].isin(["Lunes", "Miercoles"])]
heatmap_data = df_filtrado.pivot_table(
    index= "ubicacion",
    columns= "periodo",
    values= "promedio",
    aggfunc= "mean"
)

st.dataframe(heatmap_data)

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(
    heatmap_data,
    annot=True,             
    fmt=".1f",              
    cmap="YlOrRd",          
    linewidths=0.5,         
    ax=ax
)

plt.title("Promedio de Decibeles en la Residencia Estudiantil Bahía y Periodo (Entre Semana)", pad=20)
plt.xlabel("Periodo (Horario)")
plt.ylabel("Ubicación")
plt.xticks(rotation=45)    

st.pyplot(fig)


pico_maximo = df["peak"].max()  
registro_pico = df.loc[df["peak"].idxmax()]  
ubicacion = registro_pico["ubicacion"]
periodo = registro_pico["periodo"]
fecha = registro_pico["fecha"]

st.title("🚨 **Pico de Ruido Máximo Registrado**")

st.write("### 📌 **¿Sabías qué?**")
st.write(f"- **{pico_maximo} dB** es equivalente al ruido de una **sirena de bomberos** (110-120 dB) o un **concierto de rock** (115 dB).")
st.write("- Para contexto: una conversación normal ronda los **60 dB** y el tráfico pesado los **85 dB**.")

fig, ax = plt.subplots()
ejemplos = ["Sirena de Bomberos", "Tráfico", "Conversación"]
niveles = [pico_maximo, 85, 60]
colores = ["#CB0404", "#F4631E", "#FF9F00"]

bars = ax.bar(ejemplos, niveles, color=colores)
ax.bar_label(bars, labels=niveles, padding=3, fontsize=10) 

ax.bar(ejemplos, niveles, color=colores)
ax.set_ylabel("Decibeles (dB)", fontweight="bold")
ax.set_title("Comparación de los Diferentes Niveles", fontweight="bold")
plt.xticks(rotation=45)
st.pyplot(fig)



st.title("📈 Evolución Temporal del Ruido")

if 'df' not in globals():
    st.error("Error: No se encontró el DataFrame 'df'")
    st.stop()

required_columns = {'fecha', 'periodo', 'promedio'}
if not required_columns.issubset(df.columns):
    missing = required_columns - set(df.columns)
    st.error(f"Faltan columnas: {missing}")
    st.stop()

try:
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df.dropna(subset=['fecha', 'periodo', 'promedio'])
    
    umbral_peligroso = st.slider("Umbral peligroso (dB)", 70, 120, 85)
    velocidad = st.slider("Velocidad animación", 0.1, 2.0, 0.5)

    df_diario = df.groupby(['fecha', 'periodo'], observed=True)['promedio'].mean().unstack()
    if df_diario.empty:
        st.error("No hay datos válidos después del procesamiento")
        st.stop()

    df_diario = df_diario.sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    placeholder = st.empty()

    for i in range(1, len(df_diario)+1):
        with placeholder.container():
            ax.clear()
            temp_df = df_diario.iloc[:i]
            
            colors = plt.cm.tab10.colors
            for j, horario in enumerate(temp_df.columns):
                ax.plot(temp_df.index, temp_df[horario], 
                      color=colors[j % 10], label=horario, marker='o')
                
                mask = temp_df[horario] > umbral_peligroso
                ax.scatter(temp_df.index[mask], temp_df[horario][mask],
                          color='red', s=100, zorder=5)

            ax.axhline(umbral_peligroso, color='red', linestyle='--')
            ax.set_title(f"Evolución hasta {temp_df.index[-1].strftime('%d/%m/%Y')}")
            ax.set_ylabel("dB")
            ax.legend()
            plt.xticks(rotation=90)
            st.pyplot(fig)
            
            current_day = df_diario.iloc[i-1]
            alertas = current_day[current_day > umbral_peligroso]
            if not alertas.empty:
                st.warning(f"¡Alerta! Valores altos en: {', '.join(alertas.index)}")
            
            time.sleep(velocidad)

    st.dataframe(df_diario.style.apply(
        lambda x: ['background: #ffcccc' if v > umbral_peligroso else '' for v in x]
    ))

except Exception as e:
    st.error(f"Error inesperado: {str(e)}")
    st.stop()



