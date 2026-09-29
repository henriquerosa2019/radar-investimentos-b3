"""
Motor de Valuation e Modelos Quantitativos de Ações da B3.
Implementa os modelos de Benjamin Graham, Décio Bazin e Fórmula Mágica (Joel Greenblatt).
"""

import math
import pandas as pd

def calculate_graham_price(lpa, vpa):
    """
    Calcula o Valor Intrínseco de Benjamin Graham:
    V = sqrt(22.5 * LPA * VPA)
    Apenas válido se LPA > 0 e VPA > 0.
    """
    if lpa is not None and vpa is not None and lpa > 0 and vpa > 0:
        try:
            return round(math.sqrt(22.5 * lpa * vpa), 2)
        except Exception:
            return None
    return None

def calculate_bazin_price(current_price, dy_pct, dpa=None, min_yield=6.0):
    """
    Calcula o Preço Teto pelo método Décio Bazin:
    Preço Teto = DPA / (min_yield / 100)
    Se dpa fornecido, utiliza diretamente. Caso contrário calcula por DY%.
    """
    effective_dpa = dpa
    if (effective_dpa is None or effective_dpa <= 0) and current_price and current_price > 0 and dy_pct and dy_pct > 0:
        effective_dpa = current_price * (dy_pct / 100.0)

    if effective_dpa and effective_dpa > 0 and min_yield > 0:
        teto = effective_dpa / (min_yield / 100.0)
        return round(teto, 2)
    return None

def apply_valuation_models(stocks_data):
    """
    Aplica os modelos de Graham, Bazin e Greenblatt à lista de ações.
    Retorna uma lista enriquecida com preços-teto, margens de segurança e rankings.
    """
    enriched = []
    
    for s in stocks_data:
        item = s.copy()
        price = item.get("price", 0)
        lpa = item.get("lpa")
        vpa = item.get("vpa")
        dy = item.get("dy", 0)
        dpa = item.get("dpa_12m")
        pe = item.get("pe")
        roe = item.get("roe", 0)

        # 1. Graham
        graham_val = calculate_graham_price(lpa, vpa)
        item["graham_price"] = graham_val
        if graham_val and price > 0:
            graham_margin = ((graham_val - price) / price) * 100.0
            item["graham_margin"] = round(graham_margin, 2)
        else:
            item["graham_margin"] = None

        # 2. Bazin
        bazin_val = calculate_bazin_price(price, dy, dpa=dpa, min_yield=6.0)
        item["bazin_price"] = bazin_val
        if bazin_val and price > 0:
            bazin_margin = ((bazin_val - price) / price) * 100.0
            item["bazin_margin"] = round(bazin_margin, 2)
        else:
            item["bazin_margin"] = None

        # 3. Proventos Anuais
        if dpa and dpa > 0:
            item["estimated_dpa"] = round(dpa, 2)
        elif price > 0 and dy > 0:
            item["estimated_dpa"] = round(price * (dy / 100.0), 2)
        else:
            item["estimated_dpa"] = 0.0

        # Classificação Inicial
        tags = []
        if dy >= 6.0:
            tags.append("Alto DY")
        if item["graham_margin"] and item["graham_margin"] > 20:
            tags.append("Desconto Graham")
        if roe >= 15.0:
            tags.append("Alto ROE")
        if pe and pe > 0 and pe < 10:
            tags.append("P/L Baixo")

        item["tags"] = tags
        enriched.append(item)

    # 4. Fórmula Mágica de Joel Greenblatt
    df = pd.DataFrame(enriched)
    if not df.empty:
        # Preço: menor P/L positivo
        df["rank_price_metric"] = df["pe"].apply(lambda x: x if (x and x > 0) else 9999)
        df["price_rank"] = df["rank_price_metric"].rank(ascending=True)

        # Qualidade: maior ROE
        df["quality_rank"] = df["roe"].rank(ascending=False)

        # Rank Mágico Combinado
        df["magic_formula_score"] = df["price_rank"] + df["quality_rank"]
        df["magic_rank"] = df["magic_formula_score"].rank(ascending=True).astype(int)

        # Status visual
        def determine_status(row):
            g_margin = row.get("graham_margin")
            dy_val = row.get("dy", 0)
            
            if g_margin is not None and g_margin > 20 and dy_val >= 6:
                return "🟢 Forte Oportunidade"
            elif (g_margin is not None and g_margin > 10) or dy_val >= 6:
                return "🟢 Atrativa"
            elif g_margin is not None and g_margin >= -10:
                return "🟡 Preço Justo"
            else:
                return "🔴 Esticada / Cautela"

        df["status"] = df.apply(determine_status, axis=1)
        return df.to_dict(orient="records")

    return enriched
