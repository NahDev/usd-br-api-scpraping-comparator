"""Verificação de robots.txt antes de fazer scraping.

Buscamos o arquivo com a mesma sessão/User-Agent do scraper em vez de usar
RobotFileParser.read(): ele usa o User-Agent genérico do urllib, que alguns
sites bloqueiam com 403 — e nesse caso o parser assume "bloquear tudo"."""

import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

logger = logging.getLogger(__name__)


def pode_acessar(url: str, sessao: requests.Session) -> bool:
    partes = urlparse(url)
    robots_url = f"{partes.scheme}://{partes.netloc}/robots.txt"
    parser = RobotFileParser()
    try:
        resposta = sessao.get(robots_url, timeout=10)
        if resposta.status_code >= 400:
            logger.warning(
                "robots.txt retornou HTTP %s em %s; assumindo acesso permitido.",
                resposta.status_code,
                robots_url,
            )
            return True
        parser.parse(resposta.text.splitlines())
    except requests.exceptions.RequestException as exc:
        logger.warning("Não foi possível obter %s (%s); assumindo acesso permitido.", robots_url, exc)
        return True
    return parser.can_fetch(sessao.headers.get("User-Agent", "*"), url)
