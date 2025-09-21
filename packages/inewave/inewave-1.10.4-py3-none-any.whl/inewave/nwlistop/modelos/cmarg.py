from cfinterface.components.floatfield import FloatField
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.line import Line

from inewave.config import MESES_DF
from inewave.nwlistop.modelos.blocos.valoresseriepatamar import (
    ValoresSeriePatamar,
)


class CmargsAnos27(ValoresSeriePatamar):
    """
    Bloco com a informaçao do submercado associado aos valores de Custo
    Marginal de Operação.
    """

    __slots__ = []

    HEADER_LINE = Line([IntegerField(4, 10)])
    DATA_LINE = Line(
        [  # type: ignore
            IntegerField(4, 2),
            IntegerField(2, 9),
        ]
        + [FloatField(8, 15 + 9 * i, 2) for i in range(len(MESES_DF))]  # type: ignore
    )


class CmargsAnos(ValoresSeriePatamar):
    """
    Bloco com a informaçao do submercado associado aos valores de Custo
    Marginal de Operação.
    """

    __slots__ = []

    HEADER_LINE = Line([IntegerField(4, 10)])
    DATA_LINE = Line(
        [  # type: ignore
            IntegerField(4, 2),
            IntegerField(2, 9),
        ]
        + [FloatField(11, 14 + 11 * i, 2) for i in range(len(MESES_DF))]  # type: ignore
    )
