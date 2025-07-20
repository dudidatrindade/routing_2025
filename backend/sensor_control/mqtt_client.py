import os
import time
import json
import paho.mqtt.client as mqtt
from backend.sensor_control.influx_client import write_sensor_data

# Lê do .env injetado pelo Docker
MQTT_BROKER = os.environ.get("MQTT_BROKER", "mqtt-broker")
MQTT_PORT   = int(os.environ.get("MQTT_PORT", 1883))

# Cria o client global
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Conectado com sucesso ao broker")
        # Inscreve em todos os tópicos relevantes
        client.subscribe("sensors/#")
    else:
        print(f"[MQTT] Falha na conexão, código de retorno {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        sensor_data = json.loads(payload)
        print("[MQTT] Dados recebidos em", msg.topic, "→", sensor_data)
        write_sensor_data(sensor_data)
    except Exception as e:
        print("[MQTT] Erro ao processar mensagem:", e)

def connect_mqtt():
    """ Tenta conectar indefinidamente até conseguir. """
    # atribui callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            client.loop_start()
            return client
        except Exception as e:
            print(f"[MQTT] Falha na conexão: {e}. Tentando novamente em 5s…")
            time.sleep(5)

def publish_message(topic: str, payload):
    """
    Publica uma mensagem no broker.
    Se payload for dict, converte para JSON automaticamente.
    """
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    result = client.publish(topic, payload)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"[MQTT] Erro ao enviar mensagem: {mqtt.error_string(result.rc)}")
