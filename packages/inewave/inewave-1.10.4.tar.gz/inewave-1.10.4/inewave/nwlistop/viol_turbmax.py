from inewave.nwlistop.modelos.blocos.usina import Usina
from inewave.nwlistop.modelos.arquivos.arquivousinapatamar import (
    ArquivoUsinaPatamar,
)
from inewave.nwlistop.modelos.viol_turbmax import ViolTurbmaxAnos


class ViolTurbmax(ArquivoUsinaPatamar):
    """
    Armazena os dados das saídas referentes à violação de restrição de
    turbinamento máximo por usina.

    Esta classe lida com as informações de saída fornecidas pelo
    NWLISTOP e reproduzidas nos `viol_turbmax00x.out`, onde x varia conforme
    a usina em questão.

    """

    BLOCKS = [
        Usina,
        ViolTurbmaxAnos,
    ]
