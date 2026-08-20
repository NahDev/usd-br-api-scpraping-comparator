import pytest

from src.domain.exceptions import DadosInvalidosError
from src.infrastructure.api.awesome_api_historico_client import AwesomeApiHistoricoClient

RESPOSTA_VALIDA = [
    {"bid": "5.1972", "pctChange": "0.355293", "timestamp": "1787235498"},
    {"bid": "5.1788", "pctChange": "-0.661773", "timestamp": "1787178605"},
]


def test_converter_com_resposta_valida():
    variacoes = AwesomeApiHistoricoClient._converter(RESPOSTA_VALIDA)
    assert len(variacoes) == 2
    assert variacoes[0].valor_fechamento == pytest.approx(5.1972)
    assert variacoes[0].variacao_percentual == pytest.approx(0.355293)
    assert variacoes[0].data  # data derivada do timestamp, não vazia


def test_converter_levanta_erro_com_lista_vazia():
    with pytest.raises(DadosInvalidosError):
        AwesomeApiHistoricoClient._converter([])


def test_converter_ignora_registro_malformado_mas_mantem_os_demais():
    resposta = [{"bid": "5.19"}, *RESPOSTA_VALIDA]  # primeiro item sem pctChange/timestamp
    variacoes = AwesomeApiHistoricoClient._converter(resposta)
    assert len(variacoes) == 2
