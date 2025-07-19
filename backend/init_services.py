from backend.sensor_control.mqtt_client import connect_mqtt

def initialize_services():
    print("Inicializando serviços MQTT...")
    if connect_mqtt():
        print("MQTT inicializado!")
    else:
        print("Falha ao conectar no MQTT!")