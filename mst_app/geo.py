import math

RAIO_TERRA_KM = 6371.0
KM_POR_GRAU_LATITUDE = 111.0


def haversine(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return RAIO_TERRA_KM * c


def coordenada_valida(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return False
    if math.isnan(lat) or math.isnan(lon) or math.isinf(lat) or math.isinf(lon):
        return False
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def validar_pontos(pontos):
    if not pontos:
        raise ValueError("Nenhum ponto informado.")
    for lat, lon in pontos:
        if not coordenada_valida(lat, lon):
            raise ValueError(f"Coordenada invalida: ({lat}, {lon}).")


def centro_geografico(pontos):
    validar_pontos(pontos)
    lat = sum(p[0] for p in pontos) / len(pontos)
    lon = sum(p[1] for p in pontos) / len(pontos)
    return (lat, lon)


def limites(pontos):
    validar_pontos(pontos)
    lats = [p[0] for p in pontos]
    lons = [p[1] for p in pontos]
    return (min(lats), min(lons), max(lats), max(lons))


def graus_por_km_longitude(latitude):
    fator = math.cos(math.radians(latitude))
    return 1.0 / (KM_POR_GRAU_LATITUDE * max(abs(fator), 0.1))


def caixa_delimitadora(pontos, margem_km=0.5, lado_minimo_km=1.0):
    sul, oeste, norte, leste = limites(pontos)
    latitude_media = (sul + norte) / 2

    margem_lat = margem_km / KM_POR_GRAU_LATITUDE
    margem_lon = margem_km * graus_por_km_longitude(latitude_media)

    lado_minimo_lat = lado_minimo_km / KM_POR_GRAU_LATITUDE
    lado_minimo_lon = lado_minimo_km * graus_por_km_longitude(latitude_media)

    falta_lat = max(0.0, lado_minimo_lat - (norte - sul)) / 2
    falta_lon = max(0.0, lado_minimo_lon - (leste - oeste)) / 2

    return (
        oeste - margem_lon - falta_lon,
        sul - margem_lat - falta_lat,
        leste + margem_lon + falta_lon,
        norte + margem_lat + falta_lat,
    )


def matriz_haversine(pontos):
    validar_pontos(pontos)
    total = len(pontos)
    matriz = [[0.0] * total for _ in range(total)]
    for i in range(total):
        for j in range(i + 1, total):
            distancia = haversine(pontos[i][0], pontos[i][1], pontos[j][0], pontos[j][1])
            matriz[i][j] = distancia
            matriz[j][i] = distancia
    return matriz
