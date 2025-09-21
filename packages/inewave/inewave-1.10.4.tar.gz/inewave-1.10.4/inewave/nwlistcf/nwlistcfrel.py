from inewave.nwlistcf.modelos.nwlistcfrel import CortesPeriodoNwlistcf

from cfinterface.files.blockfile import BlockFile
from typing import TypeVar, Optional
import pandas as pd  # type: ignore


class Nwlistcfrel(BlockFile):
    """
    Armazena os dados dos cortes construídos pelo NEWAVE existentes
    no arquivo `nwlistcf.rel` do NWLISTCF.

    Esta classe armazena os cortes da FCF de cada uma das variáveis,
    para cada registro e REE dentro do registro.

    """

    T = TypeVar("T")

    BLOCKS = [CortesPeriodoNwlistcf]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__cortes_periodos = None

    def __monta_tabela_cortes(self) -> pd.DataFrame:
        df = None
        for b in self.data.of_type(CortesPeriodoNwlistcf):
            dados = b.data
            if dados is None:
                continue
            elif df is None:
                df = b.data
            else:
                df = pd.concat([df, b.data], ignore_index=True)
        return df

    @property
    def cortes(self) -> Optional[pd.DataFrame]:
        """
        Tabela com os cortes da FCF.

        - PERIODO (`int`)
        - IREG (`int`)
        - REE ou UHE (`int`)
        - RHS (`int`)
        - PIV ou PIEARM (`int`)
        - PIH(1) (`float`)
        - ...
        - PIH(12) (`float`)
        - PIGTAD(P1L1) (`float`)
        - ...
        - PIGTAD(P3L2) (`float`)
        - PIMX_SAR (`float`)
        - PIMX_VMN (`float`)

        :return: A tabela de cortes como um DataFrame
        :rtype: pd.DataFrame | None
        """
        if self.__cortes_periodos is None:
            self.__cortes_periodos = self.__monta_tabela_cortes()
        return self.__cortes_periodos
