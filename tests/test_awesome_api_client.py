import pytest

from src.domain.exceptions import DadosInvalidosError
from src.infrastructure.api.awesome_api_client import AwesomeApiClient

RESPOSTA_VALIDA = {
    "USDBRL": {
        "code": "USD",
        "codein": "BRL",
        "bid": "5.1650",
        "ask": "5.1700",
        "high": "5.1750",
        "low": "5.1500",
        "pctChange": "0.10",
    }
}


def test_converter_com_resposta_valida():
    cotacao = AwesomeApiClient._converter(RESPOSTA_VALIDA)
    assert cotacao.moeda_base == "USD"
    assert cotacao.valor_compra == pytest.approx(5.1650)
    assert cotacao.valor_venda == pytest.approx(5.1700)


def test_converter_levanta_erro_quando_chave_ausente():
    with pytest.raises(DadosInvalidosError):
        AwesomeApiClient._converter({"OUTRAMOEDA": {}})


def test_converter_levanta_erro_quando_campo_obrigatorio_ausente():
    resposta_incompleta = {"USDBRL": {"code": "USD", "codein": "BRL"}}
    with pytest.raises(DadosInvalidosError):
        AwesomeApiClient._converter(resposta_incompleta)
