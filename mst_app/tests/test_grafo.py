import math

import pytest

from grafo import Aresta, Grafo, UnionFind


def test_union_find_une_dois_conjuntos():
    uf = UnionFind(4)
    assert uf.union(0, 1) is True
    assert uf.find(0) == uf.find(1)


def test_union_find_rejeita_uniao_ja_existente():
    uf = UnionFind(4)
    uf.union(0, 1)
    assert uf.union(0, 1) is False


def test_union_find_mantem_conjuntos_separados():
    uf = UnionFind(4)
    uf.union(0, 1)
    uf.union(2, 3)
    assert uf.find(0) != uf.find(2)


def test_union_find_uniao_transitiva():
    uf = UnionFind(4)
    uf.union(0, 1)
    uf.union(1, 2)
    assert uf.find(0) == uf.find(2)


def test_union_find_conta_componentes():
    uf = UnionFind(5)
    assert uf.componentes == 5
    uf.union(0, 1)
    uf.union(1, 2)
    assert uf.componentes == 3


def test_union_find_rejeita_indice_invalido():
    uf = UnionFind(3)
    with pytest.raises(IndexError):
        uf.find(7)


def test_union_find_suporta_cadeia_longa_sem_estouro_de_pilha():
    total = 20000
    uf = UnionFind(total)
    for i in range(total - 1):
        uf.union(i, i + 1)
    assert uf.find(0) == uf.find(total - 1)
    assert uf.componentes == 1


def test_grafo_registra_arestas_e_adjacencia():
    grafo = Grafo(3, [(0, 1, 2.5), (1, 2, 1.0)])
    assert grafo.num_vertices == 3
    assert grafo.num_arestas == 2
    assert grafo.arestas[0] == Aresta(0, 1, 2.5)
    assert set(grafo.vizinhos(1)) == {(0, 2.5), (2, 1.0)}
    assert grafo.grau(1) == 2


def test_grafo_rejeita_vertice_fora_do_intervalo():
    grafo = Grafo(2)
    with pytest.raises(ValueError):
        grafo.adicionar_aresta(0, 5, 1.0)


def test_grafo_rejeita_peso_nao_finito():
    grafo = Grafo(2)
    with pytest.raises(ValueError):
        grafo.adicionar_aresta(0, 1, math.inf)


def test_grafo_rejeita_numero_de_vertices_negativo():
    with pytest.raises(ValueError):
        Grafo(-1)


def test_grafo_ignora_laco_na_adjacencia():
    grafo = Grafo(2, [(0, 0, 5.0)])
    assert grafo.num_arestas == 1
    assert grafo.grau(0) == 0


def test_grafo_identifica_componentes():
    grafo = Grafo(5, [(0, 1, 1.0), (1, 2, 1.0), (3, 4, 1.0)])
    assert grafo.num_componentes() == 2
    assert grafo.componentes() == [[0, 1, 2], [3, 4]]
    assert grafo.conexo() is False


def test_grafo_conexo_com_um_vertice():
    grafo = Grafo(1)
    assert grafo.conexo() is True
    assert grafo.densidade() == 0.0


def test_grafo_de_matriz_descarta_pares_sem_rota():
    matriz = [
        [0.0, 2.0, math.inf],
        [2.0, 0.0, 3.0],
        [math.inf, 3.0, 0.0],
    ]
    grafo = Grafo.de_matriz(matriz)
    assert grafo.num_arestas == 2
    assert grafo.num_componentes() == 1


def test_grafo_densidade_do_grafo_completo():
    grafo = Grafo(4, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 2, 1), (1, 3, 1), (2, 3, 1)])
    assert grafo.densidade() == 1.0
