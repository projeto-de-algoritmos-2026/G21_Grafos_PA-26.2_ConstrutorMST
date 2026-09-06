import math

import pytest

from geo import (
    caixa_delimitadora,
    centro_geografico,
    coordenada_valida,
    haversine,
    limites,
    matriz_haversine,
)

BRASILIA = (-15.7797, -47.9297)
SAO_PAULO = (-23.5505, -46.6333)


def test_haversine_mesmo_ponto():
    assert haversine(*BRASILIA, *BRASILIA) == 0.0


def test_haversine_brasilia_sao_paulo():
    assert math.isclose(haversine(*BRASILIA, *SAO_PAULO), 875, rel_tol=0.05)


def test_haversine_e_simetrica():
    ida = haversine(*BRASILIA, *SAO_PAULO)
    volta = haversine(*SAO_PAULO, *BRASILIA)
    assert math.isclose(ida, volta, rel_tol=1e-12)


def test_coordenada_valida_rejeita_fora_do_intervalo():
    assert coordenada_valida(-15.0, -47.0)
    assert not coordenada_valida(-91.0, 0.0)
    assert not coordenada_valida(0.0, 181.0)
    assert not coordenada_valida("norte", 0.0)
    assert not coordenada_valida(float("nan"), 0.0)


def test_centro_geografico_de_dois_pontos():
    centro = centro_geografico([(0.0, 0.0), (10.0, 20.0)])
    assert centro == (5.0, 10.0)


def test_centro_geografico_exige_pontos():
    with pytest.raises(ValueError):
        centro_geografico([])


def test_limites_retorna_extremos():
    assert limites([(1.0, 2.0), (-3.0, 8.0)]) == (-3.0, 2.0, 1.0, 8.0)


def test_caixa_delimitadora_respeita_ordem_do_osmnx():
    oeste, sul, leste, norte = caixa_delimitadora([BRASILIA, SAO_PAULO])
    assert oeste < leste
    assert sul < norte


def test_caixa_delimitadora_garante_lado_minimo():
    ponto = BRASILIA
    oeste, sul, leste, norte = caixa_delimitadora([ponto, ponto], margem_km=0.0, lado_minimo_km=2.0)
    assert (norte - sul) > 0.017
    assert (leste - oeste) > 0.017


def test_matriz_haversine_e_simetrica_com_diagonal_zero():
    matriz = matriz_haversine([BRASILIA, SAO_PAULO, (-19.9, -43.9)])
    for i in range(3):
        assert matriz[i][i] == 0.0
        for j in range(3):
            assert math.isclose(matriz[i][j], matriz[j][i])
