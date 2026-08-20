#!/usr/bin/env python3
"""Script bônus: roda scraping + API juntos e salva um CSV comparativo.

Uso:
    python scripts/comparar_cotacoes.py
"""

import logging
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROJETO))

from src.application.use_cases import CompararFontesCotacaoUseCase 
from src.infrastructure.api.awesome_api_client import AwesomeApiClient 
from src.infrastructure.logging_config import configurar_logging 
from src.infrastructure.scraping.melhor_cambio_scraper import MelhorCambioScraper 

CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "comparativo_cotacoes.csv"


def _imprimir_resumo(cotacoes) -> None:
    por_fonte = {c.fonte: c for c in cotacoes}
    scraping = next((c for c in cotacoes if c.fonte.startswith("scraping")), None)
    api = next((c for c in cotacoes if c.fonte.startswith("api")), None)

    print("\nResumo comparativo USD/BRL")
    print("-" * 40)
    for cotacao in cotacoes:
        print(f"{cotacao.fonte:<28} compra={cotacao.valor_compra:.4f}  venda={cotacao.valor_venda:.4f}")

    if scraping and api:
        valor_medio_api = (api.valor_compra + api.valor_venda) / 2
        diferenca = scraping.valor_compra - valor_medio_api
        diferenca_pct = (diferenca / valor_medio_api) * 100
        print("-" * 40)
        print(
            f"Diferença scraping vs. média da API: {diferenca:+.4f} "
            f"({diferenca_pct:+.2f}%)"
        )
    print()


def main() -> int:
    configurar_logging()
    logger = logging.getLogger("comparar_cotacoes")

    fontes = {
        "scraping": MelhorCambioScraper(),
        "api": AwesomeApiClient(),
    }
    caso_de_uso = CompararFontesCotacaoUseCase(fontes, CAMINHO_SAIDA)
    cotacoes = caso_de_uso.executar()

    if not cotacoes:
        logger.error("Nenhum dado coletado de nenhuma fonte.")
        return 1

    _imprimir_resumo(cotacoes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
