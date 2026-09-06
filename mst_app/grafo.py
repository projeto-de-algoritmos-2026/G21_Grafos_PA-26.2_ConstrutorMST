import math
from collections import deque
from typing import NamedTuple


class Aresta(NamedTuple):
    origem: int
    destino: int
    peso: float


class UnionFind:
    def __init__(self, n):
        if n < 0:
            raise ValueError("O numero de elementos nao pode ser negativo.")
        self.pai = list(range(n))
        self.rank = [0] * n
        self.componentes = n
        self.passos_find = 0
        self.chamadas_find = 0
        self.unioes_efetivadas = 0

    def _validar(self, x):
        if not isinstance(x, int) or x < 0 or x >= len(self.pai):
            raise IndexError(f"Elemento {x} fora do intervalo do Union-Find.")

    def find(self, x):
        self._validar(x)
        self.chamadas_find += 1

        raiz = x
        while self.pai[raiz] != raiz:
            self.passos_find += 1
            raiz = self.pai[raiz]

        atual = x
        while self.pai[atual] != raiz:
            self.pai[atual], atual = raiz, self.pai[atual]

        return raiz

    def union(self, x, y):
        raiz_x, raiz_y = self.find(x), self.find(y)
        if raiz_x == raiz_y:
            return False

        if self.rank[raiz_x] < self.rank[raiz_y]:
            raiz_x, raiz_y = raiz_y, raiz_x
        self.pai[raiz_y] = raiz_x
        if self.rank[raiz_x] == self.rank[raiz_y]:
            self.rank[raiz_x] += 1

        self.componentes -= 1
        self.unioes_efetivadas += 1
        return True

    def conectados(self, x, y):
        return self.find(x) == self.find(y)


class Grafo:
    def __init__(self, num_vertices, arestas=None):
        if not isinstance(num_vertices, int) or num_vertices < 0:
            raise ValueError("O numero de vertices deve ser um inteiro nao negativo.")

        self.num_vertices = num_vertices
        self._arestas = []
        self._adjacencia = [[] for _ in range(num_vertices)]

        for aresta in arestas or []:
            origem, destino, peso = aresta
            self.adicionar_aresta(origem, destino, peso)

    def _validar_vertice(self, v):
        if not isinstance(v, int) or v < 0 or v >= self.num_vertices:
            raise ValueError(f"Vertice {v} fora do intervalo [0, {self.num_vertices - 1}].")

    def adicionar_aresta(self, origem, destino, peso):
        self._validar_vertice(origem)
        self._validar_vertice(destino)

        peso = float(peso)
        if math.isnan(peso) or math.isinf(peso):
            raise ValueError("O peso da aresta deve ser um numero finito.")

        aresta = Aresta(origem, destino, peso)
        self._arestas.append(aresta)
        if origem != destino:
            self._adjacencia[origem].append((destino, peso))
            self._adjacencia[destino].append((origem, peso))
        return aresta

    @property
    def arestas(self):
        return tuple(self._arestas)

    @property
    def num_arestas(self):
        return len(self._arestas)

    def vizinhos(self, v):
        self._validar_vertice(v)
        return tuple(self._adjacencia[v])

    def lista_adjacencia(self):
        return self._adjacencia

    def grau(self, v):
        self._validar_vertice(v)
        return len(self._adjacencia[v])

    def componentes(self):
        visitado = [False] * self.num_vertices
        grupos = []

        for inicio in range(self.num_vertices):
            if visitado[inicio]:
                continue
            visitado[inicio] = True
            fila = deque([inicio])
            grupo = []
            while fila:
                atual = fila.popleft()
                grupo.append(atual)
                for vizinho, _ in self._adjacencia[atual]:
                    if not visitado[vizinho]:
                        visitado[vizinho] = True
                        fila.append(vizinho)
            grupos.append(sorted(grupo))

        return grupos

    def num_componentes(self):
        return len(self.componentes())

    def conexo(self):
        return self.num_componentes() == 1

    def densidade(self):
        if self.num_vertices < 2:
            return 0.0
        maximo = self.num_vertices * (self.num_vertices - 1) / 2
        return self.num_arestas / maximo

    @classmethod
    def de_lista(cls, num_vertices, arestas):
        return cls(num_vertices, arestas)

    @classmethod
    def de_matriz(cls, matriz, limite_superior=math.inf):
        total = len(matriz)
        grafo = cls(total)
        for i in range(total):
            for j in range(i + 1, total):
                peso = matriz[i][j]
                if peso is None or math.isinf(peso) or math.isnan(peso) or peso > limite_superior:
                    continue
                grafo.adicionar_aresta(i, j, peso)
        return grafo
