import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import webbrowser

# Configuração da página
st.set_page_config(
    page_title="Jovem investimento",
    page_icon=":bar_chart:",
    layout="wide",
)

# Título e configuração inicial
st.title("Análise de Ações")
st.sidebar.header("Configurações")

# Lista de tickers da B3 e internacionais
lista_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "PETR4.SA", "VALE3.SA", "ITUB4.SA"]

# Entrada do usuário: seleção de ação
acao = st.sidebar.selectbox(
    "Selecione o ticker da ação:",
    options=lista_tickers,
    index=0  # Define o primeiro ticker como padrão
)

# Entrada do usuário: datas de início e fim
data_inicio = st.sidebar.date_input("Data de início:", value=pd.to_datetime("2020-01-01"))
data_fim = st.sidebar.date_input("Data de fim:", value=pd.to_datetime("2023-01-01"))

# Baixar os dados da ação
st.write(f"### Dados da Ação: {acao}")
dados = yf.download(acao, start=data_inicio, end=data_fim)

# Exibir a tabela com dados básicos
st.write("### Dados Financeiros da Ação:")
st.write(dados.head(20))

# Adicionar cálculo de indicadores financeiros
st.write("### Indicadores Fundamentais:")
try:
    # Obter informações da empresa
    info = yf.Ticker(acao).info

    # Indicadores de Valuation
    pl = info.get("trailingPE", "N/A")
    div_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
    roe = info.get("returnOnEquity", "N/A") * 100 if info.get("returnOnEquity") else "N/A"
    margem_liquida = info.get("profitMargins", "N/A") * 100 if info.get("profitMargins") else "N/A"

    # Exibir os indicadores com explicações
    st.write("### Explicação dos Indicadores:")
    st.write(
        """
        - **P/L (Preço/Lucro)**: Reflete quanto os investidores estão dispostos a pagar por cada dólar de lucro da empresa. Um P/L mais baixo pode sugerir que a ação está subvalorizada.
        - **Dividend Yield**: Indica o rendimento anual do dividendo em relação ao preço da ação. Um alto dividend yield pode ser atrativo para investidores que buscam rendimentos passivos.
        - **ROE (Retorno sobre o Patrimônio Líquido)**: Mede a rentabilidade da empresa em relação ao seu patrimônio. Um ROE mais alto indica maior eficiência na utilização do capital.
        - **Margem Líquida**: Mede a lucratividade da empresa após todas as despesas. Uma margem líquida alta sugere que a empresa tem um bom controle de custos.
        """
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("P/L (Preço/Lucro)", f"{pl:.2f}" if pl != "N/A" else "N/A")
    col2.metric("Dividend Yield", f"{div_yield:.2f}%")
    col3.metric("ROE", f"{roe:.2f}%" if roe != "N/A" else "N/A")
    col4.metric("Margem Líquida", f"{margem_liquida:.2f}%" if margem_liquida != "N/A" else "N/A")
    
    # Adicionar botão para buscar informações sobre a empresa no Google
    if st.button("Buscar no Google sobre a empresa"):
        query = info.get("shortName", acao)
        webbrowser.open(f"https://www.google.com/search?q={query}")
except Exception as e:
    st.error(f"Erro ao obter indicadores: {e}")

# Comentário sobre o gráfico de preço de fechamento
st.write("### Gráfico de Preço de Fechamento:")
st.write(
    """
    O **gráfico de preço de fechamento** mostra o histórico de preços ao final de cada dia de negociação. A análise dessa curva pode ajudar a identificar a tendência de alta ou baixa da ação.
    Um movimento ascendente pode indicar que a empresa está em crescimento, enquanto uma queda pode sinalizar problemas financeiros ou mudanças no mercado.
    """
)

# Gráfico de preço de fechamento
st.write("### Gráfico de Preço de Fechamento")
fig, ax = plt.subplots(figsize=(15, 5)) 
ax.plot(dados['Close'], label="Preço de Fechamento")
ax.set_title(f"Preço de Fechamento - {acao}")
ax.set_xlabel("Data")
ax.set_ylabel("Preço (USD)")
ax.legend()
st.pyplot(fig)  # Exibe o gráfico criado

# Comentário sobre as médias móveis
st.write("###  Médias Móveis:")
st.write(
    """
    As **médias móveis** são indicadores técnicos que ajudam a suavizar os dados de preços, tornando mais fácil identificar tendências. 
    A **Média Móvel de 20 dias (SMA_20)** reflete as últimas 20 sessões de preço, enquanto a **Média Móvel de 50 dias (SMA_50)** é uma tendência mais longa. 
    Quando a média de curto prazo (SMA_20) cruza para cima da média de longo prazo (SMA_50), pode ser um sinal de compra (tendência de alta), e o oposto pode indicar uma tendência de venda.
    """
)

# Calcular e exibir média móvel (SMA)
dados['SMA_20'] = dados['Close'].rolling(window=20).mean()
dados['SMA_50'] = dados['Close'].rolling(window=50).mean()

st.write("### Gráfico com Médias Móveis")
fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(dados['Close'], label="Preço de Fechamento", alpha=0.7)
ax.plot(dados['SMA_20'], label="Média Móvel 20 dias", linestyle="--")
ax.plot(dados['SMA_50'], label="Média Móvel 50 dias", linestyle="--")
ax.set_title(f"Médias Móveis - {acao}")
ax.set_xlabel("Data")
ax.set_ylabel("Preço (USD)")
ax.legend()
st.pyplot(fig)
