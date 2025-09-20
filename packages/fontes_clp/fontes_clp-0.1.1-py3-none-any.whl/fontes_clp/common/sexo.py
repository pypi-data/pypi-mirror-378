from enum import Enum

_nomes_sexos = {
    1: "Mulheres",
    2: "Homens",
    3: "Ambos",
}


class Sexo(Enum):
    F = 1
    M = 2
    AMBOS = 3

    def get_nome(self) -> str:
        return _nomes_sexos.get(self.value)

    def get_sigla(self) -> str:
        return self.name
