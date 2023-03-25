import pandas as pd 
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
import datetime


# Datos de la página

st.set_page_config(page_title="Calculadora Sherpa", layout="wide")
st.header("Calculadora Estrategias Sherpa")

# Obtener Base de Datos de rendimientos Sherpa y Benchmarks 

base_rend = (pd.read_excel("Base_1.xlsx"))
base_bmks = (pd.read_excel("Base_1.xlsx", sheet_name="BMKS_MXN"))
base_rend = base_rend.set_index("FECHA")

# Crear una tabla con las fechas para mostrar en formato dd/mm/aaaa

t_fechas = pd.DataFrame([base_rend.index, base_rend.index.strftime("%d/%m/%Y")]).T
t_fechas.index = t_fechas[1]


# Opciones de la barra lateral 

tipo_calculadora = st.sidebar.selectbox("Tipo de Calculadora", ["Personalizada", "Affluent", "Robo"])
num_estrategias = st.sidebar.radio("Número de Estrategias", [1,2,3])

# Selección de Fechas (Inicial, Final, Determinado o Personalizado)

periodo = st.sidebar.selectbox("Periodo", ["3 Años", "5 Años", "Personalizado"])


f_ini = []
f_imi = []

if periodo == "Personalizado":

    f_inicial_1 = st.sidebar.selectbox("Fecha Incial", base_rend.index.strftime("%d/%m/%Y"))
    f_final_1 = st.sidebar.selectbox("Fecha Final", base_rend.index.strftime("%d/%m/%Y"))
    f_ini = t_fechas.loc[f_inicial_1][0]
    f_fin = t_fechas.loc[f_final_1][0]


if periodo == "3 Años":

    f_ini = t_fechas[0].iloc[-37]
    f_fin = t_fechas[0].iloc[-1]
    
if periodo == "5 Años":

    f_ini = t_fechas[0].iloc[-61]
    f_fin = t_fechas[0].iloc[-1]

else:

    pass


# Datos Inciales del Cliente y Banquero


st.subheader("Datos del Cliente")
col1, col2 = st.columns(2)

with col1:

    nombre = st.text_input("Nombre del Cliente")
    perfil = st.selectbox("Perfil del Cliente", ["Conservador", "Moderado", "Crecimiento"])


# Seleccionar las ponderaciones por estrategia 

st.header("Ponderaciones Portafolio")

col1, col2, col3, col4 = st.columns(4)

with col1: 
    st.subheader("Deuda Local")
    DLCP = st.number_input("DL Corto Plazo", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    DLMP = st.number_input("DL Mediano Plazo", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    DLLP = st.number_input("DL Largo Plazo", min_value=float(0.00), max_value=float(1.00), step=float(0.01))


with col2: 
    st.subheader("Deuda Global")
    DGCP = st.number_input("DG Corto Plazo", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    DGLP = st.number_input("DG Largo Plazo", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
        
with col3:
    st.subheader("Capitales Local")
    CLB = st.number_input("Sherpa Beta", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    CLM = st.number_input("Sherpa Mexopp", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    SAURO = st.number_input("Sauro", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    QVG = st.number_input("QVGMEX", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    
with col4:
    st.subheader("Capitales Global")
    CGC = st.number_input("Sherpa Global", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    CGIGP = st.number_input("Sherpa IGP", min_value=float(0.00), max_value=float(1.00), step=float(0.01))
    CGOX = st.number_input("Sherpa OX", min_value=float(0.00), max_value=float(1.00), step=float(0.01))



   
# Ponderaciones y tabla de rendimientos

w_port = np.array([DLCP, DLMP, DLLP, DGCP, DGLP, CLB, SAURO, CLM, QVG, CGC, CGOX, CGIGP])

if sum(w_port) != 1:

    st.error("Las ponderaciones no suman 100%", icon="🚨")

else:
    pass


value_1 = w_port > 0
w_port_f = w_port[w_port > 0]


if f_ini == base_rend.index[0]:

    base_rend.iloc[0] = 0

else:

    pass





base_rend_fechas = base_rend.loc[f_ini:f_fin].loc[::, value_1].dropna()
base_rend_fechas.iloc[0] = 0

f_value = base_rend_fechas.index[0]

if f_ini < f_value:

    st.error("Fecha Inicial Incorrecta, se utilizará ____")

else:
    pass


pond = base_rend_fechas * w_port_f
pond["PORT_1"] = pond.sum(axis=1)
a = ((1 + pond["PORT_1"]).cumprod()) -1



labels = ["DLCP", "DLMP","DLLP","DGCP", "DGLP", "CLB", "SAURO", "CLM", "QVG", "CGC", "CGOX", "CGIGP"]
pc = pd.DataFrame(data=([labels, w_port]))
pc = pc.T
pc.columns = ["Estrategia", "Inv"]
pc = pc.loc[(pc !=0).all(axis=1), :]



colors = ["#113365", "#B37700", "#B39C0C", "#B36630", "#3C5780"]
pie_chart = px.pie(pc, names="Estrategia", values="Inv", hole=0.4, color="Estrategia", color_discrete_map=dict(zip(pc["Estrategia"], colors)))


# Gráfica de Línea 


l_chart = px.area(a)
l_chart.update_traces(line_color="#113365")
l_chart.update_layout(yaxis_tickformat = '0.00%', yaxis_title="Rendimiento", xaxis_title="Fecha")



# Métricas del portafolio

t = a.index[-1] - a.index[0]
pos = (pond["PORT_1"] > 0).value_counts()[1]
neg = (pond["PORT_1"] > 0).value_counts()[0] - 1

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric(label="Rendimiento Total", value="{:.2%}".format(a.iloc[-1]))
col2.metric(label="Anualizado", value="{:.2%}".format(((1 + a.iloc[-1]) ** (365 / t.days)) -1 ))
col3.metric(label="Volatilidad", value="{:.2%}".format(pond["PORT_1"].std() * np.sqrt(12)))
col4.metric(label="Número de meses", value=pos+neg)
col5.metric(label="Meses Positivos", value=pos)
col6.metric(label="Meses Negativos", value=neg)


col1, col2 = st.columns(2)

with col1: 

    st.header("📈 Simulación Histórica del Portafolio 📈")
    st.plotly_chart(l_chart)

with col2: 
    
    st.header("Distribución")
    st.plotly_chart(pie_chart)
