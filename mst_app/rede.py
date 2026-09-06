import math
from dataclasses import dataclass, field

from analise import comparar_algoritmos
from geo import coordenada_valida, haversine, matriz_haversine
from grafo import Grafo
from rotas import ErroDeRotas, baixar_grafo_area, caminho_entre_nos, matriz_distancias_km

MODO_ROTA = "rota"
MODO_HAVERSINE = "haversine"
MODOS = (MODO_ROTA, MODO_HAVERSINE)

MINIMO_DE_ESTACOES = 2
DISTANCIA_MINIMA_KM = 0.005


class ErroDeRede(Exception):
    pass


@dataclass
class Estacao:
    id: int
    nome: str
    lat: float
    lon: float

    @property
    def coordenada(self):
        return (self.lat, self.lon)

    def como_dict(self):
        return {"id": self.id, "nome": self.nome, "lat": self.lat, "lon": self.lon}

    @classmethod
    def de_dict(cls, dados):
        return cls(
            id=int(dados["id"]),
            nome=str(dados["nome"]),
            lat=float(dados["lat"]),
            lon=float(dados["lon"]),
        )


@dataclass(frozen=True)
class Conexao:
    origem: int
    destino: int
    distancia_km: float
    caminho: tuple
    rota_real: bool


@dataclass(frozen=True)
class RedeConstruida:
    estacoes: tuple
    grafo: Grafo
    resultado: object
    comparacao: object
    conexoes: tuple
    modo: str
    tipo_rede: str
    custo_por_km: float
    pares_sem_conexao: tuple = field(default_factory=tuple)

    @property
    def algoritmo(self):
        return self.resultado.algoritmo

    @property
    def distancia_total_km(self):
        return self.resultado.custo_total

    @property
    def custo_total(self):
        return self.resultado.custo_total * self.custo_por_km

    @property
    def usa_rotas_reais(self):
        return self.modo == MODO_ROTA

    def nome_da_estacao(self, indice):
        return self.estacoes[indice].nome

    def conexoes_por_estacao(self, indice):
        return [c for c in self.conexoes if indice in (c.origem, c.destino)]


def proximo_id(estacoes):
    return max((estacao.id for estacao in estacoes), default=-1) + 1


def criar_estacao(estacoes, lat, lon, nome=None):
    if not coordenada_valida(lat, lon):
        raise ErroDeRede("Coordenada invalida. Latitude entre -90 e 90, longitude entre -180 e 180.")

    lat, lon = float(lat), float(lon)
    if estacao_proxima(estacoes, lat, lon) is not None:
        raise ErroDeRede("Ja existe uma estacao praticamente nessa posicao.")

    identificador = proximo_id(estacoes)
    return Estacao(
        id=identificador,
        nome=nome.strip() if nome and nome.strip() else f"Estacao {identificador + 1}",
        lat=lat,
        lon=lon,
    )


def estacao_proxima(estacoes, lat, lon, limite_km=DISTANCIA_MINIMA_KM):
    for estacao in estacoes:
        if haversine(estacao.lat, estacao.lon, lat, lon) < limite_km:
            return estacao
    return None


def validar_estacoes(estacoes):
    if len(estacoes) < MINIMO_DE_ESTACOES:
        raise ErroDeRede(
            f"Sao necessarias pelo menos {MINIMO_DE_ESTACOES} estacoes para construir a rede."
        )
    for estacao in estacoes:
        if not coordenada_valida(estacao.lat, estacao.lon):
            raise ErroDeRede(f"A estacao '{estacao.nome}' possui coordenada invalida.")


def pares_inalcancaveis(matriz):
    total = len(matriz)
    return tuple(
        (i, j)
        for i in range(total)
        for j in range(i + 1, total)
        if matriz[i][j] is None or math.isinf(matriz[i][j])
    )


def montar_rede(
    estacoes,
    algoritmo="Kruskal",
    modo=MODO_ROTA,
    custo_por_km=0.0,
    margem_km=0.5,
    tipo_rede="drive",
    obter_grafo_ruas=None,
):
    if modo not in MODOS:
        raise ErroDeRede(f"Modo de distancia invalido: {modo}.")

    estacoes = tuple(estacoes)
    validar_estacoes(estacoes)
    pontos = [estacao.coordenada for estacao in estacoes]

    grafo_ruas = None
    nos = None

    if modo == MODO_ROTA:
        carregar = obter_grafo_ruas or (
            lambda pontos_alvo: baixar_grafo_area(
                pontos_alvo, margem_km=margem_km, tipo_rede=tipo_rede
            )
        )
        grafo_ruas = carregar(pontos)
        matriz, nos = matriz_distancias_km(grafo_ruas, pontos)
    else:
        matriz = matriz_haversine(pontos)

    faltantes = pares_inalcancaveis(matriz)
    grafo = Grafo.de_matriz(matriz)

    if grafo.num_arestas == 0:
        raise ErroDeRede(
            "Nenhuma conexao pode ser calculada entre as estacoes selecionadas."
        )

    comparacao = comparar_algoritmos(grafo)
    if algoritmo not in comparacao.resultados:
        raise ErroDeRede(f"Algoritmo '{algoritmo}' nao esta disponivel.")
    resultado = comparacao.resultados[algoritmo]

    conexoes = montar_conexoes(estacoes, resultado, matriz, grafo_ruas, nos)

    return RedeConstruida(
        estacoes=estacoes,
        grafo=grafo,
        resultado=resultado,
        comparacao=comparacao,
        conexoes=tuple(conexoes),
        modo=modo,
        tipo_rede=tipo_rede if modo == MODO_ROTA else "-",
        custo_por_km=float(custo_por_km),
        pares_sem_conexao=faltantes,
    )


def montar_conexoes(estacoes, resultado, matriz, grafo_ruas=None, nos=None):
    conexoes = []
    for aresta in resultado.arestas:
        origem, destino = aresta.origem, aresta.destino
        caminho = None
        rota_real = False

        if grafo_ruas is not None and nos is not None:
            try:
                caminho = caminho_entre_nos(grafo_ruas, nos[origem], nos[destino])
            except ErroDeRotas:
                caminho = None
            rota_real = caminho is not None

        if caminho is None:
            caminho = [estacoes[origem].coordenada, estacoes[destino].coordenada]

        conexoes.append(
            Conexao(
                origem=origem,
                destino=destino,
                distancia_km=matriz[origem][destino],
                caminho=tuple(caminho),
                rota_real=rota_real,
            )
        )
    return conexoes


def arestas_candidatas(rede, limite=60):
    selecionadas = {
        (min(c.origem, c.destino), max(c.origem, c.destino)) for c in rede.conexoes
    }
    candidatas = [
        aresta
        for aresta in rede.grafo.arestas
        if (min(aresta.origem, aresta.destino), max(aresta.origem, aresta.destino))
        not in selecionadas
    ]
    candidatas.sort(key=lambda a: a.peso)
    return candidatas[:limite]
