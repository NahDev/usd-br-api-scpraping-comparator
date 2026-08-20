"""Coleta a cotação do dólar via API pública AwesomeAPI (sem chave)."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import requests

from src.domain.entities import CotacaoCambio
from src.domain.exceptions import BloqueioOuRestricaoError, ColetaDadosError, DadosInvalidosError
from src.domain.repositories import FonteCotacaoCambio
from src.infrastructure.http.http_client import TIMEOUT_PADRAO_SEGUNDOS, criar_sessao

logger = logging.getLogger(__name__)

URL_PADRAO = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
CHAVE_RESPOSTA = "USDBRL"


class AwesomeApiClient(FonteCotacaoCambio):
    def __init__(self, url: str = URL_PADRAO, sessao: Optional[requests.Session] = None):
        self._url = url
        self._sessao = sessao or criar_sessao()

    def coletar(self) -> List[CotacaoCambio]:
        dados = self._buscar_json()
        cotacao = self._converter(dados)
        return [cotacao]

    def _buscar_json(self) -> dict:
        try:
            resposta = self._sessao.get(self._url, timeout=TIMEOUT_PADRAO_SEGUNDOS)
        except requests.exceptions.Timeout as exc:
            raise BloqueioOuRestricaoError(f"Timeout ao acessar {self._url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise ColetaDadosError(f"Falha de conexão ao acessar {self._url}: {exc}") from exc

        if resposta.status_code in (403, 429):
            raise BloqueioOuRestricaoError(
                f"Acesso à API bloqueado ou limitado (HTTP {resposta.status_code})."
            )
        try:
            resposta.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise ColetaDadosError(f"Resposta HTTP inesperada de {self._url}: {exc}") from exc

        try:
            return resposta.json()
        except ValueError as exc:
            raise DadosInvalidosError(f"Resposta da API não é um JSON válido: {exc}") from exc

    @staticmethod
    def _converter(dados: dict) -> CotacaoCambio:
        if CHAVE_RESPOSTA not in dados:
            raise DadosInvalidosError(
                f"Campo '{CHAVE_RESPOSTA}' ausente na resposta da API. "
                "O contrato da API pode ter mudado."
            )
        item = dados[CHAVE_RESPOSTA]
        try:
            return CotacaoCambio(
                moeda_base=item.get("code", "USD"),
                moeda_cotacao=item.get("codein", "BRL"),
                valor_compra=float(item["bid"]),
                valor_venda=float(item["ask"]),
                valor_alta=float(item["high"]),
                valor_baixa=float(item["low"]),
                variacao_percentual=float(item["pctChange"]),
                fonte="api:awesomeapi.com.br",
                coletado_em=datetime.now(timezone.utc).astimezone(),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise DadosInvalidosError(f"Campo ausente ou em formato inesperado na resposta da API: {exc}") from exc
