import re
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from fontes_clp.common.estados import Estado
from fontes_clp.tabnet.grupos import GruposObitos

_tabnet_url = (
    "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sim/cnv/ext10uf.def;"
)


class TabNetObitos():
    ano: int
    estado: Estado
    grupo: GruposObitos

    def __init__(self, ano: int, estado: Estado, grupo: GruposObitos):
        self.ano = ano
        self.estado = estado
        self.grupo = grupo

    def _get_conteudo(self) -> str:
        if isinstance(self.grupo.value, range):
            grupo_valor = ""
            for grupo in self.grupo.value:
                grupo_valor += f"&SGrupo_CID10={grupo}"
        else:
            grupo_valor = f"&SGrupo_CID10={self.grupo.value}"

        return (
            "Linha=Unidade_da_Federa%E7%E3o"
            "&Coluna=Unidade_da_Federa%E7%E3o"
            "&Incremento=%D3bitos_p%2FOcorr%EAnc"
            f"&Arquivos=extuf{self.ano - 2000}.dbf"
            "&SRegi%E3o=TODAS_AS_CATEGORIAS__"
            "&pesqmes2=Digite+o+texto+e+ache+f%E1cil"
            f"&SUnidade_da_Federa%E7%E3o={self.estado.value}"
            "&SGrande_Grupo_CID10=TODAS_AS_CATEGORIAS__"
            "&pesqmes4=Digite+o+texto+e+ache+f%E1cil"
            f"{grupo_valor}"
            "&pesqmes5=Digite+o+texto+e+ache+f%E1cil"
            "&SCategoria_CID10=TODAS_AS_CATEGORIAS__"
            "&pesqmes6=Digite+o+texto+e+ache+f%E1cil"
            "&SFaixa_Et%E1ria=TODAS_AS_CATEGORIAS__"
            "&pesqmes7=Digite+o+texto+e+ache+f%E1cil"
            "&SFaixa_Et%E1ria_OPS=TODAS_AS_CATEGORIAS__"
            "&pesqmes8=Digite+o+texto+e+ache+f%E1cil"
            "&SFaixa_Et%E1ria_det=TODAS_AS_CATEGORIAS__"
            "&SFx.Et%E1ria_Menor_1A=TODAS_AS_CATEGORIAS__"
            "&SSexo=TODAS_AS_CATEGORIAS__"
            "&SCor%2Fra%E7a=TODAS_AS_CATEGORIAS__"
            "&SEscolaridade=TODAS_AS_CATEGORIAS__"
            "&SEstado_civil=TODAS_AS_CATEGORIAS__"
            "&SLocal_ocorr%EAncia=TODAS_AS_CATEGORIAS__"
            "&SAcid._Trabalho=TODAS_AS_CATEGORIAS__"
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
                match = re.search(r"((\d+)(\.\d+)?)+", str(el))
                if not match:
                    raise ValueError("Não foi possível encontrar o valor")

                nome_estado = re.findall(self.estado.get_nome(), el[0].text)
                if not nome_estado:
                    raise ValueError(
                        "Não foi possível encontrar o nome do estado"
                    )

                valor = int(match.group().replace(".", ""))
            else:
                valor = None

            return pd.DataFrame(
                [(
                    self.ano,
                    self.estado.get_sigla(),
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
