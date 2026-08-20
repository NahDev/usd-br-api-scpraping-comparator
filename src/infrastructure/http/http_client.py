"""Sessão HTTP compartilhada: retry/backoff, User-Agent de navegador e
timeout padrão, reutilizada pelo scraper e pelos clientes de API."""

import random

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
]

TIMEOUT_PADRAO_SEGUNDOS = 15


def _escolher_user_agent() -> str:
    return random.choice(USER_AGENTS)


def criar_sessao(
    total_retries: int = 3,
    backoff_factor: float = 1.5,
    status_forcelist: tuple = (429, 500, 502, 503, 504),
) -> requests.Session:
    sessao = requests.Session()
    sessao.headers.update(
        {
            "User-Agent": _escolher_user_agent(),
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    )

    retry = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    sessao.mount("https://", adapter)
    sessao.mount("http://", adapter)
    return sessao
