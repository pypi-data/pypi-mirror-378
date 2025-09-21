# Rotinas de testes associadas ao arquivo vazpast.dat do NEWAVE
from inewave.newave.modelos.vazpast import BlocoVazPast

from inewave.newave import Vazpast


from tests.mocks.mock_open import mock_open
from unittest.mock import MagicMock, patch

from tests.mocks.arquivos.vazpast import MockBlocoVazoesPassadas

ARQ_TESTE = "./tests/mocks/arquivos/__init__.py"


def test_bloco_desvios_vazpast():
    m: MagicMock = mock_open(read_data="".join(MockBlocoVazoesPassadas))
    b = BlocoVazPast()
    with patch("builtins.open", m):
        with open("", "") as fp:
            b.read(fp)

    assert b.data.shape[0] == 2604
    assert b.data.iloc[0, 0] == 1
    assert b.data.iloc[-1, -1] == 20.0


def test_atributos_encontrados_vazpast():
    m: MagicMock = mock_open(read_data="".join(MockBlocoVazoesPassadas))
    with patch("builtins.open", m):
        ad = Vazpast.read(ARQ_TESTE)
        assert ad.tendencia is not None


def test_atributos_nao_encontrados_vazpast():
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        ad = Vazpast.read(ARQ_TESTE)
        assert ad.tendencia is None


def test_eq_vazpast():
    m: MagicMock = mock_open(read_data="".join(MockBlocoVazoesPassadas))
    with patch("builtins.open", m):
        cf1 = Vazpast.read(ARQ_TESTE)
        cf2 = Vazpast.read(ARQ_TESTE)
        assert cf1 == cf2


def test_neq_vazpast():
    m: MagicMock = mock_open(read_data="".join(MockBlocoVazoesPassadas))
    with patch("builtins.open", m):
        cf1 = Vazpast.read(ARQ_TESTE)
        cf2 = Vazpast.read(ARQ_TESTE)
        cf2.tendencia.iloc[0, 0] = -1
        assert cf1 != cf2


def test_leitura_escrita_vazpast():
    m_leitura: MagicMock = mock_open(
        read_data="".join(MockBlocoVazoesPassadas)
    )
    with patch("builtins.open", m_leitura):
        cf1 = Vazpast.read(ARQ_TESTE)
    m_escrita: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m_escrita):
        cf1.write(ARQ_TESTE)
        # Recupera o que foi escrito
        chamadas = m_escrita.mock_calls
        linhas_escritas = [
            chamadas[i].args[0] for i in range(1, len(chamadas) - 1)
        ]
    m_releitura: MagicMock = mock_open(read_data="".join(linhas_escritas))
    with patch("builtins.open", m_releitura):
        cf2 = Vazpast.read(ARQ_TESTE)
        assert cf1 == cf2
