import subprocess

import pytest

import webapp.robo as robo


@pytest.fixture(autouse=True)
def estado_limpo():
    """Reseta o estado do robô de teste ("scraping") antes de cada teste,
    para que a ordem de execução dos testes não interfira entre si."""
    robo._estado["scraping"] = robo._estado_ocioso()
    yield
    robo._estado["scraping"] = robo._estado_ocioso()


def test_rodar_com_sucesso_atualiza_status(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(robo.subprocess, "run", fake_run)

    iniciado = robo.rodar("scraping", executar_em_thread=False)

    assert iniciado is True
    item = next(e for e in robo.listar_status() if e["id"] == "scraping")
    assert item["status"] == "sucesso"
    assert item["codigo_saida"] == 0
    assert "ok" in item["log"]


def test_rodar_com_falha_marca_status_erro(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, returncode=1, stdout="", stderr="deu ruim\n")

    monkeypatch.setattr(robo.subprocess, "run", fake_run)

    robo.rodar("scraping", executar_em_thread=False)

    item = next(e for e in robo.listar_status() if e["id"] == "scraping")
    assert item["status"] == "erro"
    assert "deu ruim" in item["log"]


def test_rodar_nao_inicia_de_novo_se_ja_esta_rodando():
    robo._estado["scraping"]["status"] = "rodando"

    iniciado = robo.rodar("scraping", executar_em_thread=False)

    assert iniciado is False


def test_rodar_com_id_desconhecido_levanta_key_error():
    with pytest.raises(KeyError):
        robo.rodar("robo-que-nao-existe", executar_em_thread=False)
