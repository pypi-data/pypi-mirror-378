from inewave.newave.modelos.parp import BlocoSerieEnergiaREE
from inewave.newave.modelos.parp import BlocoCorrelEnergiasREE
from inewave.newave.modelos.parp import BlocoCorrelParcialEnergiasREE
from inewave.newave.modelos.parp import BlocoOrdemModeloREE
from inewave.newave.modelos.parp import BlocoCoeficientesModeloREE
from inewave.newave.modelos.parp import BlocoSerieRuidosREE
from inewave.newave.modelos.parp import BlocoCorrelRuidosREE
from inewave.newave.modelos.parp import BlocoSerieMediasREE
from inewave.newave.modelos.parp import BlocoCorrelCruzadaMediaREE
from inewave.newave.modelos.parp import BlocoCorrelEspacialAnualConfig
from inewave.newave.modelos.parp import BlocoCorrelEspacialMensalConfig

from cfinterface.components.block import Block
from cfinterface.files.blockfile import BlockFile
from typing import Type, TypeVar, Optional, Any, List
import pandas as pd  # type: ignore
from datetime import datetime


class Parp(BlockFile):
    """
    Armazena os dados de saída do NEWAVE referentes aos modelos e às
    séries sintéticas de energia geradas pelo PAR(p).


    Esta classe lida com informações de saída do NEWAVE e
    cujas saídas devem ser compatíveis com as observadas através
    do NWLISTOP.

    """

    T = TypeVar("T")

    BLOCKS = [
        BlocoSerieEnergiaREE,
        BlocoCorrelEnergiasREE,
        BlocoCorrelParcialEnergiasREE,
        BlocoOrdemModeloREE,
        BlocoCoeficientesModeloREE,
        BlocoSerieRuidosREE,
        BlocoCorrelRuidosREE,
        BlocoSerieMediasREE,
        BlocoCorrelCruzadaMediaREE,
        BlocoCorrelEspacialAnualConfig,
        BlocoCorrelEspacialMensalConfig,
    ]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__series_energia = None
        self.__correl_series_energia = None
        self.__correl_parcial_series_energia = None
        self.__series_ruido = None
        self.__correl_series_ruido = None
        self.__series_media = None
        self.__correl_cruzada_media = None
        self.__ordem_original_modelo = None
        self.__ordem_final_modelo = None
        self.__coeficientes = None
        self.__correl_espacial_anual = None
        self.__correl_espacial_mensal = None

    def __rees(self) -> Optional[List[str]]:
        """
        Retorna a lista dos REEs lidos do arquivo.

        :return: Os nomes dos REEs
        :rtype: List[str]
        """
        if self.series_energia_ree is None:
            return None
        else:
            return self.series_energia_ree["ree"].unique().tolist()

    def __concatena_dados(self, bloco: Type[Block]) -> Optional[Any]:
        """
        Obtém os dados de um bloco se este existir dentre os blocos do arquivo.

        :param bloco: O tipo do bloco cujos dados serão extraídos
        :type bloco: Type[T]
        :param indice: Qual dos blocos do tipo será acessado
        :type indice: int, optional
        :return: Os dados do bloco, se existirem
        :rtype: Any
        """
        dados = pd.DataFrame()
        for b in self.data.of_type(bloco):
            if dados.empty:
                dados = b.data
            else:
                dados = pd.concat([dados, b.data], ignore_index=True)
        if not dados.empty:
            return dados
        else:
            return None

    def __adiciona_coluna_ree(
        self, df: Optional[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        """
        Adiciona uma coluna com os REEs de cada amostra, assumindo
        a mesma ordem das séries de energia.

        :param df: O DataFrame que irá receber os REEs
        :type df: pd.DataFrame
        :return: O DataFrame com os REEs
        :rtype: pd.DataFrame
        """
        if df is None:
            return None
        rees = self.__rees()
        if rees is None:
            return None
        linhas_por_ree = df.shape[0] / len(rees)
        if int(linhas_por_ree) != linhas_por_ree:
            raise ValueError(
                f"{df.shape[0]} linhas não podem ser "
                + f"divididas em {len(rees)} grupos"
            )
        cols = list(df.columns)
        col_ree: List[str] = []
        for ree in rees:
            col_ree += [ree] * int(linhas_por_ree)
        df["ree"] = col_ree
        return df[["ree"] + cols]

    def __adiciona_coluna_ree_com_estagios(
        self, df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Adiciona uma coluna com os REEs de cada amostra e outra
        com o estágio de cada uma, assumindo
        a mesma ordem das séries de energia.

        :param df: O DataFrame que irá receber os REEs
        :type df: pd.DataFrame
        :return: O DataFrame com os REEs
        :rtype: pd.DataFrame
        """
        rees = self.__rees()
        if rees is None:
            return None
        linhas_por_ree = df.shape[0] / len(rees)
        if int(linhas_por_ree) != linhas_por_ree:
            raise ValueError(
                f"{df.shape[0]} linhas não podem ser "
                + f"divididas em {len(rees)} grupos"
            )
        cols = list(df.columns)
        col_ree: List[str] = []
        col_estagio: List[int] = []
        for ree in rees:
            col_ree += [ree] * int(linhas_por_ree)
            col_estagio += list(range(1, int(linhas_por_ree) + 1))
        df["ree"] = col_ree
        df["estagio"] = col_estagio
        return df[["ree", "estagio"] + cols]

    def __adiciona_coluna_ree_corrigindo_pre_pos(
        self, df: Optional[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        """
        Adiciona uma coluna com os REEs de cada amostra e outra
        com o estágio de cada uma, assumindo
        a mesma ordem das séries de energia, e corrigindo os valores
        dos anos se houve períodos PRE e POS.

        :param df: O DataFrame que irá receber os REEs
        :type df: pd.DataFrame
        :return: O DataFrame com os REEs
        :rtype: pd.DataFrame
        """

        def converte_vetor_anos(anos: List[str], n: int) -> List[int]:
            # Descobre os anos pré e pós estudo
            numero_anos_pre = len([p for p in anos if p == "PRE"]) // n
            numero_anos_pos = len([p for p in anos if p == "POS"]) // n
            anos_estudo = [int(p) for p in anos if p not in ["PRE", "POS"]]
            # Descobre o primeiro ano de estudo
            primeiro_ano_estudo = sorted(anos_estudo)[0]
            # Descobre o último ano de estudo
            ultimo_ano_estudo = sorted(anos_estudo)[-1]
            indice_inicio_pos = anos.index("POS")
            # Substitui os anos pré e pós pelos valores específicos
            for a in range(numero_anos_pre):
                idx_i = n * a
                idx_f = idx_i + n
                ano = primeiro_ano_estudo - (numero_anos_pre - a)
                anos[idx_i:idx_f] = [str(ano)] * n
            for a in range(numero_anos_pos):
                idx_i = indice_inicio_pos + n * a
                idx_f = idx_i + n
                ano = ultimo_ano_estudo + a + 1
                anos[idx_i:idx_f] = [str(ano)] * n
            return [int(a) for a in anos]

        if df is None:
            return None
        rees = self.__rees()
        if rees is None:
            return None
        linhas_por_ree = df.shape[0] / len(rees)
        if int(linhas_por_ree) != linhas_por_ree:
            raise ValueError(
                f"{df.shape[0]} linhas não podem ser "
                + f"divididas em {len(rees)} grupos"
            )
        cols = list(df.columns)
        col_ree: List[str] = []
        for ree in rees:
            col_ree += [ree] * int(linhas_por_ree)
        df["ree"] = col_ree
        ree0 = rees[0]
        ano0 = df["ano"].unique().tolist()[0]
        filtro = (df["ano"] == ano0) & (df["ree"] == ree0)
        n_series = df.loc[filtro].shape[0]
        for i, ree in enumerate(rees):
            i_i = i * int(linhas_por_ree)
            i_f = i_i + int(linhas_por_ree) - 1
            df.loc[i_i:i_f, "ano"] = converte_vetor_anos(
                df.loc[i_i:i_f, "ano"].tolist(), n_series
            )
        return df[["ree"] + cols]

    def __converte_ano_mes_data(
        self, df: Optional[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        """
        Converte um dataframe com colunas `mes` e `ano` para um com
        uma coluna `data`.

        :param df: O DataFrame com colunas `mes` e `ano`
        :type df: pd.DataFrame
        :return: O DataFrame com coluna `data`
        :rtype: pd.DataFrame
        """
        if df is None:
            return None
        cols_identificacao = [
            c for c in df.columns if c not in ["valor", "ano", "mes"]
        ]
        df.loc[:, "data"] = df.apply(
            lambda linha: datetime(
                year=linha["ano"], month=linha["mes"], day=1
            ),
            axis=1,
        )
        return df.drop(columns=["ano", "mes"])[
            cols_identificacao + ["data", "valor"]
        ]

    @property
    def series_energia_ree(self) -> Optional[pd.DataFrame]:
        """
        A tabela de séries de energia para todas as configurações
        e REEs, no mesmo formato do arquivo `parp.dat`.

        - ree (`str`)
        - configuracao (`int`)
        - data (`datetime`)
        - valor (`float`)

        :return: A tabela como um DataFrame.
        :rtype: pd.DataFrame | None
        """
        if self.__series_energia is None:
            self.__series_energia = self.__concatena_dados(
                BlocoSerieEnergiaREE
            )
        return self.__series_energia

    @property
    def series_ruido_ree(self) -> Optional[pd.DataFrame]:
        """
        A tabela de séries de ruído para todos os REEs,
        no mesmo formato do arquivo `parp.dat`.

        - ree (`str`)
        - serie (`int`)
        - data (`datetime`)
        - valor (`float`)

        :return: A tabela como um DataFrame.
        :rtype: pd.DataFrame | None
        """
        if self.__series_ruido is None:
            self.__series_ruido = self.__concatena_dados(BlocoSerieRuidosREE)
            self.__series_ruido = (
                self.__adiciona_coluna_ree_corrigindo_pre_pos(
                    self.__series_ruido
                )
            )
            self.__series_ruido = self.__converte_ano_mes_data(
                self.__series_ruido
            )
        return self.__series_ruido

    @property
    def series_media_ree(self) -> Optional[pd.DataFrame]:
        """
        A tabela de séries de médias para todos os REEs,
        no mesmo formato do arquivo `parp.dat`.

        - ree (`str`)
        - serie (`int`)
        - data (`datetime`)
        - valor (`float`)

        :return: A tabela como um DataFrame.
        :rtype: pd.DataFrame | None
        """
        if self.__series_media is None:
            self.__series_media = self.__concatena_dados(BlocoSerieMediasREE)
            self.__series_media = (
                self.__adiciona_coluna_ree_corrigindo_pre_pos(
                    self.__series_media
                )
            )
            self.__series_media = self.__converte_ano_mes_data(
                self.__series_media
            )
        return self.__series_media

    @property
    def correlacao_series_energia_ree(self) -> Optional[pd.DataFrame]:
        """
        A tabela de correlação das séries de energia para
        todas as configurações vigentes e REEs,
        no mesmo formato do arquivo `parp.dat`.

        - ree (`str`)
        - data (`datetime`)
        - lag (`int`)
        - valor (`float`)

        :return: A tabela como um DataFrame
        :rtype: pd.DataFrame | None
        """
        if self.__correl_series_energia is None:
            self.__correl_series_energia = self.__concatena_dados(
                BlocoCorrelEnergiasREE
            )
            self.__correl_series_energia = self.__adiciona_coluna_ree(
                self.__correl_series_energia
            )
        return self.__correl_series_energia

    @property
    def correlacao_parcial_series_energia_ree(self) -> Optional[pd.DataFrame]:
        """
        A tabela de correlação parcial das séries de energia para
        todas as configurações vigentes e REEs,
        no mesmo formato do arquivo `parp.dat`.

        - ree (`str`)
        - data (`datetime`)
        - lag (`int`)
        - valor (`float`)

        :return: A tabela como um DataFrame
        :rtype: pd.DataFrame | None
        """
        if self.__correl_parcial_series_energia is None:
            self.__correl_parcial_series_energia = self.__concatena_dados(
                BlocoCorrelParcialEnergiasREE
            )
            self.__correl_parcial_series_energia = self.__adiciona_coluna_ree(
                self.__correl_parcial_series_energia
            )
        return self.__correl_parcial_series_energia

    @property
    def correlacao_series_ruidos_ree(self) -> Optional[pd.DataFrame]:
        """
        A tabela de correlação das séries de ruídos para
        todas as configurações vigentes e REEs,
        no mesmo formato do arquivo `parp.dat`.

        - ree (`str`)
        - data (`datetime`)
        - lag (`int`)
        - valor (`float`)

        :return: A tabela como um DataFrame
        :rtype: pd.DataFrame | None
        """
        if self.__correl_series_ruido is None:
            self.__correl_series_ruido = self.__concatena_dados(
                BlocoCorrelRuidosREE
            )
            self.__correl_series_ruido = self.__adiciona_coluna_ree(
                self.__correl_series_ruido
            )
        return self.__correl_series_ruido

    @property
    def correlacao_cruzada_media_ree(self) -> Optional[pd.DataFrame]:
        """
        A tabela de correlação cruzada da variável anual com
        as séries de energia para todas as configurações vigentes e REEs,
        no mesmo formato do arquivo `parp.dat`.

        - ree (`str`)
        - data (`datetime`)
        - lag (`int`)
        - valor (`float`)

        :return: A tabela como um DataFrame
        :rtype: pd.DataFrame | None
        """
        if self.__correl_cruzada_media is None:
            self.__correl_cruzada_media = self.__concatena_dados(
                BlocoCorrelCruzadaMediaREE
            )
            self.__correl_cruzada_media = self.__adiciona_coluna_ree(
                self.__correl_cruzada_media
            )
        return self.__correl_cruzada_media

    @property
    def ordem_original_modelo(self) -> Optional[pd.DataFrame]:
        """
        A tabela de ordens originais do modelo PAR ou PAR-A
        de cada REE, no mesmo formato do arquivo `parp.dat`,
        organizada por ano de estudo.

        - ree (`str`)
        - data (`datetime`)
        - valor (`int`)

        :return: A tabela como um DataFrame
        :rtype: pd.DataFrame | None
        """

        if self.__ordem_original_modelo is None:
            dados = self.__concatena_dados(BlocoOrdemModeloREE)
            if dados is not None:
                dados = (
                    dados.loc[dados["tipo"] == "ORIGINAL", :]
                    .drop(columns=["tipo"])
                    .copy()
                )
                dados = self.__adiciona_coluna_ree(dados)
                self.__ordem_original_modelo = dados

        return self.__ordem_original_modelo

    @property
    def ordem_final_modelo(self) -> Optional[pd.DataFrame]:
        """
        A tabela de ordens finais do modelo PAR ou PAR-A
        de cada REE, no mesmo formato do arquivo `parp.dat`,
        organizada por ano de estudo.

        - ree (`str`)
        - data (`datetime`)
        - valor (`int`)

        :return: A tabela como um DataFrame.
        :rtype: pd.DataFrame | None
        """
        if self.__ordem_final_modelo is None:
            dados = self.__concatena_dados(BlocoOrdemModeloREE)
            if dados is not None:
                dados = (
                    dados.loc[dados["tipo"] == "FINAL", :]
                    .drop(columns=["tipo"])
                    .copy()
                )
                dados = self.__adiciona_coluna_ree(dados)
                self.__ordem_final_modelo = dados

        return self.__ordem_final_modelo

    @property
    def coeficientes(self) -> Optional[pd.DataFrame]:
        """
        Lista de coeficientes dos modelos PAR ou PAR-A
        de cada REE, no mesmo formato do arquivo `parp.dat`,
        organizada por período de estudo.

        - ree (`str`)
        - estagio (`int`)
        - tipo (`str`)
        - ordem (`int`)
        - valor (`float`)

        :return: A tabela como um DataFrame.
        :rtype: pd.DataFrame | None
        """
        if self.__coeficientes is None:
            dados = self.__concatena_dados(BlocoCoeficientesModeloREE)
            if dados is not None:
                dados = self.__adiciona_coluna_ree_com_estagios(dados)
                self.__coeficientes = dados

        return self.__coeficientes

    @property
    def correlacao_espacial_anual(self) -> Optional[pd.DataFrame]:
        """
        A tabela de correlação para todas as configurações
        e REEs, no mesmo formato do arquivo `parp.dat`.

        - configuracao (`int`)
        - ree (`str`)
        - <Nome do REE 1> (`str`)
        - <Nome do REE 2> (`str`)
        - ...
        - <Nome do REE N> (`str`)

        :return: A tabela como um DataFrame.
        :rtype: pd.DataFrame | None
        """
        if self.__correl_espacial_anual is None:
            self.__correl_espacial_anual = self.__concatena_dados(
                BlocoCorrelEspacialAnualConfig
            )
        return self.__correl_espacial_anual

    @property
    def correlacao_espacial_mensal(self) -> Optional[pd.DataFrame]:
        """
        A tabela de correlação para todas as configurações
        e REEs, no mesmo formato do arquivo `parp.dat`.

        - configuracao (`int`)
        - ree (`str`)
        - mes (`int`)
        - <Nome do REE 1> (`str`)
        - <Nome do REE 2> (`str`)
        - ...
        - <Nome do REE N> (`str`)

        :return: A tabela como um DataFrame.
        :rtype: Optional[pd.DataFrame]
        """
        if self.__correl_espacial_mensal is None:
            self.__correl_espacial_mensal = self.__concatena_dados(
                BlocoCorrelEspacialMensalConfig
            )
        return self.__correl_espacial_mensal
