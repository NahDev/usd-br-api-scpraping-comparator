from datetime import datetime
from pathlib import Path
from typing import List

from src.domain.entities import CotacaoCambio
from src.domain.exceptions import ColetaDadosError
from src.domain.repositories import FonteCotacaoCambio
from src.application.use_cases import CompararFontesCotacaoUseCase


class _FonteFalsaOk(FonteCotacaoCambio):
    def __init__(self, fonte: str, valor: float):
        self._fonte = fonte
        self._valor = valor

    def coletar(self) -> List[CotacaoCambio]:
        return [
            CotacaoCambio(
                moeda_base="USD",
                moeda_cotacao="BRL",
                valor_compra=self._valor,
                valor_venda=self._valor,
                fonte=self._fonte,
                coletado_em=datetime(2026, 1, 1, 12, 0, 0),
            )
        ]


class _FonteFalsaComFalha(FonteCotacaoCambio):
    def coletar(self) -> List[CotacaoCambio]:
        raise ColetaDadosError("fonte indisponível")


def test_comparar_fontes_consolida_resultados_de_todas_as_fontes(tmp_path: Path):
    fontes = {
        "scraping": _FonteFalsaOk("scraping:teste", 5.10),
        "api": _FonteFalsaOk("api:teste", 5.15),
    }
    caso_de_uso = CompararFontesCotacaoUseCase(fontes, tmp_path / "comparativo.csv")

    resultado = caso_de_uso.executar()

    assert len(resultado) == 2
    assert (tmp_path / "comparativo.csv").exists()


def test_comparar_fontes_ignora_fonte_com_falha_e_mantem_as_demais(tmp_path: Path):
    fontes = {
        "scraping": _FonteFalsaComFalha(),
        "api": _FonteFalsaOk("api:teste", 5.15),
    }
    caso_de_uso = CompararFontesCotacaoUseCase(fontes, tmp_path / "comparativo.csv")

    resultado = caso_de_uso.executar()

    assert len(resultado) == 1
    assert resultado[0].fonte == "api:teste"


def test_comparar_fontes_nao_gera_csv_quando_todas_as_fontes_falham(tmp_path: Path):
    fontes = {"scraping": _FonteFalsaComFalha(), "api": _FonteFalsaComFalha()}
    caminho = tmp_path / "comparativo.csv"
    caso_de_uso = CompararFontesCotacaoUseCase(fontes, caminho)

    resultado = caso_de_uso.executar()

    assert resultado == []
    assert not caminho.exists()
