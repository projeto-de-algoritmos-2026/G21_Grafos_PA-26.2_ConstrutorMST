import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kruskal import kruskal


def test_kruskal_grafo_simples():
    arestas = [
        (0, 1, 4), (0, 2, 4), (1, 2, 2),
        (1, 3, 5), (2, 3, 8), (2, 4, 10),
        (3, 4, 2), (3, 5, 6), (4, 5, 3),
    ]
    mst, custo_total = kruskal(6, arestas)

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
