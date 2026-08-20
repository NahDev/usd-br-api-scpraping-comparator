#!/usr/bin/env python3
"""Script 2 — API pública.

Coleta a cotação do dólar via API pública AwesomeAPI e salva o resultado em
data/cotacao_dolar_api.csv, no mesmo formato usado pelo script de scraping.

Uso:
    python scripts/coletar_api.py
"""

import logging
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROJETO))

from src.application.use_cases import ColetarCotacaoCambioUseCase 
from src.domain.exceptions import ColetaDadosError 
from src.infrastructure.api.awesome_api_client import AwesomeApiClient 
from src.infrastructure.logging_config import configurar_logging 

CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "cotacao_dolar_api.csv"


def main() -> int:
    configurar_logging()
    logger = logging.getLogger("coletar_api")

    fonte = AwesomeApiClient()
    caso_de_uso = ColetarCotacaoCambioUseCase(fonte, CAMINHO_SAIDA)

    try:
        cotacoes = caso_de_uso.executar()
    except ColetaDadosError as exc:
        logger.error("Falha na coleta via API: %s", exc)
        return 1

    for cotacao in cotacoes:
        logger.info(
            "%s/%s compra=%.4f venda=%.4f (fonte: %s)",
            cotacao.moeda_base,
            cotacao.moeda_cotacao,
            cotacao.valor_compra,
            cotacao.valor_venda,
            cotacao.fonte,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
