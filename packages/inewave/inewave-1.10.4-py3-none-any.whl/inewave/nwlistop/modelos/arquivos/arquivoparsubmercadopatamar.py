from inewave.nwlistop.modelos.blocos.parsubmercados import ParSubmercados
from inewave.nwlistop.modelos.blocos.valoresseriepatamar import (
    ValoresSeriePatamar,
)

from cfinterface.files.blockfile import BlockFile
import pandas as pd  # type: ignore
from typing import TypeVar, Optional


class ArquivoParSubmercadoPatamar(BlockFile):
    """
    Armazena os dados das saídas por patamar, por par de submercados.
    """

    __slots__ = ["__valores"]

    T = TypeVar("T")

    BLOCKS = [ParSubmercados, ValoresSeriePatamar]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__valores = None

    def __monta_tabela(self) -> pd.DataFrame:
        df = None
        for b in self.data.of_type(ValoresSeriePatamar):
            dados = b.data
            if dados is None:
                continue
            elif df is None:
                df = b.data
            else:
                df = pd.concat([df, b.data], ignore_index=True)
        return df

    @property
    def valores(self) -> Optional[pd.DataFrame]:
        """
        Tabela com os valores por patamar, por série e
        por mês/ano de estudo.

        - data (`datetime`)
        - patamar (`str`)
        - serie (`str`)
        - valor (`float`)

        :return: A tabela dos valores por patamar.
        :rtype: pd.DataFrame | None
        """
        if self.__valores is None:
            self.__valores = self.__monta_tabela()
        return self.__valores

    @property
    def submercado_de(self) -> Optional[str]:
        """
        O submercado de origem associado ao arquivo lido.

        :return: Os nome do submercado
        :rtype: str
        """
        b = self.data.get_blocks_of_type(ParSubmercados)
        if isinstance(b, ParSubmercados):
            return b.data[0]
        return None

    @property
    def submercado_para(self) -> Optional[str]:
        """
        O submercado de destino associado ao arquivo lido.

        :return: Os nome do submercado
        :rtype: str
        """
        b = self.data.get_blocks_of_type(ParSubmercados)
        if isinstance(b, ParSubmercados):
            return b.data[1]
        return None
