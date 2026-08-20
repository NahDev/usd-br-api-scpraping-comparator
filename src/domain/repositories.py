"""Portas do domínio: a camada de aplicação depende só destas abstrações,
nunca das implementações concretas de infraestrutura."""

from abc import ABC, abstractmethod
from typing import Dict, List

from src.domain.entities import CotacaoCambio, Noticia, VariacaoDiaria


class FonteCotacaoCambio(ABC):
    @abstractmethod
    def coletar(self) -> List[CotacaoCambio]:
        raise NotImplementedError


class RepositorioHistoricoCambio(ABC):
    @abstractmethod
    def obter_historico(self, dias: int) -> List[VariacaoDiaria]:
        raise NotImplementedError


class RepositorioNoticias(ABC):
    @abstractmethod
    def buscar_noticias_por_dias(
        self, termo: str, datas: List[str], limite_por_dia: int
    ) -> Dict[str, List[Noticia]]:
        raise NotImplementedError
