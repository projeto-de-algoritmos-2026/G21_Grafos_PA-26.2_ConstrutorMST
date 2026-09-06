from grafo import Grafo

GRAFOS_DIDATICOS = {
    "Triangulo": {
        "descricao": "Menor caso nao trivial: a aresta mais cara e descartada.",
        "rotulos": ["A", "B", "C"],
        "arestas": [(0, 1, 1), (1, 2, 1), (0, 2, 5)],
        "custo_esperado": 2.0,
        "conexo": True,
    },
    "Vertice unico": {
        "descricao": "Caso limite: a MST de um unico vertice e vazia e tem custo zero.",
        "rotulos": ["A"],
        "arestas": [],
        "custo_esperado": 0.0,
        "conexo": True,
    },
    "Pesos iguais": {
        "descricao": "Todos os pesos iguais: qualquer arvore geradora e otima e os empates aparecem.",
        "rotulos": ["A", "B", "C", "D"],
        "arestas": [(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 0, 2), (0, 2, 2)],
        "custo_esperado": 6.0,
        "conexo": True,
    },
    "Grafo classico de 9 vertices": {
        "descricao": "Grafo classico de livro-texto usado para demonstrar Kruskal e Prim.",
        "rotulos": ["a", "b", "c", "d", "e", "f", "g", "h", "i"],
        "arestas": [
            (0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 11), (2, 3, 7),
            (2, 8, 2), (2, 5, 4), (3, 4, 9), (3, 5, 14), (4, 5, 10),
            (5, 6, 2), (6, 7, 1), (6, 8, 6), (7, 8, 7),
        ],
        "custo_esperado": 37.0,
        "conexo": True,
    },
    "Grafo desconexo": {
        "descricao": "Duas componentes separadas: os algoritmos devolvem uma floresta geradora minima.",
        "rotulos": ["A", "B", "C", "D", "E"],
        "arestas": [(0, 1, 1), (0, 2, 3), (1, 2, 2), (3, 4, 4)],
        "custo_esperado": 7.0,
        "conexo": False,
    },
}

ESTACOES_DEMONSTRACAO = [
    {"nome": "Rodoviaria do Plano Piloto", "lat": -15.7940, "lon": -47.8828},
    {"nome": "Torre de TV", "lat": -15.7901, "lon": -47.8929},
    {"nome": "Catedral de Brasilia", "lat": -15.7983, "lon": -47.8756},
    {"nome": "Estadio Mane Garrincha", "lat": -15.7835, "lon": -47.8993},
    {"nome": "Parque da Cidade", "lat": -15.7975, "lon": -47.9075},
]


def construir_grafo_didatico(nome):
    if nome not in GRAFOS_DIDATICOS:
        raise ValueError(f"Exemplo '{nome}' nao encontrado.")
    dados = GRAFOS_DIDATICOS[nome]
    return Grafo(len(dados["rotulos"]), dados["arestas"])


def rotulos_do_exemplo(nome):
    if nome not in GRAFOS_DIDATICOS:
        raise ValueError(f"Exemplo '{nome}' nao encontrado.")
    return list(GRAFOS_DIDATICOS[nome]["rotulos"])
