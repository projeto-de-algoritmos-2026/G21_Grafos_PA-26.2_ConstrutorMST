import math

import pytest

from analise import (
    ALGORITMOS,
    comparar_algoritmos,
    executar_algoritmo,
    executar_benchmark,
    gerar_grafo_aleatorio,
)
from exemplos import GRAFOS_DIDATICOS, construir_grafo_didatico
from grafo import Grafo
from kruskal import kruskal_detalhado
from prim import prim_detalhado


def test_registro_de_algoritmos_contem_kruskal_e_prim():
    assert set(ALGORITMOS) == {"Kruskal", "Prim"}


def test_executar_algoritmo_rejeita_nome_desconhecido():
    with pytest.raises(ValueError):
        executar_algoritmo("Boruvka", Grafo(2, [(0, 1, 1)]))


@pytest.mark.parametrize("nome", list(GRAFOS_DIDATICOS))
def test_exemplos_didaticos_reproduzem_custo_conhecido(nome):
    grafo = construir_grafo_didatico(nome)
    esperado = GRAFOS_DIDATICOS[nome]["custo_esperado"]

    assert kruskal_detalhado(grafo).custo_total == esperado
    assert prim_detalhado(grafo).custo_total == esperado


@pytest.mark.parametrize("semente", [1, 7, 21, 42, 99])
def test_prim_e_kruskal_produzem_o_mesmo_custo(semente):
    grafo = gerar_grafo_aleatorio(40, densidade=0.4, semente=semente)
    comparacao = comparar_algoritmos(grafo)

    assert comparacao.custos_equivalentes is True
    assert comparacao.diferenca_custo < 1e-9


def test_comparacao_conta_arestas_comuns_e_exclusivas():
    grafo = Grafo(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 1), (0, 2, 1)])
    comparacao = comparar_algoritmos(grafo)

    total_kruskal = len(comparacao.resultados["Kruskal"].arestas)
    exclusivas = len(comparacao.arestas_exclusivas["Kruskal"])

    assert len(comparacao.arestas_comuns) + exclusivas == total_kruskal
    assert comparacao.custos_equivalentes is True


def test_comparacao_em_grafo_desconexo_mantem_mesmo_numero_de_componentes():
    grafo = Grafo(5, [(0, 1, 1), (1, 2, 2), (3, 4, 3)])
    comparacao = comparar_algoritmos(grafo)

    componentes = {resultado.componentes for resultado in comparacao.resultados.values()}
    assert componentes == {2}


def test_comparacao_como_linhas_tem_uma_linha_por_algoritmo():
    comparacao = comparar_algoritmos(gerar_grafo_aleatorio(10, semente=3))
    linhas = comparacao.como_linhas()

    assert len(linhas) == 2
    assert {linha["Algoritmo"] for linha in linhas} == {"Kruskal", "Prim"}


def test_grafo_aleatorio_e_conexo_e_respeita_densidade():
    grafo = gerar_grafo_aleatorio(30, densidade=1.0, semente=5)

    assert grafo.conexo() is True
    assert grafo.num_arestas == 30 * 29 // 2


def test_grafo_aleatorio_esparso_continua_conexo():
    grafo = gerar_grafo_aleatorio(50, densidade=0.05, semente=5)

    assert grafo.conexo() is True
    assert grafo.num_arestas >= 49


def test_grafo_aleatorio_e_reprodutivel():
    primeiro = gerar_grafo_aleatorio(20, densidade=0.5, semente=11).arestas
    segundo = gerar_grafo_aleatorio(20, densidade=0.5, semente=11).arestas

    assert primeiro == segundo


def test_grafo_aleatorio_valida_parametros():
    with pytest.raises(ValueError):
        gerar_grafo_aleatorio(0)
    with pytest.raises(ValueError):
        gerar_grafo_aleatorio(5, densidade=2.0)


def test_benchmark_gera_uma_linha_por_tamanho():
    linhas = executar_benchmark([10, 20], densidade=0.5, repeticoes=1)

    assert len(linhas) == 2
    assert linhas[0]["Vertices"] == 10
    assert linhas[1]["Vertices"] == 20
    for linha in linhas:
        assert linha["Custos iguais"] is True
        assert linha["Tempo Kruskal (ms)"] >= 0
        assert linha["Tempo Prim (ms)"] >= 0
        assert math.isclose(linha["Custo Kruskal"], linha["Custo Prim"], abs_tol=1e-6)


def test_benchmark_exige_repeticoes_positivas():
    with pytest.raises(ValueError):
        executar_benchmark([10], repeticoes=0)
