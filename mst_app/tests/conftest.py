import math
import sys
from pathlib import Path

CODIGO = Path(__file__).resolve().parent.parent
if str(CODIGO) not in sys.path:
    sys.path.insert(0, str(CODIGO))

import networkx as nx
import pytest

import rotas

PONTO_A = (-15.7900, -47.9000)
PONTO_B = (-15.7900, -47.8900)
PONTO_C = (-15.7900, -47.8800)
PONTO_ILHADO = (-15.8100, -47.8600)

COORDENADAS_DOS_NOS = {
    1: PONTO_A,
    2: PONTO_B,
    3: PONTO_C,
    4: PONTO_ILHADO,
}


@pytest.fixture
def grafo_ruas_falso():
    grafo = nx.MultiDiGraph()
    for identificador, (lat, lon) in COORDENADAS_DOS_NOS.items():
        grafo.add_node(identificador, x=lon, y=lat)

    grafo.add_edge(1, 2, length=1000.0)
    grafo.add_edge(2, 1, length=1000.0)
    grafo.add_edge(2, 3, length=2000.0)
    grafo.add_edge(3, 2, length=2000.0)
    return grafo


@pytest.fixture
def nos_falsos(monkeypatch):
    def nearest_nodes(grafo, X, Y, **kwargs):
        entradas = list(zip(list(X), list(Y)))
        encontrados = []
        for lon, lat in entradas:
            melhor = min(
                COORDENADAS_DOS_NOS,
                key=lambda no: math.dist(
                    (lat, lon), (COORDENADAS_DOS_NOS[no][0], COORDENADAS_DOS_NOS[no][1])
                ),
            )
            encontrados.append(melhor)
        return encontrados

    monkeypatch.setattr(rotas.ox, "nearest_nodes", nearest_nodes)
    return nearest_nodes


@pytest.fixture
def estacoes_tres():
    from rede import Estacao

    return [
        Estacao(id=0, nome="Estacao A", lat=PONTO_A[0], lon=PONTO_A[1]),
        Estacao(id=1, nome="Estacao B", lat=PONTO_B[0], lon=PONTO_B[1]),
        Estacao(id=2, nome="Estacao C", lat=PONTO_C[0], lon=PONTO_C[1]),
    ]
