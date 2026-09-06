import pytest

from grafo import Grafo
from kruskal import kruskal, kruskal_detalhado

GRAFO_CLASSICO = [
    (0, 1, 4), (0, 2, 4), (1, 2, 2),
    (1, 3, 5), (2, 3, 8), (2, 4, 10),
    (3, 4, 2), (3, 5, 6), (4, 5, 3),
]


def test_kruskal_grafo_simples():
    mst, custo_total = kruskal(6, GRAFO_CLASSICO)

    assert len(mst) == 5
    assert custo_total == 16.0


def test_kruskal_grafo_triangulo():
    arestas = [(0, 1, 1), (1, 2, 1), (0, 2, 5)]
    mst, custo_total = kruskal(3, arestas)

    assert len(mst) == 2
    assert custo_total == 2.0
    arestas_mst = {(u, v) for u, v, _ in mst}
    assert (0, 2) not in arestas_mst and (2, 0) not in arestas_mst


def test_kruskal_grafo_desconexo():
    arestas = [(0, 1, 1), (2, 3, 1)]
    mst, custo_total = kruskal(4, arestas)

    assert len(mst) == 2
    assert custo_total == 2.0


def test_kruskal_detalhado_reporta_componentes_e_conectividade():
    resultado = kruskal_detalhado(Grafo(4, [(0, 1, 1), (2, 3, 1)]))

    assert resultado.componentes == 2
    assert resultado.conexo is False
    assert resultado.e_floresta is True
    assert resultado.e_arvore_geradora is False


def test_kruskal_detalhado_em_grafo_conexo_gera_arvore_geradora():
    resultado = kruskal_detalhado(Grafo(6, GRAFO_CLASSICO))

    assert resultado.e_arvore_geradora is True
    assert resultado.num_arestas_mst == resultado.num_vertices - 1
    assert resultado.custo_total == 16.0


def test_kruskal_vertice_unico():
    resultado = kruskal_detalhado(Grafo(1))

    assert resultado.num_arestas_mst == 0
    assert resultado.custo_total == 0.0
    assert resultado.conexo is True
    assert resultado.e_arvore_geradora is True


def test_kruskal_grafo_vazio():
    resultado = kruskal_detalhado(Grafo(0))

    assert resultado.num_arestas_mst == 0
    assert resultado.componentes == 0


def test_kruskal_ignora_arestas_paralelas_mais_caras():
    resultado = kruskal_detalhado(Grafo(2, [(0, 1, 9.0), (0, 1, 1.0)]))

    assert resultado.num_arestas_mst == 1
    assert resultado.custo_total == 1.0


def test_kruskal_descarta_laco():
    resultado = kruskal_detalhado(Grafo(2, [(0, 0, 1.0), (0, 1, 5.0)]))

    assert resultado.num_arestas_mst == 1
    assert resultado.custo_total == 5.0


def test_kruskal_registra_contadores_de_operacoes():
    resultado = kruskal_detalhado(Grafo(6, GRAFO_CLASSICO))

    operacoes = resultado.operacoes
    assert operacoes["arestas_ordenadas"] == len(GRAFO_CLASSICO)
    assert 0 < operacoes["arestas_avaliadas"] <= len(GRAFO_CLASSICO)
    assert operacoes["unioes_efetivadas"] == resultado.num_arestas_mst


def test_kruskal_e_deterministico_com_empates():
    arestas = [(0, 1, 1), (1, 2, 1), (0, 2, 1)]
    primeira = kruskal_detalhado(Grafo(3, arestas)).arestas
    segunda = kruskal_detalhado(Grafo(3, arestas)).arestas

    assert primeira == segunda


def test_kruskal_detalhado_exige_grafo():
    with pytest.raises(TypeError):
        kruskal_detalhado([(0, 1, 1)])
