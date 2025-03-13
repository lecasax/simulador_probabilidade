import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

st.set_page_config(layout="wide")  # Ajusta toda a página para modo wide

def probabilidade_conjunta(n, m, k):
    if k > n:
        return 0  
    prob = 1.0
    for i in range(k - 1):
        prob *= (n - m - i) / (n - i)
    prob *= m / (n - (k - 1))
    return prob

def prob_cond_k(m, n, k):
    return min(1, m / (n - (k - 1)))

def probabilidade_sucesso_ate_k(n, m, k, s):
    if s > m or s > k:
        return 0  
    prob = 0.0
    for i in range(s, min(m, k) + 1):
        prob_i = (math.comb(m, i) * math.comb(n - m, k - i)) / math.comb(n, k)
        prob += prob_i
    return prob

def probabilidade_zero_sucesso_ate_k(n, m, k):
    if k > n:
        return 0
    prob = (math.comb(n - m, k)) / math.comb(n, k)
    return prob

st.title("Calculadora de Probabilidades Condicionais e Conjuntas")

# Criando um layout menor para os inputs e mantendo o gráfico wide
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    n = col1.number_input("Tamanho do conjunto total (n):", min_value=1, value=650)
    m = col2.number_input("Tamanho do subconjunto de interesse (m):", min_value=1, value=15)
    k = col3.number_input("Número de rodadas (k):", min_value=1, max_value=n, value=650)
    
    #col1.caption("Tamanho do conjunto total (n)")
    #col2.caption("Tamanho do subconjunto de interesse (m)")
    #col3.caption("Número de rodadas (k)")

if st.button("Calcular e Gerar Gráficos"):
    k_values_discretized = np.arange(1, k + 1, 5)
    if k not in k_values_discretized:
        k_values_discretized = np.append(k_values_discretized, k)  # Garante que k esteja presente no eixo X

    prob_cond_values_discretized = [prob_cond_k(m, n, i) for i in k_values_discretized]
    prob_zero_values_discretized = [probabilidade_zero_sucesso_ate_k(n, m, i) for i in k_values_discretized]
    prob_s_values_discretized = {s: [probabilidade_sucesso_ate_k(n, m, i, s) for i in k_values_discretized] for s in range(1, m + 1)}
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=k_values_discretized, y=prob_cond_values_discretized, mode='lines+markers', name="P(Exata da rodada k)"))
    fig.add_trace(go.Scatter(x=k_values_discretized, y=prob_zero_values_discretized, mode='lines+markers', name="P(0 sucessos até a rodada k)", line=dict(dash='dot'), visible="legendonly"))
    
    for s in range(1, min(m, k) + 1):
        fig.add_trace(go.Scatter(x=k_values_discretized, y=prob_s_values_discretized[s], mode='lines+markers', name=f"P({s} sucessos até a rodada k)"))
    
    fig.update_layout(
        title=f"Probabilidades Condicionais para n={n}, m={m}",
        xaxis_title="Número da rodada",
        yaxis_title="Probabilidade",
        legend_title="Legenda",
        template="plotly_white",
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black', range=[-5, k+5]),
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black', range=[-0.05, 1.05])
    )
    
    # Garantindo que o gráfico fique realmente wide
    st.plotly_chart(fig, use_container_width=True)
