"""Escrita dos dados coletados em CSV."""

import csv
from pathlib import Path
from typing import Iterable, List

from src.domain.entities import CAMPOS_CSV, CotacaoCambio


def salvar_csv(cotacoes: Iterable[CotacaoCambio], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        for cotacao in cotacoes:
            escritor.writerow(cotacao.to_csv_row())


def salvar_csv_linhas(linhas: Iterable[dict], campos: List[str], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow(linha)
