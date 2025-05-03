import math
import streamlit as st
import plotly.graph_objects as go

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


st.title("Modalidades de consórico")

# Lista de opções de layout
opcoes_layout = ["Modalidade A", "Modalidade B", "Modalidade C"]

# Selectbox para escolher o layout
layout_selecionado = st.selectbox("Escolha sua modalidade de consóricio:", opcoes_layout)

st.markdown("---")

# Exibição dos campos com base na seleção
if layout_selecionado == "Modalidade A":
    st.subheader("Sorteio + Lance Livre")
    # nome = st.text_input("Nome:")
    # idade = st.number_input("Idade:", min_value=0, max_value=120, step=1)
    # st.write(f"Nome: {nome}, Idade: {idade}")
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.2])

        tamanho_grupo = col1.number_input("Grupo:", min_value=1, value=650)
        numero_cartas_adquiridas = col2.number_input("Cartas:", min_value=1,
                                                     max_value=tamanho_grupo, value=5)
        sorteio = col3.number_input("Sorteio:", min_value=1, max_value=tamanho_grupo, value=1)
        lance_livre = col4.number_input("Lance Livre:", min_value=1, max_value=tamanho_grupo, value=1)
        numero_de_sucessos = col5.number_input("Sucessos até k:", min_value=1,
                                               max_value=numero_cartas_adquiridas,
                                               value=1)

    # Botão e gráfico
    if st.button("Gerar Gráficos"):
        cartas_por_mes = sorteio + lance_livre
        n_meses = math.ceil(tamanho_grupo / cartas_por_mes)

        rodadas_removidas = cria_rodadas_de_remocao(sorteio, lance_livre, tamanho_grupo)
        rodada_por_mes = [(i + 1) * cartas_por_mes for i in range(n_meses)]
        rodada_por_mes = [min(r, tamanho_grupo) for r in rodada_por_mes]

        curva_original = [
            probabilidade_sucesso_ate_k(tamanho_grupo, numero_cartas_adquiridas, k, numero_de_sucessos) * 100 for k in
            rodada_por_mes]
        curva_ajustada = curva_com_ajuste_propagado(tamanho_grupo, numero_cartas_adquiridas, numero_de_sucessos,
                                                    tamanho_grupo, rodadas_removidas)
        curva_ajustada_por_mes = [curva_ajustada[k - 1] * 100 for k in rodada_por_mes]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=list(range(1, n_meses + 1)), y=curva_original, mode='lines+markers', name="Original"))
        fig.add_trace(go.Scatter(x=list(range(1, n_meses + 1)), y=curva_ajustada_por_mes, mode='lines+markers',
                                 name="Com remoções propagadas", line=dict(dash='dot')))

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

        # Criando o gráfico de pizza
        fig_pizza = go.Figure(data=[go.Pie(
            labels=['Sorteio', 'Lances Livres'],
            values=[n_meses * sorteio, n_meses * lance_livre],
            hole=0.4,  # Para criar um gráfico de rosca; remova ou ajuste para um gráfico de pizza tradicional
            marker=dict(colors=['#1f77b4', '#ff7f0e']),  # Cores personalizadas
            hoverinfo='label+percent',
            textinfo='value'
        )])

        # Configurando o layout do gráfico
        fig_pizza.update_layout(
            title_text='Distribuição de Contemplações',
            annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )

        fig_pizza.update_traces(
            textinfo='percent',
            hovertemplate='%{label}: %{value}<extra></extra>'
        )

        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig_pizza, use_container_width=True)


        st.markdown(f"Total de meses estimado: **{n_meses}**")



elif layout_selecionado == "Modalidade B":
    st.subheader("Sorteio + Lance Livre + Lance Fidel 6m + Lance Fidel 12m + Lance Fixo 30%")
    # nome = st.text_input("Nome:")
    # idade = st.number_input("Idade:", min_value=0, max_value=120, step=1)
    # st.write(f"Nome: {nome}, Idade: {idade}")
    with st.container():
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.0, 1.0, 1.0, 1.3, 1.7, 1.8, 1.7, 1.4])

        tamanho_grupo = col1.number_input("Grupo:", min_value=1, value=3000)
        numero_cartas_adquiridas = col2.number_input("Cartas:", min_value=1,
                                                     max_value=tamanho_grupo, value=5)
        sorteio = col3.number_input("Sorteio:", min_value=1, max_value=tamanho_grupo, value=1)
        lance_livre = col4.number_input("Lance Livre:", min_value=1, max_value=tamanho_grupo, value=4)
        lance_fidel_6m = col5.number_input("Lance Fidel 6m:", min_value=1, max_value=tamanho_grupo, value=3)
        lance_fidel_12m = col6.number_input("Lance Fidel 12m:", min_value=1, max_value=tamanho_grupo, value=3)
        lance_fixo_30 = col7.number_input("Lance Fixo 30%:", min_value=1, max_value=tamanho_grupo, value=2)
        numero_de_sucessos = col8.number_input("Sucessos k:", min_value=1,
                                               max_value=numero_cartas_adquiridas,
                                               value=1)

    # Botão e gráfico
    if st.button("Gerar Gráficos"):
        cartas_por_mes = sorteio + lance_livre + lance_fidel_6m + lance_fidel_12m + lance_fixo_30
        n_meses = math.ceil(tamanho_grupo / cartas_por_mes)

        rodadas_removidas = cria_rodadas_de_remocao(sorteio, cartas_por_mes - sorteio, tamanho_grupo)
        rodada_por_mes = [(i + 1) * cartas_por_mes for i in range(n_meses)]
        rodada_por_mes = [min(r, tamanho_grupo) for r in rodada_por_mes]

        curva_original = [
            probabilidade_sucesso_ate_k(tamanho_grupo, numero_cartas_adquiridas, k, numero_de_sucessos) * 100 for k in
            rodada_por_mes]
        curva_ajustada = curva_com_ajuste_propagado(tamanho_grupo, numero_cartas_adquiridas, numero_de_sucessos,
                                                    tamanho_grupo, rodadas_removidas)
        curva_ajustada_por_mes = [curva_ajustada[k - 1] * 100 for k in rodada_por_mes]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=list(range(1, n_meses + 1)), y=curva_original, mode='lines+markers', name="Original"))
        fig.add_trace(go.Scatter(x=list(range(1, n_meses + 1)), y=curva_ajustada_por_mes, mode='lines+markers',
                                 name="Com remoções propagadas", line=dict(dash='dot')))

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

        # Criando o gráfico de pizza
        fig_pizza = go.Figure(data=[go.Pie(
            labels=['Sorteio', 'Lances Livres', 'Lance Fidel 6m', 'Lance Fidel 12m', 'Lance Fixo 30%'],
            values=[n_meses * sorteio, n_meses * lance_livre, n_meses * lance_fidel_6m, n_meses * lance_fidel_12m, n_meses * lance_fixo_30],
            hole=0.4,  # Para criar um gráfico de rosca; remova ou ajuste para um gráfico de pizza tradicional
            marker=dict(colors=['#1f77b4', '#ff7f0e']),  # Cores personalizadas
            hoverinfo='label+percent',
            textinfo='value'
        )])

        # Configurando o layout do gráfico
        fig_pizza.update_layout(
            title_text='Distribuição de Contemplações',
            annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )

        fig_pizza.update_traces(
            textinfo='percent',
            hovertemplate='%{label}: %{value}<extra></extra>'
        )

        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig_pizza, use_container_width=True)

        st.markdown(f"Total de meses estimado: **{n_meses}**")


elif layout_selecionado == "Modalidade C":
    st.subheader("Sorteio + Lance Livre + Lance Fixo 30% + Lance Lim 50%")
    # nome = st.text_input("Nome:")
    # idade = st.number_input("Idade:", min_value=0, max_value=120, step=1)
    # st.write(f"Nome: {nome}, Idade: {idade}")
    with st.container():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1.0, 1.0, 1.0, 1.3, 1.7, 1.8, 1.8])

        tamanho_grupo = col1.number_input("Grupo:", min_value=1, value=3333)
        numero_cartas_adquiridas = col2.number_input("Cartas:", min_value=1,
                                                     max_value=tamanho_grupo, value=5)
        sorteio = col3.number_input("Sorteio:", min_value=1, max_value=tamanho_grupo, value=1)
        lance_livre = col4.number_input("Lance Livre:", min_value=1, max_value=tamanho_grupo, value=10)
        lance_fixo_30 = col5.number_input("Lance Fixo 30%:", min_value=1, max_value=tamanho_grupo, value=1)
        lance_lim_50 = col6.number_input("Lance Lim 50%:", min_value=1, max_value=tamanho_grupo, value=1)
        numero_de_sucessos = col7.number_input("Sucessos k:", min_value=1,
                                               max_value=numero_cartas_adquiridas,
                                               value=1)

    # Botão e gráfico
    if st.button("Gerar Gráficos"):
        cartas_por_mes = sorteio + lance_livre + lance_fixo_30 + lance_lim_50
        n_meses = math.ceil(tamanho_grupo / cartas_por_mes)

        rodadas_removidas = cria_rodadas_de_remocao(sorteio, cartas_por_mes - sorteio, tamanho_grupo)
        rodada_por_mes = [(i + 1) * cartas_por_mes for i in range(n_meses)]
        rodada_por_mes = [min(r, tamanho_grupo) for r in rodada_por_mes]

        curva_original = [
            probabilidade_sucesso_ate_k(tamanho_grupo, numero_cartas_adquiridas, k, numero_de_sucessos) * 100 for k in
            rodada_por_mes]
        curva_ajustada = curva_com_ajuste_propagado(tamanho_grupo, numero_cartas_adquiridas, numero_de_sucessos,
                                                    tamanho_grupo, rodadas_removidas)
        curva_ajustada_por_mes = [curva_ajustada[k - 1] * 100 for k in rodada_por_mes]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=list(range(1, n_meses + 1)), y=curva_original, mode='lines+markers', name="Original"))
        fig.add_trace(go.Scatter(x=list(range(1, n_meses + 1)), y=curva_ajustada_por_mes, mode='lines+markers',
                                 name="Com remoções propagadas", line=dict(dash='dot')))

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

        # Criando o gráfico de pizza
        fig_pizza = go.Figure(data=[go.Pie(
            labels=['Sorteio', 'Lances Livres', 'Lance Fixo 30%', 'Lance Lim 50%'],
            values=[n_meses * sorteio, n_meses * lance_livre, n_meses * lance_fixo_30, n_meses * lance_lim_50,
                    n_meses * lance_fixo_30],
            hole=0.4,  # Para criar um gráfico de rosca; remova ou ajuste para um gráfico de pizza tradicional
            marker=dict(colors=['#1f77b4', '#ff7f0e']),  # Cores personalizadas
            hoverinfo='label+percent',
            textinfo='value'
        )])

        # Configurando o layout do gráfico
        fig_pizza.update_layout(
            title_text='Distribuição de Contemplações',
            annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )

        fig_pizza.update_traces(
            textinfo='percent',
            hovertemplate='%{label}: %{value}<extra></extra>'
        )

        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig_pizza, use_container_width=True)

        st.markdown(f"Total de meses estimado: **{n_meses}**")
