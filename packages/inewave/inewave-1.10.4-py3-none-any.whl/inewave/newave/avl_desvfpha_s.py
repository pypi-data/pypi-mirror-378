from inewave.newave.modelos.blocos.versaomodelo import VersaoModelo
from inewave.newave.modelos.avl_desvfpha_s import TabelaAvlDesvFphaS

from cfinterface.files.blockfile import BlockFile
from typing import Optional, TypeVar
import pandas as pd  # type: ignore

from warnings import warn


class AvlDesvFphaS(BlockFile):
    """
    Arquivo com os desvios da função de produção no plano de
    vazão vertida (S).
    """

    BLOCKS = [VersaoModelo, TabelaAvlDesvFphaS]
    ENCODING = "iso-8859-1"

    T = TypeVar("T")

    def __init__(self, data=...) -> None:
        warn(
            "Esta classe é relativa a um arquivo que não é mais suportado."
            + " Utilize a classe FphaAvlDesvS no lugar.",
            DeprecationWarning,
        )
        super().__init__(data)
        self.__df_completo: Optional[pd.DataFrame] = None

    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        """
        A tabela de dados que está contida no arquivo.

        - codigo_usina (`int`)
        - nome_usina (`str`)
        - volume_armazenado_percentual (`float`)
        - vazao_turbinada_m3s (`float`)
        - vazao_vertida_m3s (`float`)
        - desvio_percentual (`float`)

        :return: A tabela como um dataframe
        :rtype: pd.DataFrame | None
        """
        if self.__df_completo is None:
            tabelas = self.data.of_type(TabelaAvlDesvFphaS)
            self.__df_completo = pd.DataFrame()
            for t in tabelas:
                self.__df_completo = pd.concat(
                    [self.__df_completo, t.data], ignore_index=True
                )
        return self.__df_completo

    @property
    def versao(self) -> Optional[str]:
        """
        A versão do modelo utilizada para executar o caso.

        :return: A versão do modelo
        :rtype: str | None
        """
        b = self.data.get_blocks_of_type(VersaoModelo)
        if isinstance(b, VersaoModelo):
            return b.data
        return None
