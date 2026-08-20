import pytest

from src.domain.exceptions import DadosInvalidosError
from src.infrastructure.scraping.melhor_cambio_scraper import MelhorCambioScraper

HTML_VALIDO = """
<html><body>
<input type="text" value="5,17" class="text-verde" id="comercial" calc="sim">
</body></html>
"""

HTML_SEM_CAMPO = "<html><body><p>Página fora do ar</p></body></html>"


def test_extrair_valor_comercial_com_html_valido():
    valor = MelhorCambioScraper._extrair_valor_comercial(HTML_VALIDO)
    assert valor == pytest.approx(5.17)


def test_extrair_valor_comercial_levanta_erro_quando_campo_ausente():
    with pytest.raises(DadosInvalidosError):
        MelhorCambioScraper._extrair_valor_comercial(HTML_SEM_CAMPO)
