import pytest

from grafo import Grafo
from prim import prim, prim_detalhado

GRAFO_CLASSICO = [
    (0, 1, 4), (0, 2, 4), (1, 2, 2),
    (1, 3, 5), (2, 3, 8), (2, 4, 10),
    (3, 4, 2), (3, 5, 6), (4, 5, 3),
]

GRAFO_DE_NOVE_VERTICES = [
    (0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 11), (2, 3, 7),
    (2, 8, 2), (2, 5, 4), (3, 4, 9), (3, 5, 14), (4, 5, 10),
    (5, 6, 2), (6, 7, 1), (6, 8, 6), (7, 8, 7),
]


def test_prim_grafo_simples():
    mst, custo_total = prim(6, GRAFO_CLASSICO)

    assert len(mst) == 5
    assert custo_total == 16.0


def test_prim_grafo_triangulo_descarta_aresta_mais_cara():
    mst, custo_total = prim(3, [(0, 1, 1), (1, 2, 1), (0, 2, 5)])

    assert len(mst) == 2
    assert custo_total == 2.0
    arestas_mst = {(min(u, v), max(u, v)) for u, v, _ in mst}
    assert (0, 2) not in arestas_mst


def test_prim_grafo_de_nove_vertices():
    resultado = prim_detalhado(Grafo(9, GRAFO_DE_NOVE_VERTICES))

    assert resultado.custo_total == 37.0
    assert resultado.num_arestas_mst == 8
    assert resultado.e_arvore_geradora is True


def test_prim_grafo_desconexo_gera_floresta():
    resultado = prim_detalhado(Grafo(5, [(0, 1, 1), (0, 2, 3), (1, 2, 2), (3, 4, 4)]))

    assert resultado.componentes == 2
    assert resultado.conexo is False
    assert resultado.num_arestas_mst == 3
    assert resultado.custo_total == 7.0


def test_prim_vertice_unico():
    resultado = prim_detalhado(Grafo(1))

    assert resultado.num_arestas_mst == 0
    assert resultado.custo_total == 0.0
    assert resultado.e_arvore_geradora is True


def test_prim_grafo_vazio():
    resultado = prim_detalhado(Grafo(0))

    assert resultado.num_arestas_mst == 0
    assert resultado.componentes == 0


def test_prim_vertices_isolados_contam_como_componentes():
    resultado = prim_detalhado(Grafo(4, [(0, 1, 1)]))

    assert resultado.componentes == 3
    assert resultado.num_arestas_mst == 1


def test_prim_com_pesos_iguais():
    resultado = prim_detalhado(Grafo(4, [(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 0, 2), (0, 2, 2)]))

    assert resultado.custo_total == 6.0
    assert resultado.num_arestas_mst == 3


def test_prim_ignora_arestas_paralelas_mais_caras():
    resultado = prim_detalhado(Grafo(2, [(0, 1, 9.0), (0, 1, 1.0)]))

    assert resultado.num_arestas_mst == 1
    assert resultado.custo_total == 1.0


def test_prim_descarta_laco():
    resultado = prim_detalhado(Grafo(2, [(0, 0, 1.0), (0, 1, 5.0)]))

    assert resultado.num_arestas_mst == 1
    assert resultado.custo_total == 5.0


def test_prim_independe_da_raiz_no_custo_total():
    grafo = Grafo(9, GRAFO_DE_NOVE_VERTICES)
    custos = {prim_detalhado(grafo, raiz=raiz).custo_total for raiz in range(9)}

    assert custos == {37.0}


def test_prim_rejeita_raiz_invalida():
    with pytest.raises(ValueError):
        prim_detalhado(Grafo(3, [(0, 1, 1)]), raiz=9)


def test_prim_detalhado_exige_grafo():
    with pytest.raises(TypeError):
        prim_detalhado([(0, 1, 1)])


def test_prim_registra_contadores_de_operacoes():
    resultado = prim_detalhado(Grafo(6, GRAFO_CLASSICO))
    operacoes = resultado.operacoes

    assert operacoes["vertices_visitados"] == 6
    assert operacoes["arestas_relaxadas"] == 2 * len(GRAFO_CLASSICO)
    assert operacoes["insercoes_heap"] >= operacoes["vertices_visitados"]
    assert operacoes["remocoes_heap"] <= operacoes["insercoes_heap"]
    assert operacoes["reinicios_por_componente"] == 1


def test_prim_produz_arvore_sem_ciclos():
    resultado = prim_detalhado(Grafo(6, GRAFO_CLASSICO))
    visitados = set()
    for origem, destino, _ in resultado.arestas:
        assert not (origem in visitados and destino in visitados)
        visitados.add(origem)
        visitados.add(destino)


def test_prim_grafo_em_estrela():
    arestas = [(0, i, float(i)) for i in range(1, 6)]
    resultado = prim_detalhado(Grafo(6, arestas))

    assert resultado.num_arestas_mst == 5
    assert resultado.custo_total == 15.0


def test_prim_em_grafo_maior_em_linha():
    total = 500
    arestas = [(i, i + 1, 1.0) for i in range(total - 1)]
    resultado = prim_detalhado(Grafo(total, arestas))

    assert resultado.num_arestas_mst == total - 1
    assert resultado.custo_total == float(total - 1)
    assert resultado.conexo is True
