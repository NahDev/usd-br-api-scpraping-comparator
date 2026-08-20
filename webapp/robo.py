"""Executa os scripts do projeto sob demanda e guarda status/log de cada um,
em thread separada para não travar a interface."""

import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
TIMEOUT_SEGUNDOS = 600
LINHAS_DE_LOG_MANTIDAS = 30

ROBOS: Dict[str, Dict[str, Any]] = {
    "scraping": {
        "nome": "Script 1 — Scraping",
        "descricao": "Raspa a cotação do dólar comercial em melhorcambio.com.",
        "script": RAIZ_PROJETO / "scripts" / "coletar_scraping.py",
        "arquivo_saida": RAIZ_PROJETO / "data" / "cotacao_dolar_scraping.csv",
    },
    "api": {
        "nome": "Script 2 — API",
        "descricao": "Busca a cotação do dólar na API pública AwesomeAPI.",
        "script": RAIZ_PROJETO / "scripts" / "coletar_api.py",
        "arquivo_saida": RAIZ_PROJETO / "data" / "cotacao_dolar_api.csv",
    },
    "comparar": {
        "nome": "Comparativo",
        "descricao": "Roda scraping + API juntos e compara os dois valores.",
        "script": RAIZ_PROJETO / "scripts" / "comparar_cotacoes.py",
        "arquivo_saida": RAIZ_PROJETO / "data" / "comparativo_cotacoes.csv",
    },
    "noticias": {
        "nome": "Ciência de dados",
        "descricao": "Identifica os dias de maior variação do dólar e associa notícias (GDELT).",
        "script": RAIZ_PROJETO / "scripts" / "correlacionar_noticias.py",
        "arquivo_saida": RAIZ_PROJETO / "data" / "dias_impactantes.csv",
    },
}

_lock = threading.Lock()


def _estado_ocioso() -> Dict[str, Any]:
    return {"status": "ocioso", "iniciado_em": None, "duracao_segundos": None, "codigo_saida": None, "log": []}


_estado: Dict[str, Dict[str, Any]] = {robo_id: _estado_ocioso() for robo_id in ROBOS}


def listar_status() -> List[Dict[str, Any]]:
    with _lock:
        resultado = []
        for robo_id, config in ROBOS.items():
            item = dict(_estado[robo_id])
            item["id"] = robo_id
            item["nome"] = config["nome"]
            item["descricao"] = config["descricao"]
            caminho = config["arquivo_saida"]
            item["arquivo_existe"] = caminho.exists()
            item["arquivo_atualizado_em"] = (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(caminho.stat().st_mtime))
                if caminho.exists()
                else None
            )
            resultado.append(item)
        return resultado


def rodar(robo_id: str, executar_em_thread: bool = True) -> bool:
    """Retorna False se o robô já estiver rodando."""
    if robo_id not in ROBOS:
        raise KeyError(robo_id)

    with _lock:
        if _estado[robo_id]["status"] == "rodando":
            return False
        _estado[robo_id] = {
            "status": "rodando",
            "iniciado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duracao_segundos": None,
            "codigo_saida": None,
            "log": [],
        }

    if executar_em_thread:
        threading.Thread(target=_executar, args=(robo_id,), daemon=True).start()
    else:
        _executar(robo_id)
    return True


def _executar(robo_id: str) -> None:
    config = ROBOS[robo_id]
    inicio = time.time()
    try:
        processo = subprocess.run(
            [sys.executable, str(config["script"])],
            cwd=str(RAIZ_PROJETO),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SEGUNDOS,
        )
        saida = (processo.stdout + processo.stderr).splitlines()
        codigo = processo.returncode
    except subprocess.TimeoutExpired:
        saida = [f"Tempo limite de {TIMEOUT_SEGUNDOS}s excedido."]
        codigo = -1
    except OSError as exc:
        saida = [f"Falha ao iniciar o processo: {exc}"]
        codigo = -1

    with _lock:
        iniciado_em = _estado[robo_id]["iniciado_em"]
        _estado[robo_id] = {
            "status": "sucesso" if codigo == 0 else "erro",
            "iniciado_em": iniciado_em,
            "duracao_segundos": round(time.time() - inicio, 1),
            "codigo_saida": codigo,
            "log": saida[-LINHAS_DE_LOG_MANTIDAS:],
        }
