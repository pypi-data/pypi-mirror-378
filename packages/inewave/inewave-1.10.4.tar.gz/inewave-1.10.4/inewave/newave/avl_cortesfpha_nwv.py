from inewave.newave.modelos.blocos.versaomodelo import (
    VersaoModelo,
    VersaoModeloLibs,
)
from inewave.newave.modelos.avl_cortesfpha_nwv import (
    TabelaAvlCortesFpha28,
    TabelaAvlCortesFpha,
)

from inewave.newave.modelos.arquivoscsv.arquivocsv import ArquivoCSV
from typing import Optional
import pandas as pd  # type: ignore

from warnings import warn


class AvlCortesFpha(ArquivoCSV):
    """
    Arquivo com os cortes da função de produção para as UHEs
    do NEWAVE.
    """

    BLOCKS = [VersaoModeloLibs, TabelaAvlCortesFpha]
    VERSIONS = {
        "28": [VersaoModelo, TabelaAvlCortesFpha28],
        "28.16": [VersaoModeloLibs, TabelaAvlCortesFpha],
    }

    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        """
        A tabela de dados que está contida no arquivo.

        - codigo_usina (`int`)
        - periodo (`int`)
        - nome_usina (`str`)
        - indice_corte (`int`)
        - fator_correcao (`float`)
        - rhs_energia (`float`)
        - coeficiente_volume_util_MW_hm3 (`float`)
        - coeficiente_vazao_turbinada_MW_m3s (`float`)
        - coeficiente_vazao_vertida_MW_m3s (`float`)
        - coeficiente_vazao_lateral_MW_m3s (`float`)

        :return: A tabela como um dataframe
        :rtype: pd.DataFrame | None
        """
        return self._tabela()

    def __init__(self, data=...) -> None:
        warn(
            "Esta classe é relativa a um arquivo que não é mais suportado."
            + " Utilize a classe FphaCortes no lugar.",
            DeprecationWarning,
        )
        super().__init__(data)
