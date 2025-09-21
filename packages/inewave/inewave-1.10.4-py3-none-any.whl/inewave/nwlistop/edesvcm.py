from inewave.nwlistop.modelos.blocos.submercado import Submercado
from inewave.nwlistop.modelos.arquivos.arquivosubmercado import (
    ArquivoSubmercado,
)

from inewave.nwlistop.modelos.edesvcm import EdesvcmAnos


class Edesvcm(ArquivoSubmercado):
    """
    Armazena os dados das saídas referentes às energias
    de desvio de água controlável por submercado.

    Esta classe lida com as informações de saída fornecidas pelo
    NWLISTOP e reproduzidas nos `edesvcm00x.out`, onde x varia conforme o
    submercado em questão.

    """

    BLOCKS = [
        Submercado,
        EdesvcmAnos,
    ]
