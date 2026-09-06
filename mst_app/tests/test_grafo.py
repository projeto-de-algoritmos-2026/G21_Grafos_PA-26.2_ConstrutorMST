import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from grafo import UnionFind, haversine


def test_haversine_mesmo_ponto():
    assert haversine(-15.7797, -47.9297, -15.7797, -47.9297) == 0.0


def test_haversine_brasilia_sao_paulo():
    distancia = haversine(-15.7797, -47.9297, -23.5505, -46.6333)
    assert math.isclose(distancia, 875, rel_tol=0.05)


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
