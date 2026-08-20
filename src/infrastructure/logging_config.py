"""Configuração centralizada de logging para os scripts de coleta."""

import logging


def configurar_logging(nivel: int = logging.INFO) -> None:
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
