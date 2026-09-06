import pytest

from geo import haversine
from rotas import baixar_grafo_area, baixar_grafo_ruas, caminho_rota, distancia_rota_km

pytestmark = pytest.mark.integracao

CENTRO_BRASILIA = (-15.7797, -47.9297)
ORIGEM = (-15.7797, -47.9297)
DESTINO = (-15.7750, -47.9250)


@pytest.fixture(scope="module")
def grafo_ruas():
    return baixar_grafo_ruas(CENTRO_BRASILIA, raio_m=800)


def test_distancia_rota_e_positiva(grafo_ruas):
    assert distancia_rota_km(grafo_ruas, ORIGEM, DESTINO) > 0


def test_distancia_rota_nunca_menor_que_linha_reta(grafo_ruas):
    distancia_rua = distancia_rota_km(grafo_ruas, ORIGEM, DESTINO)
    distancia_reta = haversine(*ORIGEM, *DESTINO)

    assert distancia_rua >= distancia_reta


def test_caminho_rota_comeca_e_termina_perto_dos_pontos(grafo_ruas):
    caminho = caminho_rota(grafo_ruas, ORIGEM, DESTINO)

    assert len(caminho) >= 2
    assert haversine(*caminho[0], *ORIGEM) < 0.3
    assert haversine(*caminho[-1], *DESTINO) < 0.3


def test_baixar_grafo_area_cobre_os_pontos_informados():
    grafo_ruas = baixar_grafo_area([ORIGEM, DESTINO], margem_km=0.3)

    assert grafo_ruas.number_of_nodes() > 0
    assert grafo_ruas.number_of_edges() > 0


def test_baixar_grafo_ruas_rejeita_tipo_de_rede_invalido():
    with pytest.raises(ValueError):
        baixar_grafo_ruas(CENTRO_BRASILIA, tipo_rede="foguete")
