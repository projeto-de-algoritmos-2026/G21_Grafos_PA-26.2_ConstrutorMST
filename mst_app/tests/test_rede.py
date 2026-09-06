import math

import pytest

from conftest import PONTO_A, PONTO_B, PONTO_C, PONTO_ILHADO
from rede import (
    MODO_HAVERSINE,
    MODO_ROTA,
    ErroDeRede,
    Estacao,
    arestas_candidatas,
    criar_estacao,
    estacao_proxima,
    montar_rede,
    pares_inalcancaveis,
    proximo_id,
    validar_estacoes,
)


def montar_com_grafo_falso(estacoes, grafo_ruas, algoritmo="Kruskal", custo_por_km=0.0):
    return montar_rede(
        estacoes=estacoes,
        algoritmo=algoritmo,
        modo=MODO_ROTA,
        custo_por_km=custo_por_km,
        obter_grafo_ruas=lambda pontos: grafo_ruas,
    )


def test_criar_estacao_gera_nome_padrao():
    estacao = criar_estacao([], -15.79, -47.9)

    assert estacao.id == 0
    assert estacao.nome == "Estacao 1"


def test_criar_estacao_usa_nome_informado():
    estacao = criar_estacao([], -15.79, -47.9, "  Terminal Norte  ")

    assert estacao.nome == "Terminal Norte"


def test_criar_estacao_rejeita_coordenada_invalida():
    with pytest.raises(ErroDeRede):
        criar_estacao([], 120.0, -47.9)


def test_criar_estacao_rejeita_duplicata_praticamente_no_mesmo_ponto():
    existentes = [Estacao(id=0, nome="A", lat=-15.79, lon=-47.9)]

    with pytest.raises(ErroDeRede):
        criar_estacao(existentes, -15.790001, -47.900001)


def test_estacao_proxima_retorna_none_quando_distante():
    existentes = [Estacao(id=0, nome="A", lat=-15.79, lon=-47.9)]

    assert estacao_proxima(existentes, -15.80, -47.91) is None


def test_proximo_id_continua_apos_remocoes():
    estacoes = [Estacao(id=0, nome="A", lat=0.0, lon=0.0), Estacao(id=4, nome="B", lat=1.0, lon=1.0)]

    assert proximo_id(estacoes) == 5


def test_validar_estacoes_exige_duas_estacoes():
    with pytest.raises(ErroDeRede):
        validar_estacoes([Estacao(id=0, nome="A", lat=0.0, lon=0.0)])


def test_pares_inalcancaveis_identifica_infinitos():
    matriz = [[0.0, math.inf], [math.inf, 0.0]]

    assert pares_inalcancaveis(matriz) == ((0, 1),)


def test_montar_rede_modo_haversine_nao_acessa_a_internet(estacoes_tres):
    rede = montar_rede(estacoes=estacoes_tres, algoritmo="Prim", modo=MODO_HAVERSINE)

    assert rede.modo == MODO_HAVERSINE
    assert rede.algoritmo == "Prim"
    assert rede.resultado.num_arestas_mst == 2
    assert rede.grafo.num_arestas == 3
    assert all(conexao.rota_real is False for conexao in rede.conexoes)


def test_montar_rede_calcula_custo_financeiro(estacoes_tres):
    rede = montar_rede(
        estacoes=estacoes_tres, algoritmo="Kruskal", modo=MODO_HAVERSINE, custo_por_km=10.0
    )

    assert rede.custo_total == pytest.approx(rede.distancia_total_km * 10.0)


def test_montar_rede_usa_rotas_reais_quando_disponiveis(
    estacoes_tres, grafo_ruas_falso, nos_falsos
):
    rede = montar_com_grafo_falso(estacoes_tres, grafo_ruas_falso)

    assert rede.usa_rotas_reais is True
    assert rede.distancia_total_km == pytest.approx(3.0)
    assert all(conexao.rota_real for conexao in rede.conexoes)
    assert rede.pares_sem_conexao == ()


def test_montar_rede_com_estacao_sem_rota_gera_floresta(grafo_ruas_falso, nos_falsos):
    estacoes = [
        Estacao(id=0, nome="A", lat=PONTO_A[0], lon=PONTO_A[1]),
        Estacao(id=1, nome="B", lat=PONTO_B[0], lon=PONTO_B[1]),
        Estacao(id=2, nome="Ilhada", lat=PONTO_ILHADO[0], lon=PONTO_ILHADO[1]),
    ]
    rede = montar_com_grafo_falso(estacoes, grafo_ruas_falso)

    assert len(rede.pares_sem_conexao) == 2
    assert rede.resultado.conexo is False
    assert rede.resultado.componentes == 2


def test_montar_rede_sempre_compara_os_dois_algoritmos(estacoes_tres, grafo_ruas_falso, nos_falsos):
    rede = montar_com_grafo_falso(estacoes_tres, grafo_ruas_falso, algoritmo="Prim")

    assert set(rede.comparacao.resultados) == {"Kruskal", "Prim"}
    assert rede.comparacao.custos_equivalentes is True


def test_montar_rede_rejeita_modo_invalido(estacoes_tres):
    with pytest.raises(ErroDeRede):
        montar_rede(estacoes=estacoes_tres, modo="teletransporte")


def test_montar_rede_rejeita_algoritmo_invalido(estacoes_tres):
    with pytest.raises(ErroDeRede):
        montar_rede(estacoes=estacoes_tres, algoritmo="Boruvka", modo=MODO_HAVERSINE)


def test_montar_rede_exige_duas_estacoes():
    with pytest.raises(ErroDeRede):
        montar_rede(estacoes=[Estacao(id=0, nome="A", lat=0.0, lon=0.0)], modo=MODO_HAVERSINE)


def test_montar_rede_falha_quando_nenhuma_conexao_existe(grafo_ruas_falso, nos_falsos):
    estacoes = [
        Estacao(id=0, nome="A", lat=PONTO_A[0], lon=PONTO_A[1]),
        Estacao(id=1, nome="Ilhada", lat=PONTO_ILHADO[0], lon=PONTO_ILHADO[1]),
    ]

    with pytest.raises(ErroDeRede):
        montar_com_grafo_falso(estacoes, grafo_ruas_falso)


def test_conexoes_por_estacao_conta_grau_na_mst(estacoes_tres):
    rede = montar_rede(estacoes=estacoes_tres, modo=MODO_HAVERSINE)

    graus = [len(rede.conexoes_por_estacao(indice)) for indice in range(3)]
    assert sum(graus) == 2 * rede.resultado.num_arestas_mst


def test_arestas_candidatas_excluem_as_selecionadas(estacoes_tres):
    rede = montar_rede(estacoes=estacoes_tres, modo=MODO_HAVERSINE)
    candidatas = arestas_candidatas(rede)

    selecionadas = {
        (min(c.origem, c.destino), max(c.origem, c.destino)) for c in rede.conexoes
    }
    for aresta in candidatas:
        assert (min(aresta.origem, aresta.destino), max(aresta.origem, aresta.destino)) not in selecionadas


def test_estacao_converte_para_dicionario_e_volta():
    original = Estacao(id=3, nome="Central", lat=-15.79, lon=-47.9)
    copia = Estacao.de_dict(original.como_dict())

    assert copia == original


def test_nome_da_estacao_por_indice(estacoes_tres):
    rede = montar_rede(estacoes=estacoes_tres, modo=MODO_HAVERSINE)

    assert rede.nome_da_estacao(0) == "Estacao A"
    assert rede.nome_da_estacao(2) == "Estacao C"
