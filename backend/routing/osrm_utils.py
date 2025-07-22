import os
import requests

# Busca a URL base do OSRM a partir da variável de ambiente ou usa o serviço Docker "osrm"
OSRM_BASE = os.environ.get("OSRM_URL", "http://osrm:5000").rstrip('/')


def get_osrm_matrix(coordinates, annotation='distance'):
    """
    Retorna matriz de custos (distâncias ou durações) entre coordenadas usando a OSRM Table API.

    :param coordinates: lista de tuplas (lon, lat)
    :param annotation: 'distance' (metros) ou 'duration' (segundos)
    :return: matriz NxN de valores de custos
    """
    # Monta string de coordenadas no formato 'lon,lat;lon,lat;...'
    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coordinates)
    url = f"{OSRM_BASE}/table/v1/driving/{coords_str}"
    params = {"annotations": annotation}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    key = 'distances' if annotation == 'distance' else 'durations'
    return data.get(key, [])


def get_route_segment(coord1, coord2):
    """
    Retorna detalhes do segmento de rota entre duas coordenadas usando a OSRM Route API.

    :param coord1: tupla (lon, lat) do ponto de partida
    :param coord2: tupla (lon, lat) do ponto de chegada
    :return: tuple (geometry, distance, duration) ou None se não encontrar rota
    """
    coords = f"{coord1[0]},{coord1[1]};{coord2[0]},{coord2[1]}"
    url = f"{OSRM_BASE}/route/v1/driving/{coords}"
    params = {"overview": "full", "geometries": "geojson"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    routes = data.get("routes")
    if routes:
        route = routes[0]
        return route["geometry"]["coordinates"], route["distance"], route["duration"]
    return None
