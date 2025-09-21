from datetime import datetime
from unittest.mock import MagicMock, patch

from inewave.nwlistop.cmarg import Cmarg
from tests.mocks.arquivos.cmarg import MockCmarg, MockCmarg27
from tests.mocks.mock_open import mock_open

ARQ_TESTE = "./tests/mocks/arquivos/__init__.py"


def test_atributos_encontrados_cmarg27():
    m: MagicMock = mock_open(read_data="".join(MockCmarg27))
    with patch("builtins.open", m):
        Cmarg.set_version("27")
        n = Cmarg.read(ARQ_TESTE)
        assert n.valores is not None
        assert n.valores.iloc[0, 0] == datetime(1995, 1, 1)
        assert n.valores.iloc[-1, -1] == 16.61
        assert n.submercado is not None
        assert n.submercado == "SUDESTE"


def test_atributos_encontrados_cmarg():
    m: MagicMock = mock_open(read_data="".join(MockCmarg))
    with patch("builtins.open", m):
        Cmarg.set_version("latest")
        n = Cmarg.read(ARQ_TESTE)
        assert n.valores is not None
        assert n.valores.iloc[0, 0] == datetime(2024, 1, 1)
        assert n.valores.iloc[-1, -1] == 76.75
        assert n.submercado is not None
        assert n.submercado == "SUDESTE"


def test_atributos_nao_encontrados_cmarg():
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        n = Cmarg.read(ARQ_TESTE)
        assert n.valores is None
        assert n.submercado is None


def test_eq_cmarg():
    m: MagicMock = mock_open(read_data="".join(MockCmarg))
    with patch("builtins.open", m):
        n1 = Cmarg.read(ARQ_TESTE)
        n2 = Cmarg.read(ARQ_TESTE)
        assert n1 == n2


# Não deve ter teste de diferença, visto que o atributo é
# implementado como Lazy Property.
