from inewave.nwlistop.modelos.coper import CoperAnos

from inewave.nwlistop.modelos.arquivos.arquivosin import (
    ArquivoSIN,
)


class Coper(ArquivoSIN):
    """
    Armazena os dados das saídas referentes ao custo total de operação
    de cada estágio em cada série.

    Esta classe lida com as informações de saída fornecidas pelo
    NWLISTOP e reproduzidas nos `coper.out`.
    """

    BLOCKS = [
        CoperAnos,
    ]
