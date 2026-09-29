"""
Módulo de coleta e cache de dados de mercado para ações da B3.
"""

import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# Lista curada com as ações mais líquidas e negociadas da B3
DEFAULT_TICKERS = [
    # Bancos & Seguros
    "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "SANB11.SA", "BPAC11.SA", "B3SA3.SA", "BBSE3.SA", "CXSE3.SA",
    # Energia Elétrica & Saneamento (Forte em Dividendos)
    "TAEE11.SA", "EGIE3.SA", "CPLE6.SA", "EQTL3.SA", "TRPL4.SA", "CMIG4.SA", "ENEV3.SA", "SBSP3.SA", "CSMG3.SA", "SAPR11.SA",
    # Commodities, Petróleo & Mineração
    "PETR4.SA", "VALE3.SA", "PRIO3.SA", "CSNA3.SA", "GGBR4.SA", "SUZB3.SA", "KLBN11.SA", "UGPA3.SA",
    # Indústria, Logística & Infraestrutura
    "WEGE3.SA", "RENT3.SA", "RAIL3.SA", "EMBR3.SA", "CCRO3.SA", "POMO4.SA",
    # Consumo, Alimentos, Bebidas & Varejo
    "ABEV3.SA", "JBSS3.SA", "BRFS3.SA", "BEEF3.SA", "MGLU3.SA", "LREN3.SA", "ARZZ3.SA", "ASAI3.SA", "CRFB3.SA",
    # Saúde & Farmácias
    "RADL3.SA", "HYPE3.SA", "RDOR3.SA", "FLRY3.SA",
    # Telecomunicações & Tecnologia
    "VIVT3.SA", "TIMS3.SA", "TOTS3.SA"
]

CACHE_FILE = os.path.join(os.path.dirname(__file__), "market_cache.json")
CACHE_TTL_HOURS = 4

SECTOR_MAP = {
    "Financial Services": "Financeiro & Seguros",
    "Utilities": "Energia & Saneamento",
    "Basic Materials": "Materiais Básicos & Commodities",
    "Energy": "Petróleo & Gás",
    "Industrials": "Bens Industriais & Logística",
    "Consumer Cyclical": "Consumo Cíclico & Varejo",
    "Consumer Defensive": "Alimentos & Bebidas",
    "Healthcare": "Saúde & Farmácias",
    "Communication Services": "Telecomunicações",
    "Technology": "Tecnologia",
    "Real Estate": "Construção & Imobiliário"
}

def get_market_overview():
    """Retorna dados do Ibovespa e Dólar PTAX para o panorama geral."""
    indices = {
        "Ibovespa": "^BVSP",
        "Dólar (USD/BRL)": "USDBRL=X",
        "S&P 500": "^GSPC"
    }
    overview = {}
    for name, ticker_symbol in indices.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                pct_change = ((current_price - prev_price) / prev_price) * 100
                overview[name] = {
                    "price": float(current_price),
                    "change_pct": float(pct_change),
                    "prev_close": float(prev_price)
                }
            elif len(hist) == 1:
                overview[name] = {
                    "price": float(hist['Close'].iloc[-1]),
                    "change_pct": 0.0,
                    "prev_close": float(hist['Close'].iloc[-1])
                }
        except Exception as e:
            overview[name] = {"price": 0.0, "change_pct": 0.0, "error": str(e)}
    return overview

def fetch_single_ticker_data(symbol):
    """Obtém dados fundamentalistas e técnicos de um ticker individual com proventos reais."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        
        hist = ticker.history(period="1y")
        if hist.empty:
            return None

        current_price = float(hist['Close'].iloc[-1])
        if current_price <= 0:
            return None

        # Variação do dia
        pct_change = 0.0
        if len(hist) >= 2:
            prev_close = float(hist['Close'].iloc[-2])
            pct_change = ((current_price - prev_close) / prev_close) * 100

        # Médias Móveis
        ma_20 = float(hist['Close'].rolling(window=20).mean().iloc[-1]) if len(hist) >= 20 else current_price
        ma_200 = float(hist['Close'].rolling(window=200).mean().iloc[-1]) if len(hist) >= 200 else current_price

        # Dividendos reais nos últimos 12 meses
        dpa_12m = 0.0
        try:
            divs = ticker.dividends
            if not divs.empty:
                cutoff_date = pd.Timestamp.now(tz=divs.index.tz) - pd.DateOffset(years=1)
                dpa_12m = float(divs[divs.index >= cutoff_date].sum())
        except Exception:
            pass

        # Cálculo do Dividend Yield (%)
        if dpa_12m > 0 and current_price > 0:
            dy_val = (dpa_12m / current_price) * 100.0
        else:
            raw_dy = info.get("dividendYield")
            if raw_dy is not None:
                dy_val = float(raw_dy)
                if dy_val < 0.30:  # Ex: 0.08 vira 8.0%
                    dy_val *= 100.0
                dpa_12m = current_price * (dy_val / 100.0)
            else:
                dy_val = 0.0

        # Indicadores contábeis
        lpa = info.get("trailingEps")
        vpa = info.get("bookValue")
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")

        roe = info.get("returnOnEquity")
        roe_val = (float(roe) * 100.0) if roe is not None else 0.0

        profit_margins = info.get("profitMargins")
        margin_val = (float(profit_margins) * 100.0) if profit_margins is not None else 0.0

        ev_ebitda = info.get("enterpriseToEbitda")
        ev_ebitda_val = float(ev_ebitda) if ev_ebitda is not None else 0.0

        debt_to_equity = info.get("debtToEquity")
        debt_val = float(debt_to_equity) if debt_to_equity is not None else 0.0

        raw_sector = info.get("sector") or "Outro"
        sector_br = SECTOR_MAP.get(raw_sector, raw_sector)

        clean_code = symbol.replace(".SA", "")

        return {
            "symbol": symbol,
            "code": clean_code,
            "shortName": info.get("shortName") or clean_code,
            "sector": sector_br,
            "industry": info.get("industry") or "Geral",
            "price": round(float(current_price), 2),
            "change_pct": round(float(pct_change), 2),
            "ma_20": round(ma_20, 2),
            "ma_200": round(ma_200, 2),
            "pe": round(float(pe), 2) if pe else None,
            "pb": round(float(pb), 2) if pb else None,
            "dy": round(dy_val, 2),
            "dpa_12m": round(dpa_12m, 2),
            "roe": round(roe_val, 2),
            "margin_net": round(margin_val, 2),
            "lpa": round(float(lpa), 2) if lpa else None,
            "vpa": round(float(vpa), 2) if vpa else None,
            "ev_ebitda": round(ev_ebitda_val, 2) if ev_ebitda_val else None,
            "debt_to_equity": round(debt_val, 2),
            "market_cap": info.get("marketCap") or 0,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Erro ao buscar {symbol}: {e}")
        return None

def fetch_all_tickers(ticker_list=None, force_refresh=False):
    """Carrega dados de todos os tickers com suporte a cache local."""
    if ticker_list is None:
        ticker_list = DEFAULT_TICKERS

    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data.get("timestamp", "2000-01-01"))
                if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
                    return data.get("stocks", []), data.get("market_overview", {})
        except Exception:
            pass

    print(f"Atualizando base de {len(ticker_list)} ações da B3...")
    stocks = []
    for sym in ticker_list:
        data = fetch_single_ticker_data(sym)
        if data:
            stocks.append(data)
        time.sleep(0.02)

    market_ov = get_market_overview()

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "stocks": stocks,
                "market_overview": market_ov
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao gravar cache: {e}")

    return stocks, market_ov

def get_ticker_history(symbol, period="1y", interval="1d"):
    """Retorna histórico diário para gráficos em candlestick e médias móveis."""
    if not symbol.endswith(".SA") and not symbol.startswith("^"):
        symbol = f"{symbol}.SA"
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    if not df.empty:
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
    return df
