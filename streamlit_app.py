import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import requests

# Configuração da página
st.set_page_config(
    page_title="Jovem Investimento",
    page_icon="https://raw.githubusercontent.com/Daviaraujos/analise_investimento/main/logo.png",
    layout="wide",
)

# Título
st.image("https://raw.githubusercontent.com/Daviaraujos/analise_investimento/main/logo.png", width=50)
st.title("Jovem Investimento")

st.write(
    "Explore os dados históricos de ações, somos uma startup de finanças, visualize gráficos interativos e acompanhe indicadores financeiros essenciais. Bem-vindo ao Jovem Investimento, sua principal ferramenta de finanças!"
)

# Dicionário com os tickers e nomes das empresas
actions = {
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
selected_action = st.sidebar.selectbox(
    "Selecione a empresa:",
    list(actions.values()),  # Exibe os nomes das empresas
    index=0
)

# Encontrar o ticker correspondente ao nome selecionado
ticker = [k for k, v in actions.items() if v == selected_action][0]

start_date = st.sidebar.date_input("Data de início:", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("Data de fim:", pd.to_datetime("2023-01-01"))

# Valor investido
invested_value = st.sidebar.number_input("Valor investido (R$):", min_value=1.0, value=1000.0)

# Baixar dados da ação selecionada
data = yf.download(ticker, start=start_date, end=end_date)

# Verificar se os dados foram carregados corretamente
if data.empty:
    st.error("Não foi possível carregar os dados da ação. Verifique os parâmetros escolhidos.")
else:
    # Normalizar colunas se forem MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Resetar o índice para facilitar o trabalho com a coluna 'Date'
    data = data.reset_index()

    # Gráfico de preço de fechamento
    st.subheader(f"Preço de Fechamento: {selected_action}")
    st.markdown("Este gráfico mostra o comportamento do preço de fechamento da ação ao longo do período selecionado.")
    st.line_chart(data[['Date', 'Close']].set_index('Date'), use_container_width=True)

    # Cálculo de médias móveis
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    # Selecionar colunas necessárias para o gráfico
    chart_columns = data[['Date', 'Close', 'SMA_20', 'SMA_50']].dropna()

    # Configurar 'Date' como índice antes do gráfico
    chart_columns = chart_columns.set_index('Date')

    # Gráfico com médias móveis
    st.subheader(f"Médias Móveis: {selected_action}")
    st.markdown("As médias móveis ajudam a suavizar a variação de preços e identificar tendências de curto e longo prazo.")
    st.line_chart(chart_columns, use_container_width=True)

    # Cálculo de resultados do investimento
    initial_price = data['Close'].iloc[0]  # Preço de fechamento no início
    final_price = data['Close'].iloc[-1]  # Preço de fechamento no final
    shares_quantity = invested_value / initial_price
    final_value = shares_quantity * final_price
    profit = final_value - invested_value
    profit_percent = (profit / invested_value) * 100

    # Cálculo de projeção futura
    years = st.sidebar.slider("Anos para projeção futura:", min_value=1, max_value=10, value=5, help="Selecione o número de anos para estimar o crescimento futuro do investimento.")
    cagr = ((final_price / initial_price) ** (1 / (data['Date'].iloc[-1].year - data['Date'].iloc[0].year))) - 1
    projected_value = invested_value * ((1 + cagr) ** years)

    # Exibir o resultado de forma organizada
    st.subheader(f"Calculadora de Investimento")
    st.markdown("Simule o rendimento do seu investimento com base nos dados históricos da ação.")
    st.markdown("### Resultado do Investimento")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Preço Inicial (R$)", f"{initial_price:.2f}")
        st.metric("Quantidade de Ações", f"{shares_quantity:.2f}")
    with col2:
        st.metric("Preço Final (R$)", f"{final_price:.2f}")
        st.metric("Valor Final (R$)", f"{final_value:.2f}")
    with col3:
        st.metric("Rendimento Total (R$)", f"{profit:.2f}")
        st.metric("Rendimento (%)", f"{profit_percent:.2f}%")

    # Projeção futura
    st.markdown("### Projeção Futura do Investimento")
    st.markdown("Com base na taxa de crescimento anual composta (CAGR), estimamos o valor do seu investimento no futuro.")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CAGR (Taxa de Crescimento Anual Composta)", f"{cagr:.2%}")
    with col2:
        st.metric("Valor Projetado (R$)", f"{projected_value:.2f}")

    # Indicadores Fundamentais
    st.subheader("Indicadores Fundamentais")
    try:
        info = yf.Ticker(ticker).info

        # Indicadores de Valuation
        pl = info.get("trailingPE", "N/A")
        div_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
        roe = info.get("returnOnEquity", "N/A") * 100 if info.get("returnOnEquity") else "N/A"
        net_margin = info.get("profitMargins", "N/A") * 100 if info.get("profitMargins") else "N/A"

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("P/L (Preço/Lucro)", f"{pl:.2f}" if pl != "N/A" else "N/A")
        with col2:
            st.metric("Dividend Yield", f"{div_yield:.2f}%")
        with col3:
            st.metric("ROE", f"{roe:.2f}%" if roe != "N/A" else "N/A")
        with col4:
            st.metric("Margem Líquida", f"{net_margin:.2f}%" if net_margin != "N/A" else "N/A")
    except Exception as e:
        st.error(f"Erro ao carregar os indicadores: {e}")




# Campo de coleta de informações do usuário
st.subheader("Acompanhe o jovem investimento")
st.write("Receba atualizações do sistema que irá te ajudar a escolher melhor seus investimentos com base em dados.")

with st.form("user_data_form"):
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    contato = st.text_input("Contato (opcional)")
    pesquisa = st.text_input("Diga o que achou do sistema, seu feedback é muito importante!")
    enviado = st.form_submit_button("Enviar")

    if enviado:
        # URL correta para envio do Google Forms (substitua pela sua)
        google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfaTzhtb1O1M_K-ukBzsPSqMzgH2AyCqMJu8G4Eyj9GiTpObg/formResponse"

        # Mapeamento de campos no Google Forms
        form_data = {
            "entry.751390283": nome, 
            "entry.186582375": email,  
            "entry.36453594": contato, 
            "entry.921684348": pesquisa, 
        }

        # Enviar dados para o Google Forms
        try:
            response = requests.post(google_form_url, data=form_data)

            if response.status_code == 200:
                st.success("Dados enviados com sucesso! Em breve você receberá atualizações do sistema.")
            else:
                st.error(f"Houve um erro ao enviar os dados. Código de status: {response.status_code}")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
