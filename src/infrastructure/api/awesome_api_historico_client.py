"""Coleta o histórico de fechamento diário do dólar via API AwesomeAPI
(endpoint "daily"). A data de cada registro vem do campo "timestamp", já
que nem todo item traz "create_date"."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import requests

from src.domain.entities import VariacaoDiaria
from src.domain.exceptions import BloqueioOuRestricaoError, ColetaDadosError, DadosInvalidosError
from src.domain.repositories import RepositorioHistoricoCambio
from src.infrastructure.http.http_client import TIMEOUT_PADRAO_SEGUNDOS, criar_sessao

logger = logging.getLogger(__name__)

URL_BASE = "https://economia.awesomeapi.com.br/json/daily/USD-BRL"


class AwesomeApiHistoricoClient(RepositorioHistoricoCambio):
    def __init__(self, url_base: str = URL_BASE, sessao: Optional[requests.Session] = None):
        self._url_base = url_base
        self._sessao = sessao or criar_sessao()

    def obter_historico(self, dias: int) -> List[VariacaoDiaria]:
        url = f"{self._url_base}/{dias}"
        try:
            resposta = self._sessao.get(url, timeout=TIMEOUT_PADRAO_SEGUNDOS)
        except requests.exceptions.Timeout as exc:
            raise BloqueioOuRestricaoError(f"Timeout ao acessar {url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise ColetaDadosError(f"Falha de conexão ao acessar {url}: {exc}") from exc

        if resposta.status_code in (403, 429):
            raise BloqueioOuRestricaoError(f"Acesso à API bloqueado ou limitado (HTTP {resposta.status_code}).")
        try:
            resposta.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise ColetaDadosError(f"Resposta HTTP inesperada de {url}: {exc}") from exc

        try:
            dados = resposta.json()
        except ValueError as exc:
            raise DadosInvalidosError(f"Resposta da API não é um JSON válido: {exc}") from exc

        return self._converter(dados)

    @staticmethod
    def _converter(dados: list) -> List[VariacaoDiaria]:
        if not isinstance(dados, list) or not dados:
            raise DadosInvalidosError("API do histórico não retornou uma lista de cotações.")

        variacoes = []
        for item in dados:
            try:
                data_str = datetime.fromtimestamp(int(item["timestamp"]), tz=timezone.utc).strftime("%Y-%m-%d")
                variacoes.append(
                    VariacaoDiaria(
                        data=data_str,
                        valor_fechamento=float(item["bid"]),
                        variacao_percentual=float(item["pctChange"]),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Registro de histórico em formato inesperado foi ignorado: %s", exc)

        if not variacoes:
            raise DadosInvalidosError("Nenhum registro de histórico pôde ser processado.")
        return variacoes
