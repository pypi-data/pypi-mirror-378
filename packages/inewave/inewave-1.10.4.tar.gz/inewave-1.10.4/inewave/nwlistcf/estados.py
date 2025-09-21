from inewave.nwlistcf.modelos.estados import EstadosPeriodoNwlistcf

from cfinterface.files.blockfile import BlockFile
from typing import TypeVar, Optional
import pandas as pd  # type: ignore


class Estados(BlockFile):
    """
    Armazena os dados dos estados visitados pelo NEWAVE existentes
    no arquivo `estados.rel` do NWLISTCF.

    Esta classe armazena os estados de cada uma das variáveis envolvidas
    no problema e da função objetivo, para cada registro e REE dentro
    do registro.

    """

    T = TypeVar("T")

    BLOCKS = [EstadosPeriodoNwlistcf]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__estados_periodos = None

    def __monta_tabela_estados(self) -> pd.DataFrame:
        df = None
        for b in self.data.of_type(EstadosPeriodoNwlistcf):
            dados = b.data
            if dados is None:
                continue
            elif df is None:
                df = b.data
            else:
                df = pd.concat([df, b.data], ignore_index=True)
        return df

    @property
    def estados(self) -> Optional[pd.DataFrame]:
        """
        Tabela com os estados visitados na construção da FCF.

        - PERIODO (`int`)
        - IREG (`int`)
        - ITEc (`int`)
        - SIMc (`int`)
        - ITEf (`int`)
        - REE ou UHE (`int`)
        - FUNC. OBJ. (`float`)
        - EARM ou VARM (`float`)
        - EAF(1) ou VAF(1) (`float`)
        - ...
        - EAF(12) ou VAF(12) (`float`)
        - SGT(P1E1) (`float`)
        - ...
        - SGT(P3E3) (`float`)
        - MX_SAR (`float`)
        - MX_VMN ou MX_CURVA (`float`)

        :return: A tabela de estados como um DataFrame
        :rtype: pd.DataFrame | None
        """
        if self.__estados_periodos is None:
            self.__estados_periodos = self.__monta_tabela_estados()
        return self.__estados_periodos
