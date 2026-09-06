import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from grafo import haversine
from rotas import baixar_grafo_ruas, caminho_rota, distancia_rota_km

CENTRO_BRASILIA = (-15.7797, -47.9297)


@pytest.fixture(scope="module")
def grafo_ruas():
    return baixar_grafo_ruas(CENTRO_BRASILIA, raio_m=800)


def test_distancia_rota_e_positiva(grafo_ruas):
    origem = (-15.7797, -47.9297)
    destino = (-15.7750, -47.9250)

    distancia = distancia_rota_km(grafo_ruas, origem, destino)
    assert distancia > 0


def test_distancia_rota_nunca_menor_que_linha_reta(grafo_ruas):
    origem = (-15.7797, -47.9297)
    destino = (-15.7750, -47.9250)

    distancia_rua = distancia_rota_km(grafo_ruas, origem, destino)
    distancia_reta = haversine(*origem, *destino)

    assert distancia_rua >= distancia_reta


def test_caminho_rota_comeca_e_termina_perto_dos_pontos(grafo_ruas):
    origem = (-15.7797, -47.9297)
    destino = (-15.7750, -47.9250)

    caminho = caminho_rota(grafo_ruas, origem, destino)

    assert len(caminho) >= 2
    assert haversine(*caminho[0], *origem) < 0.3
    assert haversine(*caminho[-1], *destino) < 0.3
