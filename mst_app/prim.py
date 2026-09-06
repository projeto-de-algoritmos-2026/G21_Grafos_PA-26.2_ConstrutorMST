from heapq import heappop, heappush
from time import perf_counter

from grafo import Aresta, Grafo
from mst import criar_resultado

NOME = "Prim"
SEM_PAI = -1


def prim_detalhado(grafo, raiz=0):
    if not isinstance(grafo, Grafo):
        raise TypeError("prim_detalhado espera uma instancia de Grafo.")
    if grafo.num_vertices and (raiz < 0 or raiz >= grafo.num_vertices):
        raise ValueError(f"Raiz {raiz} fora do intervalo [0, {grafo.num_vertices - 1}].")

    inicio = perf_counter()

    adjacencia = grafo.lista_adjacencia()
    visitado = [False] * grafo.num_vertices
    arestas_mst = []
    custo_total = 0.0
    componentes = 0

    insercoes_heap = 0
    remocoes_heap = 0
    arestas_relaxadas = 0
    vertices_visitados = 0

    ordem_de_partida = list(range(grafo.num_vertices))
    if grafo.num_vertices:
        ordem_de_partida = [raiz] + [v for v in ordem_de_partida if v != raiz]

    for partida in ordem_de_partida:
        if visitado[partida]:
            continue

        componentes += 1
        fila = [(0.0, partida, SEM_PAI)]
        insercoes_heap += 1

        while fila:
            peso, vertice, pai = heappop(fila)
            remocoes_heap += 1

            if visitado[vertice]:
                continue

            visitado[vertice] = True
            vertices_visitados += 1

            if pai != SEM_PAI:
                arestas_mst.append(Aresta(pai, vertice, peso))
                custo_total += peso

            for vizinho, peso_aresta in adjacencia[vertice]:
                arestas_relaxadas += 1
                if not visitado[vizinho]:
                    heappush(fila, (peso_aresta, vizinho, vertice))
                    insercoes_heap += 1

    tempo_execucao = perf_counter() - inicio

    operacoes = {
        "insercoes_heap": insercoes_heap,
        "remocoes_heap": remocoes_heap,
        "arestas_relaxadas": arestas_relaxadas,
        "vertices_visitados": vertices_visitados,
        "reinicios_por_componente": componentes,
    }

    return criar_resultado(
        algoritmo=NOME,
        grafo=grafo,
        arestas=arestas_mst,
        custo_total=custo_total,
        componentes=componentes,
        tempo_execucao=tempo_execucao,
        operacoes=operacoes,
    )


def prim(n, arestas, raiz=0):
    resultado = prim_detalhado(Grafo(n, arestas), raiz=raiz)
    return list(resultado.arestas), resultado.custo_total
