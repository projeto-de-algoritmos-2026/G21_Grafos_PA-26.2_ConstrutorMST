import json

import pytest

from rede import MODO_HAVERSINE, montar_rede
from relatorio import (
    exportar_csv,
    exportar_json,
    gerar_relatorio_markdown,
    linhas_das_conexoes,
    linhas_das_estacoes,
    tabela_markdown,
)


@pytest.fixture
def rede(estacoes_tres):
    return montar_rede(
        estacoes=estacoes_tres, algoritmo="Kruskal", modo=MODO_HAVERSINE, custo_por_km=100.0
    )


def test_linhas_das_conexoes_estao_ordenadas_por_distancia(rede):
    linhas = linhas_das_conexoes(rede)
    distancias = [linha["Distancia (km)"] for linha in linhas]

    assert len(linhas) == rede.resultado.num_arestas_mst
    assert distancias == sorted(distancias)


def test_linhas_das_estacoes_incluem_grau(rede):
    linhas = linhas_das_estacoes(rede)

    assert len(linhas) == 3
    assert sum(linha["Conexoes na MST"] for linha in linhas) == 2 * len(rede.conexoes)


def test_exportar_csv_tem_cabecalho_e_uma_linha_por_conexao(rede):
    conteudo = exportar_csv(rede).strip().splitlines()

    assert conteudo[0].startswith("Ordem,Origem,Destino")
    assert len(conteudo) == 1 + rede.resultado.num_arestas_mst


def test_exportar_json_e_valido_e_contem_metricas(rede):
    dados = json.loads(exportar_json(rede))

    assert dados["algoritmo"] == "Kruskal"
    assert dados["metricas"]["arestas_da_mst"] == rede.resultado.num_arestas_mst
    assert set(dados["comparacao"]) == {"Kruskal", "Prim"}
    assert dados["custos_equivalentes"] is True
    assert len(dados["estacoes"]) == 3


def test_tabela_markdown_com_lista_vazia():
    assert tabela_markdown([]) == "_Sem dados._"


def test_tabela_markdown_gera_cabecalho_e_separador():
    tabela = tabela_markdown([{"A": 1, "B": 2}])
    linhas = tabela.splitlines()

    assert linhas[0] == "| A | B |"
    assert linhas[1] == "| --- | --- |"
    assert linhas[2] == "| 1 | 2 |"


def test_relatorio_markdown_contem_secoes_esperadas(rede):
    texto = gerar_relatorio_markdown(rede)

    assert "# Relatorio de execucao" in texto
    assert "## Metricas da MST" in texto
    assert "## Comparacao entre algoritmos" in texto
    assert "## Conexoes selecionadas" in texto
    assert "Kruskal" in texto and "Prim" in texto
