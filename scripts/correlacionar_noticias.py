#!/usr/bin/env python3
"""Script bônus: identifica os dias de maior variação do USD/BRL (AwesomeAPI)
e associa notícias publicadas nessas datas (GDELT). Gera
data/dias_impactantes.csv.

Uso:
    python scripts/correlacionar_noticias.py [dias_historico] [top_n_dias]
"""

import logging
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROJETO))

from src.application.use_cases import CorrelacionarNoticiasUseCase 
from src.domain.exceptions import ColetaDadosError 
from src.infrastructure.api.awesome_api_historico_client import AwesomeApiHistoricoClient 
from src.infrastructure.api.gdelt_noticias_client import GdeltNoticiasClient 
from src.infrastructure.logging_config import configurar_logging 

CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "dias_impactantes.csv"
DIAS_HISTORICO_PADRAO = 30
TOP_N_PADRAO = 5


def _imprimir_resumo(dias_impactantes) -> None:
    print(f"\nOs {len(dias_impactantes)} dias de maior variação do USD/BRL")
    print("-" * 72)
    for dia in dias_impactantes:
        direcao = "ALTA " if dia.variacao_percentual >= 0 else "QUEDA"
        print(f"{dia.data}  [{direcao}] {dia.variacao_percentual:+.2f}%  (R$ {dia.valor_fechamento:.4f})")
        if dia.noticias:
            for noticia in dia.noticias:
                print(f"    · {noticia.titulo}  [{noticia.fonte}]")
        else:
            print("    · nenhuma notícia encontrada para esta data")
    print()


def main() -> int:
    configurar_logging()
    logger = logging.getLogger("correlacionar_noticias")

    dias_historico = int(sys.argv[1]) if len(sys.argv) > 1 else DIAS_HISTORICO_PADRAO
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else TOP_N_PADRAO

    caso_de_uso = CorrelacionarNoticiasUseCase(
        repositorio_historico=AwesomeApiHistoricoClient(),
        repositorio_noticias=GdeltNoticiasClient(),
        caminho_saida=CAMINHO_SAIDA,
        dias_historico=dias_historico,
        top_n_dias=top_n,
    )

    try:
        dias_impactantes = caso_de_uso.executar()
    except ColetaDadosError as exc:
        logger.error("Falha ao correlacionar notícias: %s", exc)
        return 1

    if not dias_impactantes:
        logger.error("Nenhum dia de variação foi identificado.")
        return 1

    _imprimir_resumo(dias_impactantes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
