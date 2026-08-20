from src.infrastructure.api.gdelt_noticias_client import GdeltNoticiasClient

ARTIGOS_BRUTOS = [
    {
        "title": "Dólar cai fecha a R$ 5,17",
        "domain": "g1.globo.com",
        "url": "https://g1.globo.com/noticia1",
        "seendate": "20260819T120020Z",
    },
    {
        "title": "Ibovespa sobe e dólar recua",
        "domain": "infomoney.com.br",
        "url": "https://infomoney.com.br/noticia2",
        "seendate": "20260819T150000Z",
    },
    {
        "title": "Dólar sobe com tensão nos EUA",
        "domain": "valor.globo.com",
        "url": "https://valor.globo.com/noticia3",
        "seendate": "20260818T090000Z",
    },
]


def test_agrupar_por_data_junta_artigos_do_mesmo_dia():
    agrupado = GdeltNoticiasClient._agrupar_por_data(ARTIGOS_BRUTOS)
    assert len(agrupado["2026-08-19"]) == 2
    assert len(agrupado["2026-08-18"]) == 1
    assert agrupado["2026-08-19"][0].titulo == "Dólar cai fecha a R$ 5,17"
    assert agrupado["2026-08-19"][0].fonte == "g1.globo.com"


def test_agrupar_por_data_ignora_artigo_sem_data_valida():
    artigos = [*ARTIGOS_BRUTOS, {"title": "sem data", "domain": "x.com", "url": "https://x.com"}]
    agrupado = GdeltNoticiasClient._agrupar_por_data(artigos)
    total = sum(len(v) for v in agrupado.values())
    assert total == 3  # o artigo malformado foi descartado, não quebrou o agrupamento
