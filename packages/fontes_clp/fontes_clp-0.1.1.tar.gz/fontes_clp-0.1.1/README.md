# Bibliotecas para Extração de Fontes do CLP

## TabNet Óbitos

```sh
uv add fontes-clp
```

```python
from fontes_clp import Estado
from fontes_clp import TabNetObitos as TabNet
from fontes_clp import GruposCID10ObitosPorCausasExternas as GrupoCID10

# Dados são retornados como um DataFrame do Pandas
dados = TabNet(
  ano=2023,
  estado=Estado.RR,
  grupo_cid10=GrupoCID10.ACIDENTES_TERRESTRES,
).get_dados()

print(dados)
```
