import math
import random
from dataclasses import dataclass

from grafo import Grafo
from kruskal import kruskal_detalhado
from prim import prim_detalhado

ALGORITMOS = {
    "Kruskal": kruskal_detalhado,
    "Prim": prim_detalhado,
}

TOLERANCIA_CUSTO = 1e-9


def executar_algoritmo(nome, grafo):
    if nome not in ALGORITMOS:
        disponiveis = ", ".join(ALGORITMOS)
        raise ValueError(f"Algoritmo '{nome}' nao existe. Disponiveis: {disponiveis}.")
    return ALGORITMOS[nome](grafo)


def chave_nao_direcionada(aresta):
    origem, destino, peso = aresta
    return (min(origem, destino), max(origem, destino), round(float(peso), 9))


@dataclass(frozen=True)
class ComparacaoMST:
    resultados: dict
    custos_equivalentes: bool
    diferenca_custo: float
    arestas_comuns: tuple
    arestas_exclusivas: dict
    algoritmo_mais_rapido: str
    houve_empate_de_arestas: bool

    def como_linhas(self):
        linhas = []
        for nome, resultado in self.resultados.items():
            linhas.append(
                {
                    "Algoritmo": nome,
                    "Vertices": resultado.num_vertices,
                    "Arestas do grafo": resultado.num_arestas_grafo,
                    "Arestas da MST": resultado.num_arestas_mst,
                    "Custo total (km)": round(resultado.custo_total, 4),
                    "Componentes": resultado.componentes,
                    "Conexo": "Sim" if resultado.conexo else "Nao",
                    "Tempo (ms)": round(resultado.tempo_ms, 4),
                }
            )
        return linhas


def comparar_algoritmos(grafo):
    resultados = {nome: funcao(grafo) for nome, funcao in ALGORITMOS.items()}

    custos = [resultado.custo_total for resultado in resultados.values()]
    diferenca_custo = max(custos) - min(custos)
    custos_equivalentes = math.isclose(
        max(custos), min(custos), rel_tol=1e-9, abs_tol=TOLERANCIA_CUSTO
    )

    conjuntos = {
        nome: {chave_nao_direcionada(a) for a in resultado.arestas}
        for nome, resultado in resultados.items()
    }
    comuns = set.intersection(*conjuntos.values()) if conjuntos else set()
    exclusivas = {nome: tuple(sorted(conjunto - comuns)) for nome, conjunto in conjuntos.items()}

    mais_rapido = min(resultados.items(), key=lambda item: item[1].tempo_execucao)[0]
    houve_empate = any(len(valor) > 0 for valor in exclusivas.values())

    return ComparacaoMST(
        resultados=resultados,
        custos_equivalentes=custos_equivalentes,
        diferenca_custo=diferenca_custo,
        arestas_comuns=tuple(sorted(comuns)),
        arestas_exclusivas=exclusivas,
        algoritmo_mais_rapido=mais_rapido,
        houve_empate_de_arestas=houve_empate,
    )


def gerar_grafo_aleatorio(num_vertices, densidade=1.0, semente=None, peso_maximo=100.0):
    if num_vertices < 1:
        raise ValueError("O grafo aleatorio precisa de pelo menos um vertice.")
    if not 0.0 <= densidade <= 1.0:
        raise ValueError("A densidade deve estar entre 0.0 e 1.0.")

    sorteador = random.Random(semente)
    grafo = Grafo(num_vertices)

    for vertice in range(1, num_vertices):
        anterior = sorteador.randrange(vertice)
        grafo.adicionar_aresta(anterior, vertice, sorteador.uniform(1.0, peso_maximo))

    existentes = {(min(a.origem, a.destino), max(a.origem, a.destino)) for a in grafo.arestas}
    candidatas = [
        (i, j)
        for i in range(num_vertices)
        for j in range(i + 1, num_vertices)
        if (i, j) not in existentes
    ]
    sorteador.shuffle(candidatas)

    maximo = num_vertices * (num_vertices - 1) // 2
    alvo = int(round(densidade * maximo))
    faltam = max(0, alvo - len(existentes))

    for origem, destino in candidatas[:faltam]:
        grafo.adicionar_aresta(origem, destino, sorteador.uniform(1.0, peso_maximo))

    return grafo


def executar_benchmark(tamanhos, densidade=1.0, semente=42, repeticoes=3):
    if repeticoes < 1:
        raise ValueError("O benchmark precisa de pelo menos uma repeticao.")

    linhas = []
    for tamanho in tamanhos:
        grafo = gerar_grafo_aleatorio(tamanho, densidade=densidade, semente=semente)

        tempos = {nome: [] for nome in ALGORITMOS}
        ultimos = {}
        for _ in range(repeticoes):
            for nome, funcao in ALGORITMOS.items():
                resultado = funcao(grafo)
                tempos[nome].append(resultado.tempo_ms)
                ultimos[nome] = resultado

        custos = [resultado.custo_total for resultado in ultimos.values()]
        linha = {
            "Vertices": grafo.num_vertices,
            "Arestas": grafo.num_arestas,
            "Custo Kruskal": round(ultimos["Kruskal"].custo_total, 4),
            "Custo Prim": round(ultimos["Prim"].custo_total, 4),
            "Custos iguais": math.isclose(
                max(custos), min(custos), rel_tol=1e-9, abs_tol=TOLERANCIA_CUSTO
            ),
        }
        for nome in ALGORITMOS:
            linha[f"Tempo {nome} (ms)"] = round(sum(tempos[nome]) / repeticoes, 4)
        linhas.append(linha)

    return linhas
