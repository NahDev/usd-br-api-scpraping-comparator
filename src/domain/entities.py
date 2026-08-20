"""Entidades do domínio, sem dependência de infraestrutura."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class CotacaoCambio:
    moeda_base: str
    moeda_cotacao: str
    valor_compra: float
    valor_venda: float
    fonte: str
    coletado_em: datetime
    valor_alta: Optional[float] = None
    valor_baixa: Optional[float] = None
    variacao_percentual: Optional[float] = None

    def to_csv_row(self) -> dict:
        return {
            "coletado_em": self.coletado_em.strftime("%Y-%m-%d %H:%M:%S"),
            "fonte": self.fonte,
            "par_moeda": f"{self.moeda_base}/{self.moeda_cotacao}",
            "valor_compra": f"{self.valor_compra:.4f}",
            "valor_venda": f"{self.valor_venda:.4f}",
            "valor_alta": f"{self.valor_alta:.4f}" if self.valor_alta is not None else "",
            "valor_baixa": f"{self.valor_baixa:.4f}" if self.valor_baixa is not None else "",
            "variacao_percentual": (
                f"{self.variacao_percentual:.2f}" if self.variacao_percentual is not None else ""
            ),
        }


CAMPOS_CSV = [
    "coletado_em",
    "fonte",
    "par_moeda",
    "valor_compra",
    "valor_venda",
    "valor_alta",
    "valor_baixa",
    "variacao_percentual",
]


@dataclass(frozen=True)
class VariacaoDiaria:
    data: str
    valor_fechamento: float
    variacao_percentual: float


@dataclass(frozen=True)
class Noticia:
    titulo: str
    fonte: str
    link: str
    publicado_em: str


@dataclass(frozen=True)
class DiaImpactante:
    data: str
    variacao_percentual: float
    valor_fechamento: float
    noticias: List[Noticia]

    def to_csv_rows(self) -> List[dict]:
        direcao = "alta" if self.variacao_percentual >= 0 else "queda"
        base = {
            "data": self.data,
            "direcao": direcao,
            "variacao_percentual": f"{self.variacao_percentual:.2f}",
            "valor_fechamento": f"{self.valor_fechamento:.4f}",
        }
        if not self.noticias:
            return [{**base, "titulo_noticia": "", "fonte_noticia": "", "link_noticia": ""}]
        return [
            {**base, "titulo_noticia": n.titulo, "fonte_noticia": n.fonte, "link_noticia": n.link}
            for n in self.noticias
        ]


CAMPOS_CSV_NOTICIAS = [
    "data",
    "direcao",
    "variacao_percentual",
    "valor_fechamento",
    "titulo_noticia",
    "fonte_noticia",
    "link_noticia",
]
