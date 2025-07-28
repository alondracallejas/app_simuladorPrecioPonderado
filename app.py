import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Simulador de Precios Ponderados", layout="centered")

st.title("📊 Simulador de Precio Promedio Ponderado")

st.markdown("""
Esta herramienta te permite simular cómo se vería tu **precio promedio ponderado mensual** al negociar un nuevo precio con un cliente estratégico.
""")

# Paso 2: Ingreso de datos
st.header("1. Ingreso de Datos de Clientes")

num_clientes = st.number_input("Número de clientes", min_value=1, max_value=50, value=5)

default_data = {
    "Cliente": [f"Cliente {i+1}" for i in range(num_clientes)],
    "Precio por volumen": [1000 for _ in range(num_clientes)],
    "Volumen": [10 for _ in range(num_clientes)]
}
df = pd.DataFrame(default_data)

edited_df = st.data_editor(df, num_rows="fixed", use_container_width=True)

def calcular_ppp(df):
    total_volumen = df["Volumen"].sum()
    if total_volumen == 0:
        return 0
    return (df["Precio por volumen"] * df["Volumen"]).sum() / total_volumen

ppp_actual = calcular_ppp(edited_df)

st.success(f"💰 Precio promedio ponderado actual: **${ppp_actual:,.2f}**")

# 3. Matriz Rentabilidad vs Participación
st.header("2. Matriz de Participación y Precio")

edited_df["Participación (%)"] = edited_df["Volumen"] / edited_df["Volumen"].sum() * 100

fig = px.scatter(
    edited_df,
    x="Participación (%)",
    y="Precio por volumen",
    size="Volumen",
    color="Cliente",
    title="Clientes: Participación en Volumen vs Precio",
    labels={"Participación (%)": "% Volumen", "Precio por volumen": "Precio ($/volumen)"},
    size_max=40,
    hover_data=["Volumen"]
)
st.plotly_chart(fig, use_container_width=True)


st.header("3. Simulación con Cliente Estratégico")

cliente_objetivo = st.selectbox("Selecciona un cliente para simular nuevo precio", edited_df["Cliente"])
nuevo_precio = st.number_input("Nuevo precio simulado ($/volumen)", min_value=0.0, value=900.0, step=10.0)

sim_df = edited_df.copy()
sim_df.loc[sim_df["Cliente"] == cliente_objetivo, "Precio por volumen"] = nuevo_precio

ppp_simulado = calcular_ppp(sim_df)

st.info(f"📉 Nuevo precio promedio ponderado simulado: **${ppp_simulado:,.2f}**")

diff = ppp_actual - ppp_simulado
if diff > 0:
    st.warning(f"¡Reducirías tu promedio en ${diff:,.2f} por volumen!")
elif diff < 0:
    st.success(f"¡Este cambio aumentaría tu precio promedio en ${-diff:,.2f} por volumen!")
else:
    st.info("Este cambio no afecta el precio promedio.")

# Gráfica mejorada
st.header("📊 Comparación de Precios por Cliente y PPP")

fig = go.Figure()

# Barras por cliente con precios originales
fig.add_trace(go.Bar(
    x=edited_df["Cliente"],
    y=edited_df["Precio por volumen"],
    name="Precio Original",
    marker_color='rgba(0, 123, 255, 0.7)',  # Azul transparente
    text=[f"${p:,.2f}" for p in edited_df["Precio por volumen"]],
    textposition='auto',
    hovertemplate='%{x}<br>Precio Original: %{y:$,.2f}<extra></extra>',
))

# Barras por cliente con precios simulados
fig.add_trace(go.Bar(
    x=sim_df["Cliente"],
    y=sim_df["Precio por volumen"],
    name="Precio Simulado",
    marker_color='rgba(255, 165, 0, 0.7)',  # Naranja transparente
    text=[f"${p:,.2f}" for p in sim_df["Precio por volumen"]],
    textposition='auto',
    hovertemplate='%{x}<br>Precio Simulado: %{y:$,.2f}<extra></extra>',
))

# Líneas horizontales PPP actual y simulado
fig.add_trace(go.Scatter(
    x=edited_df["Cliente"],
    y=[ppp_actual]*len(edited_df),
    mode='lines+markers',
    name="PPP Actual",
    line=dict(color='green', width=3, dash='dash'),
    marker=dict(size=8),
    hovertemplate='PPP Actual: %{y:$,.2f}<extra></extra>',
))

fig.add_trace(go.Scatter(
    x=edited_df["Cliente"],
    y=[ppp_simulado]*len(edited_df),
    mode='lines+markers',
    name="PPP Simulado",
    line=dict(color='red', width=3, dash='dash'),
    marker=dict(size=8),
    hovertemplate='PPP Simulado: %{y:$,.2f}<extra></extra>',
))

fig.update_layout(
    barmode='group',
    yaxis_title='Precio ($/volumen)',
    xaxis_title='Cliente',
    legend_title_text='Leyenda',
    plot_bgcolor='white',
    yaxis=dict(
        gridcolor='lightgray',
        zeroline=True,
        zerolinecolor='gray',
        zerolinewidth=1
    ),
    xaxis=dict(tickangle=-45),
    margin=dict(t=40, b=100),
    height=550,
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("🔍 Ver detalle de datos originales y simulados"):
    st.subheader("Datos originales")
    st.dataframe(edited_df, use_container_width=True)
    st.subheader("Datos simulados")
    st.dataframe(sim_df, use_container_width=True)
