# Rotinas de testes associadas ao arquivo cvar.dat do NEWAVE
from inewave.newave.modelos.cvar import (
    BlocoValoresConstantesCVAR,
    BlocoAlfaVariavelNoTempo,
    BlocoLambdaVariavelNoTempo,
)

from inewave.newave import Cvar


from tests.mocks.mock_open import mock_open
from unittest.mock import MagicMock, patch
from datetime import datetime
from tests.mocks.arquivos.cvar import (
    MockBlocoValoresConstantes,
    MockBlocoValoresAlfaVariaveis,
    MockBlocoValoresLambdaVariaveis,
    MockCVAR,
)

ARQ_TESTE = "./tests/mocks/arquivos/__init__.py"


def test_bloco_valores_constantes_cvar():
    m: MagicMock = mock_open(read_data="".join(MockBlocoValoresConstantes))
    b = BlocoValoresConstantesCVAR()
    with patch("builtins.open", m):
        with open("", "") as fp:
            b.read(fp)

    assert b.data == [50.0, 40.0]


def test_bloco_alfa_variavel_cvar():
    m: MagicMock = mock_open(read_data="".join(MockBlocoValoresAlfaVariaveis))
    b = BlocoAlfaVariavelNoTempo()
    with patch("builtins.open", m):
        with open("", "") as fp:
            b.read(fp)

    assert b.data.iloc[0, 0] == datetime(2017, 1, 1)
    assert b.data.iloc[-1, -1] == 5.0


def test_bloco_lambda_variavel_cvar():
    m: MagicMock = mock_open(
        read_data="".join(MockBlocoValoresLambdaVariaveis)
    )
    b = BlocoLambdaVariavelNoTempo()
    with patch("builtins.open", m):
        with open("", "") as fp:
            b.read(fp)

    assert b.data.iloc[0, 0] == datetime(2017, 1, 1)
    assert b.data.iloc[-1, -1] == 10.0


def test_atributos_encontrados_cvar():
    m: MagicMock = mock_open(read_data="".join(MockCVAR))
    with patch("builtins.open", m):
        ad = Cvar.read(ARQ_TESTE)
        assert ad.valores_constantes != [None, None]
        assert ad.alfa_variavel is not None
        assert ad.lambda_variavel is not None


def test_atributos_nao_encontrados_cvar():
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        ad = Cvar.read(ARQ_TESTE)
        assert ad.valores_constantes is None
        assert ad.alfa_variavel is None
        assert ad.lambda_variavel is None


def test_eq_cvar():
    m: MagicMock = mock_open(read_data="".join(MockCVAR))
    with patch("builtins.open", m):
        cf1 = Cvar.read(ARQ_TESTE)
        cf2 = Cvar.read(ARQ_TESTE)
        assert cf1 == cf2


def test_neq_cvar():
    m: MagicMock = mock_open(read_data="".join(MockCVAR))
    with patch("builtins.open", m):
        cf1 = Cvar.read(ARQ_TESTE)
        cf2 = Cvar.read(ARQ_TESTE)
        cf2.valores_constantes = [0, 0]
        assert cf1 != cf2


def test_leitura_escrita_cvar():
    m_leitura: MagicMock = mock_open(read_data="".join(MockCVAR))
    with patch("builtins.open", m_leitura):
        cf1 = Cvar.read(ARQ_TESTE)
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
        cf2 = Cvar.read(ARQ_TESTE)
        assert cf1 == cf2
