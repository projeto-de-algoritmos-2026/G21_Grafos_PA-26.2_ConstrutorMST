import math

import pytest

from conftest import PONTO_A, PONTO_B, PONTO_C, PONTO_ILHADO
from rotas import (
    ErroDeRotas,
    caminho_entre_nos,
    caminho_rota,
    distancia_rota_km,
    matriz_distancias_km,
    nos_mais_proximos,
)


def test_nos_mais_proximos_mapeia_cada_ponto(grafo_ruas_falso, nos_falsos):
    assert nos_mais_proximos(grafo_ruas_falso, [PONTO_A, PONTO_C]) == [1, 3]


def test_nos_mais_proximos_valida_coordenadas(grafo_ruas_falso, nos_falsos):
    with pytest.raises(ValueError):
        nos_mais_proximos(grafo_ruas_falso, [(200.0, 0.0)])


def test_matriz_distancias_km_usa_o_caminho_mais_curto(grafo_ruas_falso, nos_falsos):
    matriz, nos = matriz_distancias_km(grafo_ruas_falso, [PONTO_A, PONTO_B, PONTO_C])

    assert nos == [1, 2, 3]
    assert matriz[0][1] == pytest.approx(1.0)
    assert matriz[1][2] == pytest.approx(2.0)
    assert matriz[0][2] == pytest.approx(3.0)
    assert matriz[0][0] == 0.0


def test_matriz_distancias_km_e_simetrica(grafo_ruas_falso, nos_falsos):
    matriz, _ = matriz_distancias_km(grafo_ruas_falso, [PONTO_A, PONTO_B, PONTO_C])

    for i in range(3):
        for j in range(3):
            assert matriz[i][j] == matriz[j][i]


def test_matriz_distancias_km_marca_par_sem_rota_como_infinito(grafo_ruas_falso, nos_falsos):
    matriz, _ = matriz_distancias_km(grafo_ruas_falso, [PONTO_A, PONTO_ILHADO])

    assert math.isinf(matriz[0][1])


def test_caminho_entre_nos_retorna_coordenadas(grafo_ruas_falso):
    caminho = caminho_entre_nos(grafo_ruas_falso, 1, 3)

    assert caminho[0] == PONTO_A
    assert caminho[-1] == PONTO_C
    assert len(caminho) == 3


def test_caminho_entre_nos_retorna_none_sem_rota(grafo_ruas_falso):
    assert caminho_entre_nos(grafo_ruas_falso, 1, 4) is None


def test_caminho_entre_nos_com_origem_igual_ao_destino(grafo_ruas_falso):
    caminho = caminho_entre_nos(grafo_ruas_falso, 2, 2)

    assert caminho == [PONTO_B, PONTO_B]


def test_distancia_rota_km_em_quilometros(grafo_ruas_falso, nos_falsos):
    assert distancia_rota_km(grafo_ruas_falso, PONTO_A, PONTO_C) == pytest.approx(3.0)


def test_distancia_rota_km_sem_rota_gera_erro_amigavel(grafo_ruas_falso, nos_falsos):
    with pytest.raises(ErroDeRotas):
        distancia_rota_km(grafo_ruas_falso, PONTO_A, PONTO_ILHADO)


def test_caminho_rota_sem_rota_gera_erro_amigavel(grafo_ruas_falso, nos_falsos):
    with pytest.raises(ErroDeRotas):
        caminho_rota(grafo_ruas_falso, PONTO_A, PONTO_ILHADO)


def test_caminho_rota_retorna_polilinha(grafo_ruas_falso, nos_falsos):
    caminho = caminho_rota(grafo_ruas_falso, PONTO_A, PONTO_B)

    assert caminho == [PONTO_A, PONTO_B]
