from pathlib import Path

import webapp.dados as dados


def _preparar_cotacoes(tmp_path: Path, monkeypatch):
    cabecalho = "coletado_em,fonte,par_moeda,valor_compra,valor_venda,valor_alta,valor_baixa,variacao_percentual\n"
    scraping = tmp_path / "scraping.csv"
    scraping.write_text(
        cabecalho + "2026-08-20 12:00:00,scraping:melhorcambio.com,USD/BRL,5.1900,5.1900,,,\n", encoding="utf-8"
    )
    api = tmp_path / "api.csv"
    api.write_text(
        cabecalho + "2026-08-20 12:00:00,api:awesomeapi.com.br,USD/BRL,5.1000,5.1100,5.20,5.05,0.30\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(dados, "CAMINHO_SCRAPING", scraping)
    monkeypatch.setattr(dados, "CAMINHO_API", api)


def test_carregar_cotacoes_calcula_diferenca_percentual(tmp_path: Path, monkeypatch):
    _preparar_cotacoes(tmp_path, monkeypatch)

    resultado = dados.carregar_cotacoes()

    media_api = (5.1000 + 5.1100) / 2
    esperado = ((5.1900 - media_api) / media_api) * 100
    assert resultado["diferenca_percentual"] == esperado


def test_carregar_cotacoes_sem_arquivos_retorna_none(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(dados, "CAMINHO_SCRAPING", tmp_path / "nao_existe.csv")
    monkeypatch.setattr(dados, "CAMINHO_API", tmp_path / "tambem_nao_existe.csv")

    resultado = dados.carregar_cotacoes()

    assert resultado["scraping"] is None
    assert resultado["api"] is None
    assert resultado["diferenca_percentual"] is None


def test_carregar_dias_impactantes_agrupa_noticias_por_data(tmp_path: Path, monkeypatch):
    caminho = tmp_path / "noticias.csv"
    caminho.write_text(
        "data,direcao,variacao_percentual,valor_fechamento,titulo_noticia,fonte_noticia,link_noticia\n"
        "2026-08-11,alta,0.99,5.1573,Manchete 1,g1.globo.com,https://g1.globo.com/1\n"
        "2026-08-11,alta,0.99,5.1573,Manchete 2,infomoney.com.br,https://infomoney.com.br/2\n"
        "2026-07-30,queda,-1.50,5.0774,,,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(dados, "CAMINHO_NOTICIAS", caminho)

    dias = dados.carregar_dias_impactantes()

    assert len(dias) == 2
    # ordenado pela maior variação absoluta primeiro
    assert dias[0]["data"] == "2026-07-30"
    assert len(dias[0]["noticias"]) == 0
    dia_11 = next(d for d in dias if d["data"] == "2026-08-11")
    assert len(dia_11["noticias"]) == 2
    assert dia_11["noticias"][0]["titulo"] == "Manchete 1"
