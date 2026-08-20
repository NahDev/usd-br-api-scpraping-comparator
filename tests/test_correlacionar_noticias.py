from pathlib import Path
from typing import Dict, List

from src.application.use_cases import CorrelacionarNoticiasUseCase
from src.domain.entities import Noticia, VariacaoDiaria
from src.domain.exceptions import ColetaDadosError
from src.domain.repositories import RepositorioHistoricoCambio, RepositorioNoticias

HISTORICO = [
    VariacaoDiaria("2026-08-15", 5.10, 0.10),
    VariacaoDiaria("2026-08-16", 5.30, 3.50),  # maior variação
    VariacaoDiaria("2026-08-17", 5.20, -1.80),  # segunda maior variação
    VariacaoDiaria("2026-08-18", 5.15, -0.30),
]


class _RepositorioHistoricoFalso(RepositorioHistoricoCambio):
    def obter_historico(self, dias: int) -> List[VariacaoDiaria]:
        return HISTORICO


class _RepositorioNoticiasFalso(RepositorioNoticias):
    def __init__(self, respostas: Dict[str, List[Noticia]] = None, levantar_erro: bool = False):
        self._respostas = respostas or {}
        self._levantar_erro = levantar_erro
        self.datas_recebidas = None

    def buscar_noticias_por_dias(self, termo, datas, limite_por_dia):
        self.datas_recebidas = datas
        if self._levantar_erro:
            raise ColetaDadosError("falha simulada")
        return self._respostas


def test_seleciona_os_dias_de_maior_variacao_absoluta(tmp_path: Path):
    repo_noticias = _RepositorioNoticiasFalso()
    caso_de_uso = CorrelacionarNoticiasUseCase(
        _RepositorioHistoricoFalso(), repo_noticias, tmp_path / "saida.csv", top_n_dias=2
    )

    dias = caso_de_uso.executar()

    assert [d.data for d in dias] == ["2026-08-16", "2026-08-17"]
    assert sorted(repo_noticias.datas_recebidas) == ["2026-08-16", "2026-08-17"]


def test_associa_noticias_encontradas_ao_dia_correto(tmp_path: Path):
    noticia = Noticia("Manchete", "fonte.com", "https://fonte.com/x", "2026-08-16T12:00:00Z")
    repo_noticias = _RepositorioNoticiasFalso(respostas={"2026-08-16": [noticia]})
    caso_de_uso = CorrelacionarNoticiasUseCase(
        _RepositorioHistoricoFalso(), repo_noticias, tmp_path / "saida.csv", top_n_dias=2
    )

    dias = caso_de_uso.executar()

    dia_16 = next(d for d in dias if d.data == "2026-08-16")
    dia_17 = next(d for d in dias if d.data == "2026-08-17")
    assert dia_16.noticias == [noticia]
    assert dia_17.noticias == []


def test_csv_tem_uma_linha_mesmo_sem_noticias(tmp_path: Path):
    caminho = tmp_path / "saida.csv"
    caso_de_uso = CorrelacionarNoticiasUseCase(
        _RepositorioHistoricoFalso(), _RepositorioNoticiasFalso(), caminho, top_n_dias=1
    )

    caso_de_uso.executar()

    conteudo = caminho.read_text(encoding="utf-8")
    linhas = conteudo.strip().split("\n")
    assert len(linhas) == 2  # cabeçalho + 1 dia sem notícia


def test_falha_ao_buscar_noticias_nao_derruba_a_coleta(tmp_path: Path):
    repo_noticias = _RepositorioNoticiasFalso(levantar_erro=True)
    caso_de_uso = CorrelacionarNoticiasUseCase(
        _RepositorioHistoricoFalso(), repo_noticias, tmp_path / "saida.csv", top_n_dias=2
    )

    dias = caso_de_uso.executar()

    assert len(dias) == 2
    assert all(d.noticias == [] for d in dias)
