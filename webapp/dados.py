"""Carrega os CSVs já gerados pelos scripts de coleta e agrega os dados que
a interface exibe. Não faz nenhuma coleta nova — lê apenas o que já está em
data/, gerado por scripts/coletar_scraping.py, scripts/coletar_api.py,
scripts/comparar_cotacoes.py e scripts/correlacionar_noticias.py."""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SCRAPING = RAIZ_PROJETO / "data" / "cotacao_dolar_scraping.csv"
CAMINHO_API = RAIZ_PROJETO / "data" / "cotacao_dolar_api.csv"
CAMINHO_COMPARATIVO = RAIZ_PROJETO / "data" / "comparativo_cotacoes.csv"
CAMINHO_NOTICIAS = RAIZ_PROJETO / "data" / "dias_impactantes.csv"


def _ler_csv(caminho: Path) -> List[Dict[str, Any]]:
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def _ultima_linha(caminho: Path) -> Optional[Dict[str, Any]]:
    linhas = _ler_csv(caminho)
    return linhas[-1] if linhas else None


def carregar_cotacoes() -> Dict[str, Any]:
    scraping = _ultima_linha(CAMINHO_SCRAPING)
    api = _ultima_linha(CAMINHO_API)

    diferenca_pct = None
    if scraping and api:
        valor_scraping = float(scraping["valor_compra"])
        media_api = (float(api["valor_compra"]) + float(api["valor_venda"])) / 2
        if media_api:
            diferenca_pct = ((valor_scraping - media_api) / media_api) * 100

    return {"scraping": scraping, "api": api, "diferenca_percentual": diferenca_pct}


def carregar_dias_impactantes() -> List[Dict[str, Any]]:
    linhas = _ler_csv(CAMINHO_NOTICIAS)
    dias: Dict[str, Dict[str, Any]] = {}
    for linha in linhas:
        data = linha["data"]
        dia = dias.setdefault(
            data,
            {
                "data": data,
                "direcao": linha["direcao"],
                "variacao_percentual": float(linha["variacao_percentual"]),
                "valor_fechamento": float(linha["valor_fechamento"]),
                "noticias": [],
            },
        )
        if linha.get("titulo_noticia"):
            dia["noticias"].append(
                {
                    "titulo": linha["titulo_noticia"],
                    "fonte": linha["fonte_noticia"],
                    "link": linha["link_noticia"],
                }
            )
    return sorted(dias.values(), key=lambda d: abs(d["variacao_percentual"]), reverse=True)


def montar_dados() -> Dict[str, Any]:
    return {
        "cotacoes": carregar_cotacoes(),
        "dias_impactantes": carregar_dias_impactantes(),
    }
