"""Coleta a cotação do dólar comercial via scraping do site melhorcambio.com.

O site só expõe um valor de referência, sem spread de compra/venda — por
isso valor_compra e valor_venda saem iguais."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from src.domain.entities import CotacaoCambio
from src.domain.exceptions import BloqueioOuRestricaoError, ColetaDadosError, DadosInvalidosError
from src.domain.repositories import FonteCotacaoCambio
from src.infrastructure.http.http_client import TIMEOUT_PADRAO_SEGUNDOS, criar_sessao
from src.infrastructure.scraping.robots_checker import pode_acessar

logger = logging.getLogger(__name__)

URL_PADRAO = "https://www.melhorcambio.com/dolar-hoje"


class MelhorCambioScraper(FonteCotacaoCambio):
    def __init__(self, url: str = URL_PADRAO, sessao: Optional[requests.Session] = None):
        self._url = url
        self._sessao = sessao or criar_sessao()

    def coletar(self) -> List[CotacaoCambio]:
        if not pode_acessar(self._url, self._sessao):
            raise BloqueioOuRestricaoError(
                f"robots.txt de {self._url} não permite acesso com o User-Agent atual."
            )

        html = self._buscar_html()
        valor = self._extrair_valor_comercial(html)

        cotacao = CotacaoCambio(
            moeda_base="USD",
            moeda_cotacao="BRL",
            valor_compra=valor,
            valor_venda=valor,
            fonte="scraping:melhorcambio.com",
            coletado_em=datetime.now(timezone.utc).astimezone(),
        )
        return [cotacao]

    def _buscar_html(self) -> str:
        try:
            resposta = self._sessao.get(self._url, timeout=TIMEOUT_PADRAO_SEGUNDOS)
        except requests.exceptions.Timeout as exc:
            raise BloqueioOuRestricaoError(f"Timeout ao acessar {self._url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise ColetaDadosError(f"Falha de conexão ao acessar {self._url}: {exc}") from exc

        if resposta.status_code in (403, 429):
            raise BloqueioOuRestricaoError(
                f"Acesso bloqueado pelo site (HTTP {resposta.status_code}). "
                "Possível bloqueio anti-bot ou rate limit."
            )
        try:
            resposta.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise ColetaDadosError(f"Resposta HTTP inesperada de {self._url}: {exc}") from exc

        return resposta.text

    @staticmethod
    def _extrair_valor_comercial(html: str) -> float:
        soup = BeautifulSoup(html, "html.parser")
        campo = soup.find("input", id="comercial")

        if campo is None or not campo.get("value"):
            raise DadosInvalidosError(
                "Campo de cotação comercial não encontrado na página. "
                "A estrutura do site pode ter mudado."
            )

        valor_bruto = campo["value"].strip()
        try:
            return float(valor_bruto.replace(".", "").replace(",", "."))
        except ValueError as exc:
            raise DadosInvalidosError(f"Valor de cotação em formato inesperado: {valor_bruto!r}") from exc
