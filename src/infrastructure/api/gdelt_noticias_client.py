"""Busca notícias por data via GDELT Project DOC API (pública, sem chave).
Preferida a scraping do Google Notícias, cujo robots.txt desautoriza
explicitamente crawlers da Anthropic.

A API tem rate limit agressivo, então `buscar_noticias_por_dias` faz uma
única chamada cobrindo todo o período e agrupa os artigos por data
localmente, em vez de uma chamada por dia."""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

import requests

from src.domain.entities import Noticia
from src.domain.exceptions import BloqueioOuRestricaoError, ColetaDadosError, DadosInvalidosError
from src.domain.repositories import RepositorioNoticias
from src.infrastructure.http.http_client import criar_sessao

logger = logging.getLogger(__name__)

URL_PADRAO = "https://api.gdeltproject.org/api/v2/doc/doc"
TIMEOUT_SEGUNDOS = 30
MAX_REGISTROS = 250


class GdeltNoticiasClient(RepositorioNoticias):
    def __init__(self, url: str = URL_PADRAO, sessao: Optional[requests.Session] = None):
        self._url = url
        self._sessao = sessao or criar_sessao()

    def buscar_noticias_por_dias(
        self, termo: str, datas: List[str], limite_por_dia: int
    ) -> Dict[str, List[Noticia]]:
        if not datas:
            return {}

        data_inicio, data_fim = min(datas), max(datas)
        artigos_brutos = self._buscar_periodo(termo, data_inicio, data_fim)
        agrupado = self._agrupar_por_data(artigos_brutos)

        datas_pedidas = set(datas)
        return {
            data: noticias[:limite_por_dia]
            for data, noticias in agrupado.items()
            if data in datas_pedidas
        }

    def _buscar_periodo(self, termo: str, data_inicio: str, data_fim: str) -> list:
        params = {
            "query": f"({termo}) sourcelang:portuguese sourcecountry:Brazil",
            "mode": "artlist",
            "format": "json",
            "startdatetime": data_inicio.replace("-", "") + "000000",
            "enddatetime": data_fim.replace("-", "") + "235959",
            "maxrecords": MAX_REGISTROS,
            "sort": "hybridrel",
        }
        try:
            resposta = self._sessao.get(self._url, params=params, timeout=TIMEOUT_SEGUNDOS)
        except requests.exceptions.Timeout as exc:
            raise BloqueioOuRestricaoError(f"Timeout ao acessar {self._url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise ColetaDadosError(f"Falha de conexão ao acessar {self._url}: {exc}") from exc

        if resposta.status_code == 429:
            logger.warning("GDELT limitou a taxa de requisições (HTTP 429); nenhuma notícia será associada.")
            return []
        if resposta.status_code == 403:
            raise BloqueioOuRestricaoError(f"Acesso à API do GDELT bloqueado (HTTP {resposta.status_code}).")
        try:
            resposta.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise ColetaDadosError(f"Resposta HTTP inesperada de {self._url}: {exc}") from exc

        try:
            dados = resposta.json()
        except ValueError as exc:
            raise DadosInvalidosError(f"Resposta da API não é um JSON válido: {exc}") from exc

        return dados.get("articles", [])

    @staticmethod
    def _agrupar_por_data(artigos: list) -> Dict[str, List[Noticia]]:
        agrupado: Dict[str, List[Noticia]] = defaultdict(list)
        for artigo in artigos:
            try:
                data_iso = datetime.strptime(artigo["seendate"], "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")
                agrupado[data_iso].append(
                    Noticia(
                        titulo=artigo.get("title", "").strip(),
                        fonte=artigo.get("domain", ""),
                        link=artigo.get("url", ""),
                        publicado_em=artigo.get("seendate", ""),
                    )
                )
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning("Artigo em formato inesperado foi ignorado: %s", exc)
        return dict(agrupado)
