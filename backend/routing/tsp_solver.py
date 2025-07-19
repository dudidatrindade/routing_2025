# tsp_solver.py
from .osrm_utils import get_osrm_matrix
from .coordinates import COORDINATES
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def solve_tsp(filtered_indices=None, sensor_data=None, beta=0.0,
              osrm_host='localhost', osrm_port=5000, annotation='distance'):
    """
    Resolve o problema do caixeiro viajante (TSP) usando custos reais obtidos da OSRM Table API.

    :param filtered_indices: lista de índices de COORDINATES a incluir (None para todos)
    :param sensor_data: dict {sensor_id: volume} para ajustar custos
    :param beta: fator de ponderação de volume (>=0)
    :param osrm_host: host do serviço OSRM
    :param osrm_port: porta do serviço OSRM
    :param annotation: 'distance' (metros) ou 'duration' (segundos)
    :return: lista de índices representando a rota otimizada
    """
    # Seleciona pontos e mapa de índices originais
    if filtered_indices is None:
        points = COORDINATES
        index_map = list(range(len(COORDINATES)))
    else:
        points = [COORDINATES[i] for i in filtered_indices]
        index_map = filtered_indices

    n = len(points)
    # Obtém matriz de custos reais (distância ou duração)
    cost_matrix = get_osrm_matrix(points, host=osrm_host,
                                  port=osrm_port,
                                  annotation=annotation)

    # Ajusta custos com base nos volumes de sensores e beta
    if sensor_data and beta > 0:
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                sid_i = f"lixeira_{index_map[i]+1:02d}"
                sid_j = f"lixeira_{index_map[j]+1:02d}"
                vol_i = sensor_data.get(sid_i, 0)
                vol_j = sensor_data.get(sid_j, 0)
                cost_matrix[i][j] = (
                    cost_matrix[i][j] /
                    (1 + beta * max(vol_i, vol_j))
                )
    # Converte custos para inteiros (requisito OR-Tools)
    for i in range(n):
        for j in range(n):
            cost_matrix[i][j] = int(cost_matrix[i][j])

    # Configura o OR-Tools
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def cost_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return cost_matrix[from_node][to_node]

    transit_index = routing.RegisterTransitCallback(cost_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)

    # Parâmetros de busca aprimorados
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    # Estratégia inicial global
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC
    )
    # Meta-heurística para refinamento
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    # Limite de tempo para busca local (segundos)
    search_params.time_limit.seconds = 10
    # Habilita logs de busca no console
    search_params.log_search = True

    # Resolve o TSP
    solution = routing.SolveWithParameters(search_params)
    if not solution:
        return None

    # Extrai a rota otimizada
    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(manager.IndexToNode(index))

    # Retorna índices originais de COORDINATES
    return [index_map[node] for node in route]
