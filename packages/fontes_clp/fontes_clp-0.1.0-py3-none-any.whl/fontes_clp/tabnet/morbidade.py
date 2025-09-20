import re
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from fontes_clp.common.estados import Estado
from fontes_clp.tabnet.grupos import GruposCausas

_tabnet_options_url = (
    "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/fruf.def"
)

_tabnet_url = (
    "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/fruf.def"
)


class TabNetMorbidades():
    ano: int
    mes: int
    estado: Estado
    grupo: GruposCausas

    def __init__(self, ano: int, estado: Estado, grupo: GruposCausas):
        self.ano = ano
        self.estado = estado
        self.grupo = grupo

    def _get_conteudo(self) -> str:
        with httpx.Client() as client:
            req = httpx.Request(
                "GET",
                _tabnet_options_url,
            )
            res = client.send(req, follow_redirects=True)
            soup = BeautifulSoup(res.text, features="html.parser")
            el = soup.select('select[name="Arquivos"]')
            options = el[0].find_all("option")

            values = []
            for option in options:
                value = option.get("value")
                if value:
                    values.append(value)

            arquivos = ""
            for mes in range(1, 13):
                arquivo = f"fruf{self.ano - 2000}{mes:02d}.dbf"

                if arquivo in values:
                    arquivos += f"&Arquivos={arquivo}"

            if isinstance(self.grupo.value, range):
                grupo_valor = ""
                for grupo in self.grupo.value:
                    grupo_valor += f"&SGrupo_de_Causas={grupo}"
            else:
                grupo_valor = f"&SGrupo_de_Causas={self.grupo.value}"

            return (
                "Linha=Unidade_da_Federa%E7%E3o"
                "&Coluna=Unidade_da_Federa%E7%E3o"
                "&Incremento=Interna%E7%F5es"
                f"{arquivos}"
                "&SRegi%E3o=TODAS_AS_CATEGORIAS__"
                "&pesqmes2=Digite+o+texto+e+ache+f%E1cil"
                "&SUnidade_da_Federa%E7%E3o=23"
                "&SCar%E1ter_atendimento=TODAS_AS_CATEGORIAS__"
                "&SRegime=TODAS_AS_CATEGORIAS__"
                "&pesqmes5=Digite+o+texto+e+ache+f%E1cil"
                "&SGrande_Grup_Causas=TODAS_AS_CATEGORIAS__"
                "&pesqmes6="
                f"{grupo_valor}"
                "&pesqmes7=Digite+o+texto+e+ache+f%E1cil"
                "&SCategorias_Causas=TODAS_AS_CATEGORIAS__"
                "&pesqmes8=Digite+o+texto+e+ache+f%E1cil"
                "&SFaixa_Et%E1ria_1=TODAS_AS_CATEGORIAS__"
                "&pesqmes9=Digite+o+texto+e+ache+f%E1cil"
                "&SFaixa_Et%E1ria_2=TODAS_AS_CATEGORIAS__"
                "&SSexo=TODAS_AS_CATEGORIAS__"
                "&SCor%2Fra%E7a=TODAS_AS_CATEGORIAS__"
                "&formato=table"
                "&mostre=Mostra"
            )

    def get_dados(self) -> pd.DataFrame:
        with httpx.Client() as client:
            req = httpx.Request(
                "POST",
                _tabnet_url,
                content=self._get_conteudo(),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            )
            res = client.send(req, follow_redirects=True)
            soup = BeautifulSoup(res.text, features="html.parser")
            el = soup.select('.tabdados tr > td[align="left"]')

            if el and len(el) != 0:
                match = re.search(r"\d+", str(el))
                if not match:
                    raise ValueError("Não foi possível encontrar o valor")

                nome_estado = re.findall(self.estado.get_nome(), el[0].text)
                if not nome_estado:
                    raise ValueError(
                        "Não foi possível encontrar o nome do estado"
                    )

                valor = int(match.group())
            else:
                valor = None

            return pd.DataFrame(
                [(
                    self.ano,
                    self.estado.name,
                    self.grupo.get_nome(),
                    valor,
                )],
                columns=[
                    "Ano",
                    "Estado",
                    "Grupo",
                    "Valor",
                ]
            )
