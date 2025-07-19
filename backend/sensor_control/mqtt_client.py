# mqtt_client.py
import paho.mqtt.client as mqtt
import json
from .influx_client import write_sensor_data  # Ajuste o import para o caminho real

MQTT_BROKER = 'localhost'  # ou o IP do seu broker
MQTT_PORT = 1883

client = mqtt.Client()

def on_message(client, userdata, msg):
    try:
        # Converte o payload de JSON para dicionário
        sensor_data = json.loads(msg.payload.decode())
        print("[MQTT] Dados do sensor recebidos:", sensor_data)

        # Chama a função que escreve no InfluxDB
        write_sensor_data(sensor_data)

    except Exception as e:
        print("[MQTT] Erro ao processar mensagem:", e)

def connect_mqtt():
    client.on_message = on_message  # Registra a função de callback
    rc = client.connect(MQTT_BROKER, MQTT_PORT, 60)
    if rc == 0:
        print("[MQTT] Conectado ao broker MQTT!")
        # Inscreve-se no tópico onde o sensor publica os dados
        client.subscribe("dados/sensor/#")
        client.loop_start()  # Roda o loop em background
        return True
    else:
        print(f"[MQTT] Falha na conexão. Código de retorno: {rc}")
        return False

def publish_message(topic, payload):
    """
    Caso você queira enviar dados para o broker MQTT.
    'payload' pode ser um dicionário que você converte para JSON, por exemplo.
    """
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    client.publish(topic, payload)