"""Exceções de domínio. Erros de infraestrutura são sempre traduzidos para
estas antes de subir para a camada de aplicação."""


class ColetaDadosError(Exception):
    pass


class BloqueioOuRestricaoError(ColetaDadosError):
    pass


class DadosInvalidosError(ColetaDadosError):
    pass
