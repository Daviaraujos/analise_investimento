import streamlit as st
import pandas as pd
import yfinance as yf
import webbrowser

# Configuração da página
st.set_page_config(
    page_title="Jovem investimento",
    page_icon="https://raw.githubusercontent.com/Daviaraujos/analise_investimento/main/logo.png",
    layout="wide",
)

# Título
st.image("https://raw.githubusercontent.com/Daviaraujos/analise_investimento/main/logo.png", width=50)
st.title("Análise de Ações")


st.write(
    "Explore os dados históricos de ações, visualize gráficos interativos e acompanhe indicadores financeiros essenciais.Bem-vindo a jovem investimento!"
)

# Dicionário com os tickers e nomes das empresas
acoes = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc. (Google)",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla, Inc.",
    "META": "Meta Platforms, Inc. (Facebook)",
    "NFLX": "Netflix, Inc.",
    "NVDA": "NVIDIA Corporation",
    "PETR4.SA": "Petrobras",
    "VALE3.SA": "Vale S.A.",
    "ITUB4.SA": "Itaú Unibanco",
    "BBDC3.SA": "Bradesco S.A.",
    "ABEV3.SA": "Ambev S.A.",
    "LREN3.SA": "Lojas Renner",
    "MGLU3.SA": "Magazine Luiza",
    "B3SA3.SA": "B3 S.A.",
    "SUZB3.SA": "Suzano S.A.",
    "GGBR4.SA": "Gerdau S.A."
}

# Configurações do painel lateral
st.sidebar.header("Configurações")

# Usar os nomes das empresas no seletor, mas obter o ticker para consulta
acao_selecionada = st.sidebar.selectbox(
    "Selecione a empresa:",
    list(acoes.values()),  # Exibe os nomes das empresas
    index=0
)

# Encontrar o ticker correspondente ao nome selecionado
ticker = [k for k, v in acoes.items() if v == acao_selecionada][0]

data_inicio = st.sidebar.date_input("Data de início:", pd.to_datetime("2020-01-01"))
data_fim = st.sidebar.date_input("Data de fim:", pd.to_datetime("2023-01-01"))

# Valor investido
valor_investido = st.sidebar.number_input("Valor investido (R$):", min_value=1.0, value=1000.0)

# Baixar dados da ação selecionada
dados = yf.download(ticker, start=data_inicio, end=data_fim)

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
    st.subheader(f"Preço de Fechamento: {acao_selecionada}")
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <h5>Fechamento Diário</h5>
            <span style="border-radius: 5px; margin-left: 10px; cursor: pointer;" title="Este gráfico exibe o preço de fechamento diário da ação. Uma tendência de alta pode indicar crescimento, enquanto uma queda pode sinalizar desafios financeiros.">ℹ️</span>
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

    # Configurar 'Date' como índice antes do gráfico
    colunas_para_grafico = colunas_para_grafico.set_index('Date')

    # Gráfico com médias móveis
    st.subheader(f"Médias Móveis: {acao_selecionada}")
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
    # Primeiro, vamos pegar o preço inicial e final
    preco_inicial = dados['Close'].iloc[0]  # Preço de fechamento no início
    preco_final = dados['Close'].iloc[-1]  # Preço de fechamento no final

    # Calcular o número de ações compradas com o valor investido
    quantidade_acoes = valor_investido / preco_inicial

    # Calcular o valor final do investimento
    valor_final = quantidade_acoes * preco_final

    # Calcular o rendimento do investimento
    rendimento = valor_final - valor_investido
    percentual_rendimento = (rendimento / valor_investido) * 100

    # Exibir o resultado
    st.subheader(f"Resultado do Investimento de R${valor_investido:.2f} em {acao_selecionada}")
    st.write(f"Preço de fechamento inicial: R${preco_inicial:.2f}")
    st.write(f"Preço de fechamento final: R${preco_final:.2f}")
    st.write(f"Quantidade de ações compradas: {quantidade_acoes:.2f}")
    st.write(f"Valor final do investimento: R${valor_final:.2f}")
    st.write(f"Rendimento total: R${rendimento:.2f}")
    st.write(f"Percentual de rendimento: {percentual_rendimento:.2f}%")

    # Indicadores Fundamentais
    st.subheader("Indicadores Fundamentais:")
    try:
        info = yf.Ticker(ticker).info

        # Indicadores de Valuation
        pl = info.get("trailingPE", "N/A")
        div_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
        roe = info.get("returnOnEquity", "N/A") * 100 if info.get("returnOnEquity") else "N/A"
        margem_liquida = info.get("profitMargins", "N/A") * 100 if info.get("profitMargins") else "N/A"

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("P/L (Preço/Lucro)", f"{pl:.2f}" if pl != "N/A" else "N/A")
            st.markdown(
                """
                <span style="cursor: pointer;" title="O P/L mede quanto os investidores estão dispostos a pagar por cada dólar de lucro da empresa. Um P/L mais baixo pode indicar subvalorização.">ℹ️</span>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.metric("Dividend Yield", f"{div_yield:.2f}%")
            st.markdown(
                """
                <span style="cursor: pointer;" title="O Dividend Yield indica o rendimento anual do dividendo em relação ao preço da ação. Valores altos podem atrair investidores que buscam renda passiva.">ℹ️</span>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.metric("ROE", f"{roe:.2f}%" if roe != "N/A" else "N/A")
            st.markdown(
                """
                <span style="cursor: pointer;" title="O ROE mede a rentabilidade da empresa em relação ao patrimônio líquido. Valores mais altos indicam maior retorno sobre o capital dos acionistas.">ℹ️</span>
                """,
                unsafe_allow_html=True
            )
        with col4:
            st.metric("Margem Líquida", f"{margem_liquida:.2f}%" if margem_liquida != "N/A" else "N/A")
            st.markdown(
                """
                <span style="cursor: pointer;" title="A Margem Líquida indica o lucro líquido em relação à receita líquida da empresa. Margens mais altas sugerem uma gestão mais eficiente.">ℹ️</span>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"Erro ao carregar os indicadores: {e}")
