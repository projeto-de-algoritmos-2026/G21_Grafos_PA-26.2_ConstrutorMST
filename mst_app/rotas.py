import networkx as nx
import osmnx as ox


def baixar_grafo_ruas(centro, raio_m=3000, tipo_rede="drive"):
    lat, lon = centro
    return ox.graph_from_point((lat, lon), dist=raio_m, network_type=tipo_rede)


def baixar_grafo_area(pontos, margem_km=0.5, tipo_rede="drive"):
    lats = [lat for lat, _ in pontos]
    lons = [lon for _, lon in pontos]

    margem_graus = margem_km / 111.0
    bbox = (
        min(lons) - margem_graus,
        min(lats) - margem_graus,
        max(lons) + margem_graus,
        max(lats) + margem_graus,
    )
    return ox.graph_from_bbox(bbox, network_type=tipo_rede)


def distancia_rota_km(grafo_ruas, origem, destino):
    lat1, lon1 = origem
    lat2, lon2 = destino

    no_origem = ox.nearest_nodes(grafo_ruas, X=lon1, Y=lat1)
    no_destino = ox.nearest_nodes(grafo_ruas, X=lon2, Y=lat2)

    distancia_m = nx.shortest_path_length(grafo_ruas, no_origem, no_destino, weight="length")
    return distancia_m / 1000


def caminho_rota(grafo_ruas, origem, destino):
    lat1, lon1 = origem
    lat2, lon2 = destino

    no_origem = ox.nearest_nodes(grafo_ruas, X=lon1, Y=lat1)
    no_destino = ox.nearest_nodes(grafo_ruas, X=lon2, Y=lat2)

    caminho_nos = nx.shortest_path(grafo_ruas, no_origem, no_destino, weight="length")
    return [(grafo_ruas.nodes[no]["y"], grafo_ruas.nodes[no]["x"]) for no in caminho_nos]
