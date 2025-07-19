import requests

def get_osrm_matrix(coordinates, host='localhost', port=5000, annotation='distance'):
    """
    Retorna matriz de custos (distâncias ou durações) entre coordenadas usando a OSRM Table API.

    :param coordinates: lista de tuplas (lon, lat)
    :param host: endereço do host OSRM
    :param port: porta do serviço OSRM
    :param annotation: 'distance' (metros) ou 'duration' (segundos)
    :return: matriz NxN de valores de custos
    """
    # Monta string de coordenadas no formato 'lon,lat;lon,lat;...'
    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coordinates)
    url = f"http://{host}:{port}/table/v1/driving/{coords_str}?annotations={annotation}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    key = 'distances' if annotation == 'distance' else 'durations'
    return data[key]


def get_route_segment(coord1, coord2, osrm_url="http://localhost:5000"):
    """
    Retorna detalhes do segmento de rota entre duas coordenadas usando a OSRM Route API.

    :param coord1: tupla (lon, lat) do ponto de partida
    :param coord2: tupla (lon, lat) do ponto de chegada
    :param osrm_url: URL base do serviço OSRM
    :return: tuple (geometry, distance, duration) ou None se não encontrar rota
    """
    coords = f"{coord1[0]},{coord1[1]};{coord2[0]},{coord2[1]}"
    url = f"{osrm_url}/route/v1/driving/{coords}?overview=full&geometries=geojson"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    if data.get("routes"):
        route = data["routes"][0]
        return route["geometry"]["coordinates"], route["distance"], route["duration"]
    return None
