import pandas as pd
import importlib.resources as resources
from fontes_clp.common import Estado, Sexo


class IBGEPopulacao():
    """
    Os dados apresentados aqui foram retirados diretamente das projeções mais
    recentes do IBGE, disponíveis em https://www.ibge.gov.br/estatisticas/sociais/populacao/9109-projecao-da-populacao.html
    """

    ano: int
    estado: Estado
    sexo: Sexo

    def __init__(self, ano: int, estado: Estado, sexo: Sexo = Sexo.AMBOS):
        self.ano = ano
        self.estado = estado
        self.sexo = sexo

    def get_dados(self) -> pd.DataFrame:
        with resources.open_binary("fontes_clp.ibge.dados", "dados.xlsx") as f:
            df = pd.read_excel(f, header=4)
            df.columns = df.iloc[0]
            df = df[1:]

            df = df[df["SIGLA"] == self.estado.get_sigla()]
            df = df[df["SEXO"] == self.sexo.get_nome()]
            df = df[self.ano]

            valor = df.sum()

            return pd.DataFrame(
                [(
                    self.ano,
                    self.estado.get_sigla(),
                    self.sexo.get_sigla(),
                    valor,
                )],
                columns=[
                    "Ano",
                    "Estado",
                    "Sexo",
                    "Valor",
                ]
            )
