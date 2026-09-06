from time import perf_counter

from grafo import Grafo, UnionFind
from mst import criar_resultado

NOME = "Kruskal"


def kruskal_detalhado(grafo):
    if not isinstance(grafo, Grafo):
        raise TypeError("kruskal_detalhado espera uma instancia de Grafo.")

    inicio = perf_counter()

    union_find = UnionFind(grafo.num_vertices)
    arestas_mst = []
    custo_total = 0.0
    arestas_avaliadas = 0
    limite = max(grafo.num_vertices - 1, 0)

    arestas_ordenadas = sorted(grafo.arestas, key=lambda a: (a.peso, a.origem, a.destino))

    for aresta in arestas_ordenadas:
        if len(arestas_mst) == limite:
            break
        arestas_avaliadas += 1
        if union_find.union(aresta.origem, aresta.destino):
            arestas_mst.append(aresta)
            custo_total += aresta.peso

    tempo_execucao = perf_counter() - inicio

    operacoes = {
        "arestas_ordenadas": len(arestas_ordenadas),
        "arestas_avaliadas": arestas_avaliadas,
        "chamadas_find": union_find.chamadas_find,
        "passos_find": union_find.passos_find,
        "unioes_efetivadas": union_find.unioes_efetivadas,
    }

    return criar_resultado(
        algoritmo=NOME,
        grafo=grafo,
        arestas=arestas_mst,
        custo_total=custo_total,
        componentes=union_find.componentes,
        tempo_execucao=tempo_execucao,
        operacoes=operacoes,
    )


def kruskal(n, arestas):
    resultado = kruskal_detalhado(Grafo(n, arestas))
    return list(resultado.arestas), resultado.custo_total
