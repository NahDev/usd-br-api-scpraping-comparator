"""Casos de uso: orquestram coleta + persistência a partir das abstrações
de domínio, sem conhecer os detalhes de scraping ou API."""

import logging
from pathlib import Path
from typing import Dict, List

from src.domain.entities import CAMPOS_CSV_NOTICIAS, CotacaoCambio, DiaImpactante
from src.domain.exceptions import ColetaDadosError
from src.domain.repositories import FonteCotacaoCambio, RepositorioHistoricoCambio, RepositorioNoticias
from src.infrastructure.persistence.csv_writer import salvar_csv, salvar_csv_linhas

logger = logging.getLogger(__name__)


class ColetarCotacaoCambioUseCase:
    def __init__(self, fonte: FonteCotacaoCambio, caminho_saida: Path):
        self._fonte = fonte
        self._caminho_saida = caminho_saida

    def executar(self) -> List[CotacaoCambio]:
        logger.info("Iniciando coleta via %s", type(self._fonte).__name__)
        cotacoes = self._fonte.coletar()

        if not cotacoes:
            logger.warning("Nenhuma cotação foi coletada; CSV não será gerado.")
            return cotacoes

        salvar_csv(cotacoes, self._caminho_saida)
        logger.info("%d cotação(ões) salva(s) em %s", len(cotacoes), self._caminho_saida)
        return cotacoes


class CompararFontesCotacaoUseCase:
    """Coleta a mesma cotação de várias fontes e salva num CSV comparativo.
    Uma fonte que falhar é ignorada; as demais seguem normalmente."""

    def __init__(self, fontes: Dict[str, FonteCotacaoCambio], caminho_saida: Path):
        self._fontes = fontes
        self._caminho_saida = caminho_saida

    def executar(self) -> List[CotacaoCambio]:
        cotacoes: List[CotacaoCambio] = []
        for nome, fonte in self._fontes.items():
            logger.info("Coletando fonte '%s' (%s)", nome, type(fonte).__name__)
            try:
                cotacoes.extend(fonte.coletar())
            except ColetaDadosError as exc:
                logger.warning("Fonte '%s' falhou e será ignorada no comparativo: %s", nome, exc)

        if not cotacoes:
            logger.error("Nenhuma fonte retornou dados; comparativo não será gerado.")
            return cotacoes

        salvar_csv(cotacoes, self._caminho_saida)
        logger.info("Comparativo com %d registro(s) salvo em %s", len(cotacoes), self._caminho_saida)
        return cotacoes


class CorrelacionarNoticiasUseCase:
    """Identifica os dias de maior variação cambial e associa notícias
    publicadas nessas datas."""

    def __init__(
        self,
        repositorio_historico: RepositorioHistoricoCambio,
        repositorio_noticias: RepositorioNoticias,
        caminho_saida: Path,
        dias_historico: int = 30,
        top_n_dias: int = 5,
        noticias_por_dia: int = 3,
    ):
        self._repositorio_historico = repositorio_historico
        self._repositorio_noticias = repositorio_noticias
        self._caminho_saida = caminho_saida
        self._dias_historico = dias_historico
        self._top_n_dias = top_n_dias
        self._noticias_por_dia = noticias_por_dia

    def executar(self) -> List[DiaImpactante]:
        historico = self._repositorio_historico.obter_historico(self._dias_historico)
        maiores_variacoes = sorted(historico, key=lambda v: abs(v.variacao_percentual), reverse=True)
        maiores_variacoes = maiores_variacoes[: self._top_n_dias]

        datas = [variacao.data for variacao in maiores_variacoes]
        try:
            noticias_por_data = self._repositorio_noticias.buscar_noticias_por_dias(
                "dólar câmbio", datas, self._noticias_por_dia
            )
        except ColetaDadosError as exc:
            logger.warning("Falha ao buscar notícias; CSV será gerado sem elas: %s", exc)
            noticias_por_data = {}

        dias_impactantes = [
            DiaImpactante(
                data=variacao.data,
                variacao_percentual=variacao.variacao_percentual,
                valor_fechamento=variacao.valor_fechamento,
                noticias=noticias_por_data.get(variacao.data, []),
            )
            for variacao in maiores_variacoes
        ]

        linhas = [linha for dia in dias_impactantes for linha in dia.to_csv_rows()]
        salvar_csv_linhas(linhas, CAMPOS_CSV_NOTICIAS, self._caminho_saida)
        logger.info(
            "%d dia(s) de maior variação (%d linha(s) de notícia) salvo(s) em %s",
            len(dias_impactantes),
            len(linhas),
            self._caminho_saida,
        )
        return dias_impactantes
