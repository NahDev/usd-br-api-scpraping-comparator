#!/usr/bin/env python3
"""Script 1 — Web Scraping.

Coleta a cotação do dólar comercial via scraping do site melhorcambio.com
e salva o resultado em data/cotacao_dolar_scraping.csv.

Uso:
    python scripts/coletar_scraping.py
"""

import logging
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROJETO))

from src.application.use_cases import ColetarCotacaoCambioUseCase 
from src.domain.exceptions import ColetaDadosError 
from src.infrastructure.logging_config import configurar_logging 
from src.infrastructure.scraping.melhor_cambio_scraper import MelhorCambioScraper 

CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "cotacao_dolar_scraping.csv"


def main() -> int:
    configurar_logging()
    logger = logging.getLogger("coletar_scraping")

    fonte = MelhorCambioScraper()
    caso_de_uso = ColetarCotacaoCambioUseCase(fonte, CAMINHO_SAIDA)

    try:
        cotacoes = caso_de_uso.executar()
    except ColetaDadosError as exc:
        logger.error("Falha na coleta via scraping: %s", exc)
        return 1

    for cotacao in cotacoes:
        logger.info(
            "%s/%s = %.4f (fonte: %s)",
            cotacao.moeda_base,
            cotacao.moeda_cotacao,
            cotacao.valor_compra,
            cotacao.fonte,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
