import math

import networkx as nx
import osmnx as ox

from geo import caixa_delimitadora, validar_pontos

TIPOS_DE_REDE = ("drive", "walk", "bike", "all")


class ErroDeRotas(Exception):
    pass


def baixar_grafo_ruas(centro, raio_m=3000, tipo_rede="drive"):
    if tipo_rede not in TIPOS_DE_REDE:
        raise ValueError(f"Tipo de rede invalido: {tipo_rede}.")
    if raio_m <= 0:
        raise ValueError("O raio deve ser positivo.")

    lat, lon = centro
    try:
        return ox.graph_from_point((lat, lon), dist=raio_m, network_type=tipo_rede)
    except Exception as erro:
        raise ErroDeRotas(f"Nao foi possivel baixar as ruas da regiao: {erro}") from erro


def baixar_grafo_area(pontos, margem_km=0.5, tipo_rede="drive"):
    if tipo_rede not in TIPOS_DE_REDE:
        raise ValueError(f"Tipo de rede invalido: {tipo_rede}.")
    validar_pontos(pontos)

    bbox = caixa_delimitadora(pontos, margem_km=margem_km)
    try:
        grafo_ruas = ox.graph_from_bbox(bbox, network_type=tipo_rede)
    except Exception as erro:
        raise ErroDeRotas(f"Nao foi possivel baixar as ruas da regiao: {erro}") from erro

    if grafo_ruas.number_of_nodes() == 0:
        raise ErroDeRotas("A regiao selecionada nao possui vias mapeadas no OpenStreetMap.")

    return grafo_ruas


def nos_mais_proximos(grafo_ruas, pontos):
    validar_pontos(pontos)
    try:
        retorno = ox.nearest_nodes(
            grafo_ruas,
            X=[float(lon) for _, lon in pontos],
            Y=[float(lat) for lat, _ in pontos],
        )
    except Exception as erro:
        raise ErroDeRotas(f"Nao foi possivel localizar as estacoes nas vias: {erro}") from erro

    return [int(no) for no in retorno]


def matriz_distancias_km(grafo_ruas, pontos):
    nos = nos_mais_proximos(grafo_ruas, pontos)
    total = len(nos)
    matriz = [[math.inf] * total for _ in range(total)]

    distancias_por_no = {}
    for no in set(nos):
        distancias_por_no[no] = nx.single_source_dijkstra_path_length(
            grafo_ruas, no, weight="length"
        )

    for i in range(total):
        matriz[i][i] = 0.0
        for j in range(i + 1, total):
            ida = distancias_por_no[nos[i]].get(nos[j], math.inf)
            volta = distancias_por_no[nos[j]].get(nos[i], math.inf)
            metros = min(ida, volta)
            distancia = math.inf if math.isinf(metros) else metros / 1000
            matriz[i][j] = distancia
            matriz[j][i] = distancia

    return matriz, nos


def caminho_entre_nos(grafo_ruas, no_origem, no_destino):
    if no_origem == no_destino:
        coordenada = (grafo_ruas.nodes[no_origem]["y"], grafo_ruas.nodes[no_origem]["x"])
        return [coordenada, coordenada]

    try:
        caminho_nos = nx.shortest_path(grafo_ruas, no_origem, no_destino, weight="length")
    except nx.NetworkXNoPath:
        try:
            caminho_nos = nx.shortest_path(grafo_ruas, no_destino, no_origem, weight="length")
        except nx.NetworkXNoPath:
            return None
    except nx.NodeNotFound as erro:
        raise ErroDeRotas(f"Estacao fora da area de ruas baixada: {erro}") from erro

    return [(grafo_ruas.nodes[no]["y"], grafo_ruas.nodes[no]["x"]) for no in caminho_nos]


def distancia_rota_km(grafo_ruas, origem, destino):
    nos = nos_mais_proximos(grafo_ruas, [origem, destino])
    try:
        distancia_m = nx.shortest_path_length(grafo_ruas, nos[0], nos[1], weight="length")
    except nx.NetworkXNoPath as erro:
        raise ErroDeRotas("Nao existe rota entre os pontos informados.") from erro
    return distancia_m / 1000


def caminho_rota(grafo_ruas, origem, destino):
    nos = nos_mais_proximos(grafo_ruas, [origem, destino])
    caminho = caminho_entre_nos(grafo_ruas, nos[0], nos[1])
    if caminho is None:
        raise ErroDeRotas("Nao existe rota entre os pontos informados.")
    return caminho
