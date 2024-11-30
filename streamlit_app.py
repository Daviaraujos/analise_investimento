import streamlit as st
import pandas as pd
import yfinance as yf
import webbrowser

# Configuração da página
st.set_page_config(
    page_title="Jovem investimento - Análise de ações",
    page_icon="Logo.png",
    layout="wide",
)

st.image("/Logo.png", width=50)
st.title("Jovem investimento")

# Subtítulo
st.write(
    "Explore os dados históricos de ações, visualize gráficos interativos e acompanhe indicadores financeiros essenciais.  Bem-vindo ao jovem investimo"
)

# Lista de tickers disponíveis
lista_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "PETR4.SA", "VALE3.SA",
    "ITUB4.SA", "BBDC3.SA", "ABEV3.SA", "LREN3.SA", "MGLU3.SA", "B3SA3.SA", "SUZB3.SA", "GGBR4.SA"
]

# Configurações do painel lateral
st.sidebar.header("Configurações")
acao = st.sidebar.selectbox("Selecione a ação:", lista_tickers, index=0)
data_inicio = st.sidebar.date_input("Data de início:", pd.to_datetime("2020-01-01"))
data_fim = st.sidebar.date_input("Data de fim:", pd.to_datetime("2023-01-01"))

# Valor investido
valor_investido = st.sidebar.number_input("Valor investido (R$):", min_value=1.0, value=1000.0)

# Baixar dados da ação selecionada
dados = yf.download(acao, start=data_inicio, end=data_fim)

# Verificar se os dados foram carregados corretamente
if dados.empty:
    st.error("Não foi possível carregar os dados da ação. Verifique os parâmetros escolhidos.")
else:
    # Normalizar colunas se forem MultiIndex
    if isinstance(dados.columns, pd.MultiIndex):
        dados.columns = dados.columns.get_level_values(0)

    # Resetar o índice para facilitar o trabalho com a coluna 'Date'
    dados = dados.reset_index()

    # Gráfico de preço de fechamento
    st.subheader(f"Gráfico Preço de Fechamento: {acao}")
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <h5>Preço de Fechamento Diário</h5>
            <span style="margin-left: 8px; cursor: pointer;" title="Este gráfico exibe o preço de fechamento diário da ação. Uma tendência de alta pode indicar crescimento, enquanto uma queda pode sinalizar desafios financeiros.">ℹ️</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.line_chart(dados[['Date', 'Close']].set_index('Date'), use_container_width=True)

    # Cálculo de médias móveis
    dados['SMA_20'] = dados['Close'].rolling(window=20).mean()
    dados['SMA_50'] = dados['Close'].rolling(window=50).mean()

    # Selecionar colunas necessárias para o gráfico
    colunas_para_grafico = dados[['Date', 'Close', 'SMA_20', 'SMA_50']].dropna()
    colunas_para_grafico = colunas_para_grafico.set_index('Date')

    # Gráfico com médias móveis
    st.subheader(f"Médias Móveis: {acao}")
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <h5>Médias Móveis</h5>
            <span style="margin-left: 8px; cursor: pointer;" title="As médias móveis ajudam a suavizar os dados e identificar tendências. A SMA_20 reflete tendências de curto prazo e a SMA_50, de longo prazo. Um cruzamento da SMA_20 acima da SMA_50 pode indicar uma tendência de alta.">ℹ️</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.line_chart(colunas_para_grafico, use_container_width=True)

    # Cálculo de resultados do investimento
    preco_inicial = dados['Close'].iloc[0]
    preco_final = dados['Close'].iloc[-1]
    quantidade_acoes = valor_investido / preco_inicial
    valor_final = quantidade_acoes * preco_final
    rendimento = valor_final - valor_investido
    percentual_rendimento = (rendimento / valor_investido) * 100

    # Calculadora de investimento
    st.subheader("Calculadora de Investimento")
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <h5>Simulação de Rendimento</h5>
            <span style="margin-left: 8px; cursor: pointer;" title="Insira o valor investido e veja os resultados simulados com base nos preços históricos.">ℹ️</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Preço Inicial (R$)", f"{preco_inicial:.2f}")
        st.markdown(
            """
            <span style="cursor: pointer;" title="O preço inicial da ação no período selecionado.">ℹ️</span>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.metric("Preço Final (R$)", f"{preco_final:.2f}")
        st.markdown(
            """
            <span style="cursor: pointer;" title="O preço final da ação no período selecionado.">ℹ️</span>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.metric("Qtde. Ações", f"{quantidade_acoes:.2f}")
        st.markdown(
            """
            <span style="cursor: pointer;" title="A quantidade de ações compradas com o valor investido.">ℹ️</span>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.metric("Valor Final (R$)", f"{valor_final:.2f}")
        st.markdown(
            """
            <span style="cursor: pointer;" title="O valor final do investimento baseado no preço final da ação.">ℹ️</span>
            """,
            unsafe_allow_html=True
        )
    with col5:
        st.metric("Rendimento (%)", f"{percentual_rendimento:.2f}%")
        st.markdown(
            """
            <span style="cursor: pointer;" title="A variação percentual do investimento no período selecionado.">ℹ️</span>
            """,
            unsafe_allow_html=True
        )

    # Gráfico de valorização do investimento
    st.subheader("Gráfico de Valorização do Investimento")
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <h5>Valorização do Investimento</h5>
            <span style="margin-left: 8px; cursor: pointer;" title="Este gráfico mostra a evolução do valor do seu investimento ao longo do período selecionado.">ℹ️</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    dados['Investimento'] = quantidade_acoes * dados['Close']
    st.line_chart(dados[['Date', 'Investimento']].set_index('Date'), use_container_width=True)
