from inewave.config import MESES_DF

from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.floatfield import FloatField

from inewave.nwlistop.modelos.blocos.valoresseriepatamar import (
    ValoresSeriePatamar,
)


class HliqAnos(ValoresSeriePatamar):
    """
    Bloco com as informações das tabelas de queda líquida
    da usina por mês/ano de estudo.
    """

    __slots__ = []

    HEADER_LINE = Line([IntegerField(4, 10)])
    DATA_LINE = Line(
        [  # type: ignore
            IntegerField(4, 2),
            LiteralField(5, 6),
        ]
        + [FloatField(9, 14 + 9 * i, 2) for i in range(len(MESES_DF))]  # type: ignore
    )
