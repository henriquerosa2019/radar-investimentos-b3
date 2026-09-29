# 📈 Radar B3 - Terminal de Inteligência em Ações Brasileiras

Terminal financeiro pessoal desenvolvido em **Python** com **Streamlit**, **Plotly** e integração com **Yahoo Finance** para rastreamento de ações da B3, cálculo de preços-teto pelos métodos consagrados de **Décio Bazin**, **Benjamin Graham** e **Fórmula Mágica de Joel Greenblatt**.

---

## 🚀 Como Executar o Dashboard

### Opção 1: Pelo Atalho Executável (Mais Fácil)
Basta dar um duplo-clique no arquivo:
```
run_dashboard.bat
```
O terminal iniciará o servidor local e abrirá o dashboard automaticamente no seu navegador padrão (`http://localhost:8501`).

### Opção 2: Pelo Terminal / PowerShell
Abra o PowerShell na pasta do projeto e execute:
```bash
python -m streamlit run app.py
```

---

## 🎯 Funcionalidades Principais

1. **Panorama do Mercado em Tempo Real e Fechamento:**
   * Cotações e variação percentual do **Ibovespa**, **Dólar (PTAX)** e volume.
   * Contadores dinâmicos de ações com Dividend Yield $\ge 6\%$ e papéis com desconto expressivo de Graham.

2. **Radar de Oportunidades & Screening:**
   * **Top Dividendos (Bazin):** Ranking das maiores pagadoras de proventos com cálculo do preço-teto Bazin.
   * **Top Desconto (Graham):** Ações com maior margem de segurança baseada no Valor Intrínseco de Benjamin Graham ($V = \sqrt{22.5 \times LPA \times VPA}$).
   * **Fórmula Mágica (Greenblatt):** Ranqueamento automático que cruza barateza de preço ($P/L$) com eficiência do negócio ($ROE$).
   * **Filtros Personalizados:** Filtre por setor (Bancos, Energia, Saneamento, Commodities, Consumo, etc.), DY mínimo, P/L e ROE.

3. **Raio-X Individual do Ativo:**
   * Gráficos interativos com **Candlestick**, médias móveis de 20 e 200 períodos e linhas de preço-teto Bazin e Graham sobrepostas.
   * Quadro completo de indicadores contábeis: $P/L$, $P/VP$, $ROE$, Margem Líquida, $LPA$ e $VPA$.

4. **Simulador de Preço Teto & Renda Passiva:**
   * Simule o seu próprio preço teto ajustando a taxa de retorno mínima desejada.
   * Calcule a projeção de renda passiva anual e mensal ao investir determinado valor (ex: R$ 5.000, R$ 10.000).

5. **Guia Prático para o Investidor:**
   * Didática completa sobre setores perenes (método **BEST**: Bancos, Energia, Saneamento, Telecom/Seguros).
   * Como reinvestir dividendos e acelerar o efeito bola de neve patrimonial.

---

## 📂 Estrutura de Arquivos

* `app.py`: Interface interativa do usuário construída em Streamlit com Plotly.
* `data_fetcher.py`: Coleta de cotações e fundamentos das mais de 50 principais ações da B3 via Yahoo Finance, com cache local inteligente (`market_cache.json`).
* `valuation_engine.py`: Motor matemático dos modelos de Graham, Bazin e Fórmula Mágica.
* `run_dashboard.bat`: Script de inicialização rápida com um clique.
* `requirements.txt`: Lista de dependências Python.
