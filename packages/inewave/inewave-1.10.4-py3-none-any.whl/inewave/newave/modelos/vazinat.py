from cfinterface.components.section import Section
from cfinterface.components.line import Line
from cfinterface.components.floatfield import FloatField
from typing import IO
from datetime import datetime
from inewave.config import MAX_ANOS_HISTORICO
import pandas as pd  # type: ignore
import numpy as np  # type: ignore


class SecaoDadosVazinat(Section):
    """
    Registro com os dados das séries históricas de vazão incremental por
    configuração existentes no arquivo vazinat.dat.
    """

    __slots__ = ["__linha"]

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SecaoDadosVazinat):
            return False
        bloco: SecaoDadosVazinat = o
        if not all(
            [
                isinstance(self.data, pd.DataFrame),
                isinstance(o.data, pd.DataFrame),
            ]
        ):
            return False
        else:
            return self.data.equals(bloco.data)

    def read(
        self,
        file: IO,
        numero_uhes: int = 164,
        numero_configuracoes: int = 60,
        ano_inicio_historico: int = 1931,
        *args,
        **kwargs,
    ):
        numero_registros = (
            MAX_ANOS_HISTORICO * 12 * numero_uhes * numero_configuracoes
        )
        self.__linha = Line(
            [
                FloatField(size=8, starting_position=8 * i)
                for i in range(numero_registros)
            ],
            storage="BINARY",
        )
        dados = self.__linha.read(file.read(self.__linha.size))
        datas_df = pd.date_range(
            datetime(year=ano_inicio_historico, month=1, day=1),
            datetime(
                year=ano_inicio_historico + MAX_ANOS_HISTORICO - 1,
                month=12,
                day=1,
            ),
            freq="MS",
        ).to_numpy()
        datas_df = np.tile(datas_df, numero_uhes * numero_configuracoes)
        uhes_df = np.tile(
            np.repeat(np.arange(1, numero_uhes + 1), 12 * MAX_ANOS_HISTORICO),
            numero_configuracoes,
        )
        configuracoes_df = np.repeat(
            np.arange(1, numero_configuracoes + 1),
            12 * MAX_ANOS_HISTORICO * numero_uhes,
        )

        df = pd.DataFrame(
            data={
                "configuracao": configuracoes_df,
                "data": datas_df,
                "indice_usina": uhes_df,
                "valor": dados,
            }
        )
        self.data = df

    def write(self, file: IO, *args, **kwargs):
        dados = self.data["valor"].to_numpy()
        linha = Line(
            [
                FloatField(size=8, starting_position=8 * i)
                for i in range(len(dados))
            ],
            storage="BINARY",
        )
        file.write(linha.write(dados))
