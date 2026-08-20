# Coleta de Cotação de Câmbio (USD/BRL) — Teste Btime Dev RPA

Dois scripts que coletam a cotação USD/BRL por técnicas diferentes — web
scraping e API pública — e salvam em CSV no mesmo formato. Mais dois
scripts bônus (comparativo e correlação com notícias) e um dashboard Flask
opcional.

## Arquitetura

Clean Architecture: `domain` (entidades e portas, sem dependências
externas) → `application` (casos de uso) → `infrastructure` (scraping,
API, HTTP, CSV).

```
src/
├── domain/          entities.py, repositories.py (portas), exceptions.py
├── application/      use_cases.py
└── infrastructure/
    ├── http/           sessão requests com retry/backoff
    ├── scraping/        melhor_cambio_scraper.py, robots_checker.py
    ├── api/             awesome_api_client.py, awesome_api_historico_client.py, gdelt_noticias_client.py
    └── persistence/     csv_writer.py

scripts/
├── coletar_scraping.py        Script 1 — scraping
├── coletar_api.py             Script 2 — API
├── comparar_cotacoes.py       bônus: roda as duas juntas
└── correlacionar_noticias.py  bônus: dias de maior variação + notícias

webapp/   dashboard Flask opcional (lê os CSVs, não é exigido pelo teste)
data/     CSVs gerados
tests/    pytest
```

`coletar_scraping.py` e `coletar_api.py` só escolhem qual implementação de
`FonteCotacaoCambio` usar — a lógica de salvar em CSV é compartilhada.

## Fontes de dados

| Script | Técnica | Fonte |
|---|---|---|
| `coletar_scraping.py` | Scraping (`requests` + `BeautifulSoup`) | melhorcambio.com |
| `coletar_api.py` | API pública | AwesomeAPI |
| `comparar_cotacoes.py` | Scraping + API | ambas acima |
| `correlacionar_noticias.py` | API + API | AwesomeAPI (histórico) + GDELT Project |

## CSV gerado

`coletar_scraping.py` e `coletar_api.py` geram o mesmo formato:

`coletado_em, fonte, par_moeda, valor_compra, valor_venda, valor_alta, valor_baixa, variacao_percentual`

O scraping só expõe um valor de referência (sem spread), então
`valor_compra` = `valor_venda` e alta/baixa/variação ficam vazios.

`dias_impactantes.csv` (bônus): `data, direcao, variacao_percentual,
valor_fechamento, titulo_noticia, fonte_noticia, link_noticia` — uma linha
por notícia; dias sem notícia geram uma linha com esses campos vazios.

## Robustez do scraping

- Verifica `robots.txt` antes de cada requisição, buscando com a mesma
  sessão/UA do scraper — `RobotFileParser.read()` usa um UA que o site
  bloqueia com 403, e nesse caso o parser assume "bloquear tudo"
- User-Agent de navegador, rotacionado
- Retry com backoff exponencial (429/500/502/503/504)
- Timeout obrigatório em toda requisição
- Trata 403/429 como bloqueio; valida a estrutura extraída do HTML

## Ciência de dados (bônus)

`correlacionar_noticias.py` busca o histórico diário do USD/BRL, pega os N
dias de maior variação absoluta e busca notícias publicadas nessas datas
via GDELT Project (API pública, sem chave — preferida a scraping do Google
Notícias, cujo robots.txt bloqueia crawlers da Anthropic). O GDELT tem rate
limit agressivo; se limitar, o script ainda gera o CSV, só sem notícias.

## Requisitos

Python 3.12+

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux/Mac: `source .venv/bin/activate` no lugar do `.venv\Scripts\activate`.

## Como executar

```bash
python scripts/coletar_scraping.py
python scripts/coletar_api.py
python scripts/comparar_cotacoes.py
python scripts/correlacionar_noticias.py [dias_historico] [top_n_dias]
```

## Interface (opcional)

```bash
python webapp/app.py
```

Abre em http://localhost:5001 — dashboard (`/`) e painel de robôs (`/robo`,
com botão para rodar cada script). Só lê os CSVs, não faz parte do teste.

## Testes

```bash
pytest
```

26 testes: parsing de scraping/API, casos de uso, geração de CSV e a
interface Flask (com `subprocess` mockado).
