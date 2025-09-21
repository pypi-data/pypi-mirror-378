from inewave.nwlistop.modelos.blocos.estacaobombeamento import (
    EstacaoBombeamento,
)
from inewave.nwlistop.modelos.blocos.valoresseriepatamar import (
    ValoresSeriePatamar,
)

from cfinterface.files.blockfile import BlockFile
import pandas as pd  # type: ignore
from typing import TypeVar, Optional


class ArquivoEstacaoBombeamentoPatamar(BlockFile):
    """
    Armazena os dados das saídas por patamar, por Estação de Bombeamento.
    """

    __slots__ = ["__valores"]

    T = TypeVar("T")

    BLOCKS = [EstacaoBombeamento, ValoresSeriePatamar]

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
    def estacao(self) -> Optional[str]:
        """
        A estação associada ao arquivo lido.

        :return: O nome da estação
        :rtype: str
        """
        b = self.data.get_blocks_of_type(EstacaoBombeamento)
        if isinstance(b, EstacaoBombeamento):
            return b.data
        return None
