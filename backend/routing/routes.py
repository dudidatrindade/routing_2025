import os
import json
import folium
from folium.plugins import PolyLineTextPath
from folium import Element
from flask import Blueprint, request, jsonify, send_from_directory
from .tsp_solver import solve_tsp
from .coordinates import COORDINATES
from .osrm_utils import get_route_segment
from backend.sensor_control.influx_client import get_sensor_data
import datetime

routes = Blueprint('routes', __name__)

def get_marker_color(volume):
    """Retorna a cor do marcador com base no valor do volume."""
    if volume < 40:
        return 'green'
    elif volume < 70:
        return 'orange'
    else:
        return 'red'

@routes.route('/api/mapa', methods=['GET'])
def get_mapa():
    # Parâmetros de consulta
    min_volume = request.args.get('min_volume', default=None, type=int)
    prioritize = request.args.get('prioritize', default=0, type=int)
    
    # Busca os dados dos sensores do InfluxDB
    try:
        sensor_records = get_sensor_data()  # Retorna uma lista de registros
        sensor_data = {}
        for record in sensor_records:
            sensor_data[record['sensor_id']] = {
                'fill_percentage': record['fill_percentage'],
                'time': record['time']
            }
    except Exception as e:
        sensor_data = {}
        print("Erro ao consultar o InfluxDB:", e)
    
    # Filtra os pontos para o cálculo da rota
    filtered_indices = []
    for i, coord in enumerate(COORDINATES):
        sensor_id = f"lixeira_{i+1:02d}"
        volume = sensor_data.get(sensor_id, {'fill_percentage': 0})['fill_percentage']
        if min_volume is None or volume >= min_volume:
            filtered_indices.append(i)
    
    if len(filtered_indices) < 2:
        return jsonify({"status": "fail", "message": "Poucos pontos com volume acima do threshold"}), 500

    # Calcula a rota
    if prioritize == 1:
        beta = request.args.get('beta', default=0.01, type=float)
        route = solve_tsp(filtered_indices,
                          {k: v['fill_percentage'] for k, v in sensor_data.items()},
                          beta)
    else:
        route = solve_tsp(filtered_indices)
    
    if route is None:
        return jsonify({"status": "fail", "message": "Nenhuma solução encontrada"}), 500

    # Gera o mapa centralizado no primeiro ponto da rota
    first_coord = COORDINATES[route[0]]
    m = folium.Map(location=[first_coord[1], first_coord[0]],
                   zoom_start=12, tiles=None)
    folium.TileLayer('CartoDB positron', name='Positron').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Matter').add_to(m)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    folium.LayerControl().add_to(m)

    total_distance = 0  # Em metros
    total_duration = 0  # Em segundos

    # Desenha TODOS os pontos do COORDINATES
    for i, coord in enumerate(COORDINATES):
        sensor_id = f"lixeira_{i+1:02d}"
        info = sensor_data.get(sensor_id, {'fill_percentage': 0, 'time': None})
        volume = info['fill_percentage']
        time_str = info['time'].strftime("%d/%m/%Y %H:%M:%S") if hasattr(info['time'], 'strftime') else "N/A"
        color = get_marker_color(volume)
        tooltip_html = (
            f"<span style='font-size:10px;'>ID: {sensor_id}</span><br>"
            f"<span style='font-size:10px;'>Coord: ({coord[1]:.4f}, {coord[0]:.4f})</span><br>"
            f"<span style='font-size:14px; font-weight:bold;'>Volume: {volume}</span><br>"
            f"<small>Atualizado em: {time_str}</small>"
        )
        if i in route:
            ordem = route.index(i) + 1
            folium.Marker(
                location=[coord[1], coord[0]],
                tooltip=folium.Tooltip(tooltip_html, parse_html=True),
                icon=folium.DivIcon(html=f"""
                    <div style="
                        background-color: {color};
                        color: #fff;
                        font-size: 12px;
                        font-weight: bold;
                        text-align: center;
                        border-radius: 50%;
                        width: 24px;
                        height: 24px;
                        line-height: 24px;
                        border: 2px solid #fff;">
                        {ordem}
                    </div>
                    """
                )
            ).add_to(m)
        else:
            folium.CircleMarker(
                location=[coord[1], coord[0]],
                radius=4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                tooltip=folium.Tooltip(tooltip_html, parse_html=True)
            ).add_to(m)

    # Desenha os segmentos da rota
    for a, b in zip(route, route[1:]):
        seg = get_route_segment(COORDINATES[a], COORDINATES[b])
        if seg:
            geometry, dist, dur = seg
            total_distance += dist
            total_duration += dur
            polyline_points = [[pt[1], pt[0]] for pt in geometry]
            line = folium.PolyLine(locations=polyline_points,
                                   color='green', weight=5, opacity=0.5)
            line.add_to(m)
            PolyLineTextPath(line, ' ► ', repeat=True,
                             offset=7,
                             attributes={'font-size': '16', 'fill': 'green'}
            ).add_to(m)

    # Calcula métricas e adiciona rodapé
    total_km = total_distance / 1000.0
    total_minutes = total_duration / 60.0
    fuel_consumption = total_km * 8 / 100.0
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    info_message = (
        f"Tempo total: {total_minutes:.1f} min | "
        f"Distância: {total_km:.1f} km | "
        f"Combustível: {fuel_consumption:.1f} L | "
        f"Mapa gerado em: {now}"
    )
    footer_html = f"""
    <div style="
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        font-size: 14px;
        color: #fff;
        background-color: rgba(0, 0, 0, 0.85);
        padding: 10px 15px;
        border-radius: 5px;
        white-space: nowrap;
        ">
        {info_message}
    </div>
    """
    m.get_root().html.add_child(Element(footer_html))

    # Salva o mapa
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_folder = os.path.join(base_dir, '..', 'static')
    map_folder = os.path.join(static_folder, 'map')
    if not os.path.exists(map_folder):
        os.makedirs(map_folder)
    map_file_name = "mapa_interativo.html"
    map_file_path = os.path.join(map_folder, map_file_name)
    m.save(map_file_path)

    return jsonify({"status": "success", "map_file": "map/" + map_file_name}), 200

@routes.route('/static/<path:filename>')
def serve_static(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_folder = os.path.join(base_dir, '..', 'static')
    return send_from_directory(static_folder, filename)
