"""
Dashboard Inteligente de Ações da B3 - Análise Fundamentalista, Graham, Bazin e Tempo Real.
Enriquecido com tooltips explicativos para investidores leigos e iniciantes.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from data_fetcher import fetch_all_tickers, get_ticker_history, DEFAULT_TICKERS
from valuation_engine import apply_valuation_models, calculate_graham_price, calculate_bazin_price

# Configuração da página
st.set_page_config(
    page_title="Radar Investimentos B3",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
st.markdown("""
<style>
    .metric-card {
        background-color: #1E222D;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #2A2E39;
        margin-bottom: 10px;
    }
    .metric-title {
        color: #9E9E9E;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 24px;
        font-weight: 700;
    }
    .badge-green {
        background-color: #0E4429;
        color: #3FB950;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-red {
        background-color: #4B1A1D;
        color: #F85149;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-yellow {
        background-color: #4D3800;
        color: #E3B341;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }
    /* Estilização para tooltips customizados em textos */
    .tooltip-icon {
        cursor: help;
        color: #58A6FF;
        font-size: 14px;
        margin-left: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
st.sidebar.image("https://img.icons8.com/fluency/96/bullish.png", width=64)
st.sidebar.title("Radar Investimentos B3")
st.sidebar.caption("Investimentos Inteligentes na Bolsa")

# Botão de atualização com tooltip explicativo
if st.sidebar.button(
    "🔄 Atualizar Cotações Agora",
    use_container_width=True,
    help="Clique para buscar os preços e fechamentos mais recentes do pregão da B3 direto do Yahoo Finance e recalcular os rankings."
):
    with st.spinner("Atualizando cotações e fundamentos na B3..."):
        raw_stocks, market_ov = fetch_all_tickers(force_refresh=True)
    st.sidebar.success("Cotações atualizadas com sucesso!")
else:
    raw_stocks, market_ov = fetch_all_tickers(force_refresh=False)

# Aplica os modelos quantitativos
processed_stocks = apply_valuation_models(raw_stocks)
df_all = pd.DataFrame(processed_stocks)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtros do Screening")

# Filtro por Setor
all_sectors = ["Todos"] + sorted(list(df_all["sector"].dropna().unique())) if not df_all.empty else ["Todos"]
selected_sector = st.sidebar.selectbox(
    "Setor de Atuação",
    all_sectors,
    help="Permite filtrar as empresas por área da economia. Dica: 'Energia & Saneamento' e 'Financeiro & Seguros' são os setores mais seguros e previsíveis para quem quer dividendos."
)

# Sliders de Filtro com tooltips
min_dy = st.sidebar.slider(
    "Dividend Yield Mínimo (%)",
    min_value=0.0,
    max_value=15.0,
    value=0.0,
    step=0.5,
    help="Dividend Yield (DY): É o percentual do preço da ação que a empresa devolveu em dinheiro vivo aos sócios nos últimos 12 meses. O método Décio Bazin recomenda buscar ações com DY acima de 6%."
)

max_pe = st.sidebar.slider(
    "P/L Máximo (Preço/Lucro)",
    min_value=1.0,
    max_value=40.0,
    value=30.0,
    step=1.0,
    help="Preço sobre Lucro (P/L): Mostra quantos anos de lucros atuais seriam necessários para recuperar o valor investido na ação. Quanto menor o P/L (ex: abaixo de 10), mais barata a empresa tende a estar."
)

min_roe = st.sidebar.slider(
    "ROE Mínimo (%)",
    min_value=0.0,
    max_value=40.0,
    value=0.0,
    step=1.0,
    help="Retorno sobre Patrimônio Líquido (ROE): Mede a eficiência da empresa em transformar o dinheiro dos sócios em lucro real. Acima de 12% a 15% indica uma empresa muito lucrativa e bem gerida."
)

only_graham_discount = st.sidebar.checkbox(
    "Apenas com Desconto de Graham (> 0%)",
    value=False,
    help="Filtra somente as ações cujo preço atual está abaixo do Valor Intrínseco calculado pela fórmula de Benjamin Graham (comprando empresa com margem de segurança)."
)

# Filtragem do DataFrame
df_filtered = df_all.copy()
if not df_filtered.empty:
    if selected_sector != "Todos":
        df_filtered = df_filtered[df_filtered["sector"] == selected_sector]
    if min_dy > 0:
        df_filtered = df_filtered[df_filtered["dy"] >= min_dy]
    if max_pe < 40:
        df_filtered = df_filtered[(df_filtered["pe"] > 0) & (df_filtered["pe"] <= max_pe)]
    if min_roe > 0:
        df_filtered = df_filtered[df_filtered["roe"] >= min_roe]
    if only_graham_discount:
        df_filtered = df_filtered[df_filtered["graham_margin"] > 0]

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica de Ouro:** Passe o mouse sobre qualquer interrogação ❓ na tela para ver uma explicação simples e didática de cada termo!")

# ----------------- CABEÇALHO & CARDS PRINCIPAIS -----------------
st.title("📈 Radar Investimentos B3")
st.caption(f"Dados atualizados • Base monitorada: {len(df_all)} ativos líderes da bolsa brasileira")

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

ibov = market_ov.get("Ibovespa", {})
ibov_price = ibov.get("price", 0)
ibov_chg = ibov.get("change_pct", 0)

dolar = market_ov.get("Dólar (USD/BRL)", {})
dolar_price = dolar.get("price", 0)
dolar_chg = dolar.get("change_pct", 0)

with col_m1:
    st.metric(
        "Ibovespa",
        f"{ibov_price:,.0f} pts" if ibov_price else "N/D",
        f"{ibov_chg:+.2f}%",
        help="O principal termômetro da Bolsa de Valores do Brasil. Mede o desempenho médio das cerca de 80 maiores empresas do país."
    )

with col_m2:
    st.metric(
        "Dólar (PTAX)",
        f"R$ {dolar_price:.2f}" if dolar_price else "N/D",
        f"{dolar_chg:+.2f}%",
        delta_color="inverse",
        help="Cotação comercial da moeda americana em Reais. Dólar em alta ajuda empresas exportadoras (como Vale e Petrobras) e encarece produtos importados."
    )

with col_m3:
    st.metric(
        "Ativos Monitorados",
        f"{len(df_all)}",
        help="Total de empresas selecionadas e monitoradas neste terminal. Escolhemos as ações mais sólidas e líquidas negociadas na B3."
    )

with col_m4:
    dividend_count = len(df_all[df_all["dy"] >= 6.0]) if not df_all.empty else 0
    st.metric(
        "Dividendos ≥ 6% (Bazin)",
        f"{dividend_count} ações",
        help="Quantidade de ações que pagam no mínimo 6% ao ano em proventos (dinheiro limpo no bolso). Esse é o critério de ouro do método Décio Bazin para aposentadoria com ações."
    )

with col_m5:
    opp_count = len(df_all[df_all["graham_margin"] > 20]) if not df_all.empty else 0
    st.metric(
        "Desconto Graham > 20%",
        f"{opp_count} ações",
        help="Ações em verdadeira 'liquidação' na bolsa: estão custando pelo menos 20% mais barato do que o valor justo calculado por Benjamin Graham."
    )

st.markdown("---")

# ----------------- ABAS PRINCIPAIS -----------------
tab_radar, tab_raiox, tab_simulador, tab_guia = st.tabs([
    "🎯 Radar de Oportunidades (Screening)",
    "🔍 Raio-X do Ativo & Gráficos",
    "🧮 Simulador de Preço Teto & Renda",
    "📚 Guia do Investidor Iniciante"
])

# ================= TAB 1: RADAR DE OPORTUNIDADES =================
with tab_radar:
    st.subheader("Oportunidades em Destaque na B3")
    
    col_rk1, col_rk2, col_rk3 = st.columns(3)
    
    with col_rk1:
        st.markdown("#### 💰 Top Dividendos (Décio Bazin)")
        st.caption("Ações que mais pagaram proventos nos últimos 12 meses sobre a cotação de hoje.")
        if not df_all.empty:
            top_dy = df_all.sort_values(by="dy", ascending=False).head(5)[["code", "price", "dy", "bazin_price"]]
            top_dy = top_dy.rename(columns={"code": "Ação", "price": "Preço (R$)", "dy": "DY (%)", "bazin_price": "Teto Bazin (R$)"})
            st.dataframe(
                top_dy.style.format({"Preço (R$)": "R$ {:.2f}", "DY (%)": "{:.2f}%", "Teto Bazin (R$)": "R$ {:.2f}"}),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Ação": st.column_config.TextColumn(help="Código de negociação do ativo na B3."),
                    "Preço (R$)": st.column_config.NumberColumn(help="Cotação negociada agora no pregão."),
                    "DY (%)": st.column_config.NumberColumn(help="Percentual recebido em dividendos nos últimos 12 meses."),
                    "Teto Bazin (R$)": st.column_config.NumberColumn(help="Valor MÁXIMO a pagar para garantir no mínimo 6% de retorno ao ano.")
                }
            )

    with col_rk2:
        st.markdown("#### 💎 Top Margem de Segurança (Graham)")
        st.caption("Ações com maior desconto em relação ao Valor Intrínseco de Benjamin Graham.")
        if not df_all.empty:
            top_graham = df_all[df_all["graham_margin"].notnull()].sort_values(by="graham_margin", ascending=False).head(5)[["code", "price", "graham_price", "graham_margin"]]
            top_graham = top_graham.rename(columns={"code": "Ação", "price": "Preço (R$)", "graham_price": "Teto Graham (R$)", "graham_margin": "Margem (%)"})
            st.dataframe(
                top_graham.style.format({"Preço (R$)": "R$ {:.2f}", "Teto Graham (R$)": "R$ {:.2f}", "Margem (%)": "+{:.1f}%"}),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Ação": st.column_config.TextColumn(help="Código de negociação na B3."),
                    "Preço (R$)": st.column_config.NumberColumn(help="Cotação atual da ação."),
                    "Teto Graham (R$)": st.column_config.NumberColumn(help="Valor Justo calculado pela fórmula de Benjamin Graham."),
                    "Margem (%)": st.column_config.NumberColumn(help="Quanto mais positivo, maior é o desconto da ação em relação ao valor que ela realmente tem.")
                }
            )

    with col_rk3:
        st.markdown("#### ⚡ Fórmula Mágica (Greenblatt)")
        st.caption("Combinação ideal: maior rentabilidade (ROE) com menor preço na bolsa (P/L).")
        if not df_all.empty and "magic_rank" in df_all.columns:
            top_magic = df_all.sort_values(by="magic_rank", ascending=True).head(5)[["code", "price", "pe", "roe", "magic_rank"]]
            top_magic = top_magic.rename(columns={"code": "Ação", "price": "Preço (R$)", "pe": "P/L", "roe": "ROE (%)", "magic_rank": "Rank"})
            st.dataframe(
                top_magic.style.format({"Preço (R$)": "R$ {:.2f}", "P/L": "{:.1f}x", "ROE (%)": "{:.1f}%"}),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Ação": st.column_config.TextColumn(help="Código da ação na bolsa."),
                    "Preço (R$)": st.column_config.NumberColumn(help="Cotação atual."),
                    "P/L": st.column_config.TextColumn(help="Preço/Lucro: menor indica empresa mais barata."),
                    "ROE (%)": st.column_config.NumberColumn(help="Retorno sobre Patrimônio: maior indica negócio mais lucrativo."),
                    "Rank": st.column_config.NumberColumn(help="Posição combinada de qualidade e preço (1º é o melhor da bolsa).")
                }
            )

    st.markdown("---")
    st.subheader(f"📋 Tabela Completa de Screening ({len(df_filtered)} ações encontradas)")
    st.caption("Passe o mouse sobre os títulos das colunas para entender o significado de cada indicador financeiro:")

    if not df_filtered.empty:
        display_df = df_filtered[[
            "code", "shortName", "sector", "price", "change_pct", "dy", "pe", "pb", "roe",
            "graham_price", "graham_margin", "bazin_price", "status"
        ]].copy()
        
        display_df.columns = [
            "Ação", "Empresa", "Setor", "Cotação (R$)", "Var. Dia (%)", "DY (%)", "P/L", "P/VP", "ROE (%)",
            "Preço Graham (R$)", "Margem Graham (%)", "Preço Bazin (R$)", "Diagnóstico"
        ]

        st.dataframe(
            display_df.style.format({
                "Cotação (R$)": "R$ {:.2f}",
                "Var. Dia (%)": "{:+.2f}%",
                "DY (%)": "{:.2f}%",
                "P/L": lambda x: f"{x:.1f}x" if pd.notnull(x) else "-",
                "P/VP": lambda x: f"{x:.2f}x" if pd.notnull(x) else "-",
                "ROE (%)": "{:.1f}%",
                "Preço Graham (R$)": lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "-",
                "Margem Graham (%)": lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-",
                "Preço Bazin (R$)": lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "-"
            }),
            use_container_width=True,
            height=450,
            column_config={
                "Ação": st.column_config.TextColumn(help="Código da ação na B3 (ex: PETR4, BBAS3, CMIG4)."),
                "Empresa": st.column_config.TextColumn(help="Nome fantasia ou razão social da empresa."),
                "Setor": st.column_config.TextColumn(help="Ramo da economia em que a companhia atua."),
                "Cotação (R$)": st.column_config.NumberColumn(help="Preço da última negociação no pregão."),
                "Var. Dia (%)": st.column_config.NumberColumn(help="Percentual de alta ou queda da ação no dia de hoje."),
                "DY (%)": st.column_config.NumberColumn(help="Dividend Yield: retorno em proventos pagos nos últimos 12 meses dividido pela cotação atual."),
                "P/L": st.column_config.TextColumn(help="Preço/Lucro: quantos anos de lucro pagam o preço da ação. Abaixo de 10x é considerado barato."),
                "P/VP": st.column_config.TextColumn(help="Preço sobre Valor Patrimonial: compara o preço na bolsa com tudo o que a empresa possui de patrimônio. Abaixo de 1,5x é atrativo."),
                "ROE (%)": st.column_config.NumberColumn(help="Retorno sobre Patrimônio Líquido: mede a capacidade de gerar lucro com o próprio capital. Acima de 12% é excelente."),
                "Preço Graham (R$)": st.column_config.TextColumn(help="Valor Justo de Benjamin Graham com base no lucro e patrimônio da empresa."),
                "Margem Graham (%)": st.column_config.TextColumn(help="Desconto percentual em relação ao preço justo de Graham. Se positivo (+), significa que está com desconto."),
                "Preço Bazin (R$)": st.column_config.TextColumn(help="Preço Teto de Décio Bazin: valor limite para pagar se você quiser receber pelo menos 6% ao ano em dividendos."),
                "Diagnóstico": st.column_config.TextColumn(help="Resumo visual inteligente sobre a atratividade da ação para compra hoje.")
            }
        )
    else:
        st.warning("Nenhuma ação atende aos critérios dos filtros selecionados no menu lateral.")

# ================= TAB 2: RAIO-X DO ATIVO =================
with tab_raiox:
    st.subheader("Análise Detalhada de Ativo")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        selected_code = st.selectbox(
            "Selecione o Ativo para Análise:",
            options=sorted(df_all["code"].tolist()) if not df_all.empty else ["BBAS3"],
            help="Escolha qualquer ação monitorada na B3 para carregar o gráfico histórico completo de preços, médias móveis e indicadores contábeis."
        )
    
    stock_info = df_all[df_all["code"] == selected_code].iloc[0] if not df_all.empty else {}
    
    if stock_info is not None and not stock_info.empty:
        symbol = stock_info["symbol"]
        price = stock_info["price"]
        graham = stock_info["graham_price"]
        bazin = stock_info["bazin_price"]
        dy = stock_info["dy"]
        roe = stock_info["roe"]
        pe = stock_info["pe"]
        pb = stock_info["pb"]
        margin_net = stock_info["margin_net"]
        lpa = stock_info["lpa"]
        vpa = stock_info["vpa"]

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.metric(
                "Cotação Atual",
                f"R$ {price:.2f}",
                f"{stock_info['change_pct']:+.2f}%",
                help="Preço atual da ação negociado na B3 neste momento."
            )
        with col_c2:
            st.metric(
                "Preço Teto Bazin (DY ≥ 6%)",
                f"R$ {bazin:.2f}" if bazin else "N/D", 
                f"{((bazin - price)/price)*100:+.1f}% margem" if bazin else None,
                help="O valor MÁXIMO que você deve pagar por esta ação. Se a cotação estiver ABAIXO deste valor, você receberá mais de 6% ao ano em dividendos."
            )
        with col_c3:
            st.metric(
                "Preço Justo Graham",
                f"R$ {graham:.2f}" if graham else "N/D",
                f"{((graham - price)/price)*100:+.1f}% margem" if graham else None,
                help="Valor intrínseco calculado pela fórmula de Benjamin Graham: raiz(22.5 * LPA * VPA). Se a cotação estiver abaixo dele, você compra a empresa com desconto."
            )
        with col_c4:
            st.metric(
                "Dividend Yield (12M)",
                f"{dy:.2f}%",
                f"R$ {stock_info['estimated_dpa']:.2f}/ação ano",
                help="Percentual recebido em proventos nos últimos 12 meses e o valor em reais (R$) pago por cada ação."
            )

        # Gráfico Histórico Interativo Plotly
        st.markdown("#### Histórico de Preços e Médias Móveis")
        st.caption("💡 **Dica do Gráfico:** Barras verdes = dia de alta; Barras vermelhas = dia de baixa. A linha verde tracejada é o Preço Teto Bazin e a linha roxa pontilhada é o Preço Justo Graham.")
        hist_df = get_ticker_history(symbol, period="1y")

        if not hist_df.empty:
            fig = go.Figure()
            # Candlestick
            fig.add_trace(go.Candlestick(
                x=hist_df.index,
                open=hist_df['Open'],
                high=hist_df['High'],
                low=hist_df['Low'],
                close=hist_df['Close'],
                name="Preço"
            ))
            # Média 20
            fig.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df['MA20'],
                line=dict(color='#FFA726', width=1.5),
                name='Média Móvel 20d (Curto Prazo)'
            ))
            # Média 200
            fig.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df['MA200'],
                line=dict(color='#42A5F5', width=1.5),
                name='Média Móvel 200d (Longo Prazo)'
            ))
            # Linha de Preço Teto Bazin
            if bazin:
                fig.add_hline(
                    y=bazin,
                    line_dash="dash",
                    line_color="#3FB950",
                    annotation_text=f"Teto Bazin (R$ {bazin:.2f})",
                    annotation_position="top right"
                )
            # Linha de Preço Justo Graham
            if graham:
                fig.add_hline(
                    y=graham,
                    line_dash="dot",
                    line_color="#A371F7",
                    annotation_text=f"Teto Graham (R$ {graham:.2f})",
                    annotation_position="bottom right"
                )

            fig.update_layout(
                height=450,
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Cartão de Fundamentos com Tooltips Explicativos
        st.markdown("#### Fundamentos & Saúde da Empresa")
        fcol1, fcol2, fcol3, fcol4, fcol5, fcol6 = st.columns(6)
        with fcol1:
            st.metric(
                "P/L (Preço/Lucro)",
                f"{pe:.1f}x" if pe else "N/D",
                help="Mede quantos anos de lucros atuais recuperam o preço da ação. Valores abaixo de 10x são excelentes."
            )
        with fcol2:
            st.metric(
                "P/VP (Patrimônio)",
                f"{pb:.2f}x" if pb else "N/D",
                help="Preço da ação dividido pelo Patrimônio Líquido por ação. Abaixo de 1,5x é seguro; abaixo de 1,0x significa comprar a empresa mais barata do que tudo o que ela tem de patrimônio."
            )
        with fcol3:
            st.metric(
                "ROE (Rentabilidade)",
                f"{roe:.1f}%",
                help="Retorno sobre Patrimônio Líquido: mostra quão eficiente a diretoria é para multiplicar o dinheiro dos acionistas. Acima de 12% a 15% é ótimo."
            )
        with fcol4:
            st.metric(
                "Margem Líquida",
                f"{margin_net:.1f}%",
                help="De cada R$ 100 vendidos pela empresa, quanto sobra limpo como lucro no bolso após pagar todos os custos e impostos."
            )
        with fcol5:
            st.metric(
                "LPA (Lucro p/ Ação)",
                f"R$ {lpa:.2f}" if lpa else "N/D",
                help="Lucro por Ação: o lucro líquido da empresa no ano dividido pelo número total de ações existentes."
            )
        with fcol6:
            st.metric(
                "VPA (Vl. Patr. p/ Ação)",
                f"R$ {vpa:.2f}" if vpa else "N/D",
                help="Valor Patrimonial por Ação: todo o patrimônio físico e reservas da empresa dividido pelo total de ações."
            )

# ================= TAB 3: SIMULADOR =================
with tab_simulador:
    st.subheader("Simulador de Preço Teto & Renda Passiva Futura")
    st.write("Calcule quanto você pode pagar por uma ação e quanto receberá de proventos.")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("#### 1. Parâmetros da Simulação")
        sim_stock = st.selectbox(
            "Escolha uma ação como base:",
            options=sorted(df_all["code"].tolist()) if not df_all.empty else ["BBAS3"],
            key="sim_select",
            help="Carrega os dados e o dividendo recente da ação selecionada para facilitar a sua simulação."
        )
        sim_info = df_all[df_all["code"] == sim_stock].iloc[0] if not df_all.empty else {}
        
        default_price = float(sim_info.get("price", 30.0))
        default_dpa = float(sim_info.get("estimated_dpa", 2.0))
        
        input_price = st.number_input(
            "Cotação Atual da Ação (R$):",
            value=default_price,
            step=0.5,
            format="%.2f",
            help="Preço que você paga hoje no balcão da corretora para comprar 1 ação."
        )
        input_dpa = st.number_input(
            "Dividendo Anual Esperado por Ação (R$):",
            value=default_dpa,
            step=0.1,
            format="%.2f",
            help="Quanto dinheiro você estima que essa ação pagará por ano para cada unidade que você tiver na carteira."
        )
        input_target_dy = st.slider(
            "Taxa Mínima de Retorno em Dividendos Desejada (% a.a.):",
            min_value=4.0,
            max_value=12.0,
            value=6.0,
            step=0.5,
            help="O retorno mínimo que você exige para investir (Décio Bazin recomenda 6% ao ano livres de impostos)."
        )
        
        calculated_teto = input_dpa / (input_target_dy / 100.0) if input_target_dy > 0 else 0
        current_dy_calc = (input_dpa / input_price) * 100.0 if input_price > 0 else 0

    with col_s2:
        st.markdown("#### 2. Resultado da Análise de Preço")
        st.write(f"Para você obter no mínimo **{input_target_dy:.1f}%** ao ano em dividendos:")
        
        st.success(f"### Preço Teto Máximo a Pagar: **R$ {calculated_teto:.2f}**")
        
        if input_price <= calculated_teto:
            margem = ((calculated_teto - input_price) / input_price) * 100.0
            st.info(f"✅ **Ação em oportunidade!** A cotação atual (R$ {input_price:.2f}) está **{margem:.1f}% abaixo** do seu preço teto. Você terá um Dividend Yield projetado de **{current_dy_calc:.2f}%**.")
        else:
            agio = ((input_price - calculated_teto) / calculated_teto) * 100.0
            st.warning(f"⚠️ **Ação acima do teto.** A cotação atual (R$ {input_price:.2f}) está **{agio:.1f}% mais cara** do que o seu teto para atingir {input_target_dy}%.")

        st.markdown("---")
        st.markdown("#### 3. Projeção de Renda Passiva")
        investimento = st.number_input(
            "Valor a Investir (R$):",
            value=10000.0,
            step=1000.0,
            help="Digite o valor que você planeja aplicar para simular o número de ações que conseguirá comprar e quanto receberá em dividendos."
        )
        
        if input_price > 0:
            qtd_acoes = int(investimento // input_price)
            renda_anual = qtd_acoes * input_dpa
            renda_mensal = renda_anual / 12.0
            
            pcol1, pcol2, pcol3 = st.columns(3)
            with pcol1:
                st.metric(
                    "Total de Ações",
                    f"{qtd_acoes:,} ações",
                    help="Quantidade de ações que o seu dinheiro consegue comprar na cotação atual."
                )
            with pcol2:
                st.metric(
                    "Renda Estimada / Ano",
                    f"R$ {renda_anual:,.2f}",
                    help="Estimativa total de proventos caindo na sua conta ao longo de 1 ano completo."
                )
            with pcol3:
                st.metric(
                    "Média / Mês",
                    f"R$ {renda_mensal:,.2f}",
                    help="Renda passiva média mensal equivalente (embora as empresas paguem trimestralmente ou semestralmente)."
                )

# ================= TAB 4: GUIA DO INVESTIDOR =================
with tab_guia:
    st.subheader("Guia Prático: Como Iniciar e Lucrar no Mercado de Ações")
    
    st.markdown("""
    ### 1. Os 3 Grandes Métodos de Investimento Utilizados Neste Terminal
    
    * **Método Décio Bazin (Foco em Renda Passiva e Dividendos):**
      * Desenvolvido pelo jornalista e investidor Décio Bazin (autor do clássico *Faça Fortuna com Ações*).
      * Regra básica: só comprar ações cujo Dividend Yield seja no mínimo **6% ao ano**.
      * O **Preço Teto** indica o valor limite para pagar pelo papel. Se o papel subir acima do teto, para de comprar e deixa render.
      
    * **Fórmula do Valor Intrínseco de Benjamin Graham (Pai do Value Investing):**
      * Autor de *O Investidor Inteligente* e mentor de Warren Buffett.
      * Fórmula: $V = \sqrt{22.5 \\times LPA \\times VPA}$.
      * O número 22.5 vem da multiplicação de um P/L aceitável máximo de 15 por um P/VP aceitável máximo de 1.5 ($15 \\times 1.5 = 22.5$).
      * Se o preço atual for menor que $V$, você está comprando uma empresa com **Margem de Segurança**.
      
    * **Fórmula Mágica de Joel Greenblatt:**
      * Ordena todas as empresas do mercado por dois critérios:
        1. **Preço (Barateza):** Menor múltiplo de lucro (EV/EBIT ou P/L).
        2. **Qualidade:** Maior retorno sobre o capital (ROE ou ROIC).
      * Seleciona as ações que combinam o melhor dos dois mundos: empresas muito boas a preços acessíveis.
      
    ---
    
    ### 2. O Roteiro Seguro para Iniciar do Zero em Ações da B3
    
    1. **Comece por Setores Perenes (BEST):**
       * **B**ancos (ex: Itaú, Banco do Brasil)
       * **E**nergia Elétrica (ex: Taesa, Engie, CPFL, Equatorial, Cemig)
       * **S**aneamento (ex: Sanepar, Sabesp, Copasa)
       * **T**elecomunicações / Seguros (ex: Vivo, BB Seguridade, Caixa Seguridade)
       * *Por que?* Esses setores vendem serviços essenciais que as pessoas e empresas consomem faça chuva ou faça sol.
       
    2. **Aporte Mensal e Reinvestimento de Dividendos:**
       * O verdadeiro multiplicador de patrimônio no longo prazo é comprar todos os meses e usar os dividendos que caem na conta para comprar mais ações.
       
    3. **Nunca invista o dinheiro da reserva de emergência em ações:**
       * Ações oscilam no curto prazo. Tenha 6 meses de custos de vida no Tesouro Selic ou CDB de liquidez diária antes de investir pesado em bolsa.
    """)

# Rodapé
st.markdown("---")
col_foot1, col_foot2 = st.columns([3, 2])
with col_foot1:
    st.caption("Desenvolvido para análise quantitativa e fundamentalista de ações da B3. Não representa recomendação direta de compra ou venda.")
with col_foot2:
    st.markdown(
        "<div style='text-align: right; color: #8B949E; font-size: 13px; padding-top: 5px;'>"
        "Desenvolvido por: <strong style='color: #58A6FF;'>Henrique Rosa / Antigravity - V1.0 - 2026</strong>"
        "</div>",
        unsafe_allow_html=True
    )
