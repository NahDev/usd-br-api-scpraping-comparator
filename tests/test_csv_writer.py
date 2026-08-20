import csv
from datetime import datetime
from pathlib import Path

from src.domain.entities import CotacaoCambio
from src.infrastructure.persistence.csv_writer import salvar_csv


def _cotacao_exemplo() -> CotacaoCambio:
    return CotacaoCambio(
        moeda_base="USD",
        moeda_cotacao="BRL",
        valor_compra=5.10,
        valor_venda=5.12,
        fonte="teste",
        coletado_em=datetime(2026, 1, 1, 12, 0, 0),
        valor_alta=5.15,
        valor_baixa=5.05,
        variacao_percentual=0.5,
    )


def test_salvar_csv_gera_arquivo_com_cabecalho_e_dados(tmp_path: Path):
    caminho = tmp_path / "saida.csv"
    salvar_csv([_cotacao_exemplo()], caminho)

    assert caminho.exists()
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    assert len(linhas) == 1
    assert linhas[0]["par_moeda"] == "USD/BRL"
    assert linhas[0]["valor_compra"] == "5.1000"
    assert linhas[0]["fonte"] == "teste"


def test_salvar_csv_cria_diretorio_pai_se_nao_existir(tmp_path: Path):
    caminho = tmp_path / "subpasta" / "saida.csv"
    salvar_csv([_cotacao_exemplo()], caminho)
    assert caminho.exists()
