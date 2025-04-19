import math
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("Simulador de probabilidades de carta de consórcio")


def probabilidade_sucesso_ate_k(n, m, k, s):
    if s > m or s > k or k > n:
        return 0.0
    prob = 0.0
    for i in range(s, min(m, k) + 1):
        prob_i = (math.comb(m, i) * math.comb(n - m, k - i)) / math.comb(n, k)
        prob += prob_i
    return prob


def probabilidade_sucesso_em_k(n, m, k, s):
    return (math.comb(m, s) * math.comb(n - m, k - s)) / math.comb(n, k)


def curva_com_ajuste_propagado(n, m, s, k_max, rodadas_removidas):
    curva = []
    remocoes_acumuladas = 0
    delta_prob = 0
    for k in range(1, k_max + 1):
        if k in rodadas_removidas:
            curva.append(curva[-1] if curva else 0.0)
            prob_i = probabilidade_sucesso_ate_k(n, m, k, s)
            prob_j = probabilidade_sucesso_ate_k(n, m, k - 1, s)
            delta_prob += prob_i - prob_j
        else:
            prob = probabilidade_sucesso_ate_k(n, m, k, s)
            curva.append(prob - delta_prob)
    return curva


def cria_rodadas_de_remocao(cont_por_sorteio, cont_por_lance, tamanho_do_grupo):
    rodadas_removidas = []
    count_k = 0
    while count_k <= tamanho_do_grupo:
        for k in range(cont_por_sorteio):
            count_k += 1
        for j in range(cont_por_lance):
            count_k += 1
            if count_k <= tamanho_do_grupo:
                rodadas_removidas.append(count_k)
    return rodadas_removidas

# Inputs em uma única linha responsiva (wide)
with st.container():
    col1, col2, col3, col4, col5 = st.columns([1.2, 1.8, 1.3, 1.3, 1.5])

    tamanho_grupo = col1.number_input("Tamanho do grupo:", min_value=1, value=650)
    numero_cartas_adquiridas = col2.number_input("Cartas adquiridas no consórcio:", min_value=1,
                                                 max_value=tamanho_grupo, value=5)
    cartas_por_sorteio = col3.number_input("Cartas por sorteio:", min_value=1, max_value=tamanho_grupo, value=1)
    cartas_por_lance = col4.number_input("Cartas por lance:", min_value=1, max_value=tamanho_grupo, value=1)
    numero_de_sucessos = col5.number_input("Sucessos até a rodada k:", min_value=1, max_value=numero_cartas_adquiridas,
                                           value=1)
# Botão e gráfico
if st.button("Gerar Gráficos"):
    cartas_por_mes = cartas_por_sorteio + cartas_por_lance
    n_meses = math.ceil(tamanho_grupo / cartas_por_mes)

    rodadas_removidas = cria_rodadas_de_remocao(cartas_por_sorteio, cartas_por_lance, tamanho_grupo)
    rodada_por_mes = [(i + 1) * cartas_por_mes for i in range(n_meses)]
    rodada_por_mes = [min(r, tamanho_grupo) for r in rodada_por_mes]

    curva_original = [probabilidade_sucesso_ate_k(tamanho_grupo, numero_cartas_adquiridas, k, numero_de_sucessos) * 100 for k in rodada_por_mes]
    curva_ajustada = curva_com_ajuste_propagado(tamanho_grupo, numero_cartas_adquiridas, numero_de_sucessos, tamanho_grupo, rodadas_removidas)
    curva_ajustada_por_mes = [curva_ajustada[k - 1] * 100 for k in rodada_por_mes]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(1, n_meses + 1)), y=curva_original, mode='lines+markers', name="Original"))
    fig.add_trace(go.Scatter(x=list(range(1, n_meses + 1)), y=curva_ajustada_por_mes, mode='lines+markers', name="Com remoções propagadas", line=dict(dash='dot')))

    fig.update_layout(
        title="Curva de probabilidade ideal e com remoções propagadas",
        xaxis_title="Mês",
        yaxis_title="Probabilidade (%)",
        legend_title="Legenda",
        template="plotly_white",
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black', range=[0, n_meses + 1]),
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black', range=[-5, 105]),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"Total de meses estimado: **{n_meses}**")
