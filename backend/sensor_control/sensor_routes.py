# sensor_routes.py
from flask import Blueprint, jsonify, request
from .influx_client import get_sensor_data
from .influx_client import get_sensor_history
from .mqtt_client import publish_message
import json

sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/sensores', methods=['GET'])
def get_sensors():
    try:
        data = get_sensor_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"status": "erro", "message": str(e)}), 500

@sensor_bp.route('/atualizar', methods=['POST'])
def atualizar_sensor():
    sensor_id = request.json.get("id", "lixeira_01")
    # Cria o payload do comando, ajustando conforme a necessidade
    command_payload = {"comando": "atualizar", "id": sensor_id}
    # Publica a mensagem no tópico de comando (ajuste o tópico se necessário)
    publish_message("comando/atualizacao", json.dumps(command_payload))
    return jsonify({"status": "comando enviado", "sensor": sensor_id}), 200

@sensor_bp.route('/historico', methods=['GET'])
def get_historico():
    sensor_id = request.args.get("sensor_id")
    if not sensor_id:
        return jsonify({"status": "erro", "message": "Parâmetro sensor_id não fornecido"}), 400
    try:
        history = get_sensor_history(sensor_id)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"status": "erro", "message": str(e)}), 500