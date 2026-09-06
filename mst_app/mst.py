from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResultadoMST:
    algoritmo: str
    arestas: tuple
    custo_total: float
    num_vertices: int
    num_arestas_grafo: int
    componentes: int
    tempo_execucao: float
    operacoes: dict = field(default_factory=dict)

    @property
    def num_arestas_mst(self):
        return len(self.arestas)

    @property
    def conexo(self):
        return self.componentes == 1

    @property
    def e_arvore_geradora(self):
        return self.conexo and self.num_arestas_mst == max(self.num_vertices - 1, 0)

    @property
    def e_floresta(self):
        return self.componentes > 1

    @property
    def peso_medio(self):
        if not self.arestas:
            return 0.0
        return self.custo_total / len(self.arestas)

    @property
    def menor_aresta(self):
        return min(self.arestas, key=lambda a: a.peso) if self.arestas else None

    @property
    def maior_aresta(self):
        return max(self.arestas, key=lambda a: a.peso) if self.arestas else None

    @property
    def tempo_ms(self):
        return self.tempo_execucao * 1000

    def como_par(self):
        return list(self.arestas), self.custo_total

    def resumo(self):
        return {
            "algoritmo": self.algoritmo,
            "vertices": self.num_vertices,
            "arestas_do_grafo": self.num_arestas_grafo,
            "arestas_da_mst": self.num_arestas_mst,
            "custo_total": self.custo_total,
            "componentes": self.componentes,
            "conexo": self.conexo,
            "arvore_geradora": self.e_arvore_geradora,
            "tempo_ms": self.tempo_ms,
            "operacoes": dict(self.operacoes),
        }


def criar_resultado(algoritmo, grafo, arestas, custo_total, componentes, tempo_execucao, operacoes):
    return ResultadoMST(
        algoritmo=algoritmo,
        arestas=tuple(arestas),
        custo_total=custo_total,
        num_vertices=grafo.num_vertices,
        num_arestas_grafo=grafo.num_arestas,
        componentes=componentes,
        tempo_execucao=tempo_execucao,
        operacoes=operacoes,
    )
