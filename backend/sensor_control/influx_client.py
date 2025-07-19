import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Configurações do InfluxDB
INFLUX_URL = "http://localhost:8086"  # URL do InfluxDB
INFLUX_TOKEN = "O2IJnWNV-admggVDJHRqeTl_oqxquj0vByhWLLdLL0PRRLlJ3exte5b3cSB0Zcegk0nGPB9Bt0FVEtDy7fmqkA=="  # Substitua pelo seu token
INFLUX_ORG = "Lixeia"                   # Sua organização
INFLUX_BUCKET = "Sensor_Data"           # Seu bucket

# Inicializa o cliente do InfluxDB
client_influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client_influx.write_api(write_options=SYNCHRONOUS)

# Configurações geométricas detalhadas para cada lixeira
SENSOR_CONFIG = {
    "lixeira_01": {"shape": "cylinder", "radius": 10, "height": 50},
    "lixeira_02": {"shape": "cylinder", "radius": 15, "height": 70},
    "lixeira_03": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_04": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_05": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_06": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_07": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_08": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_09": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_10": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_11": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_12": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_13": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_14": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_15": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_16": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_17": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_18": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_19": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_20": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_21": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_22": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_23": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_24": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    "lixeira_25": {"shape": "rectangle", "length": 30, "width": 20, "height": 40},
    # Adicione as configurações para as demais lixeiras (até 25, por exemplo)
    # "lixeira_04": {...}, "lixeira_05": {...}, ...
}

def calculate_fill_percentage(sensor_id, distance):
    """
    Calcula a porcentagem de volume cheio de uma lixeira, considerando sua geometria.
    
    Assumindo que:
    - O sensor mede a distância do sensor até a superfície do lixo.
    - Quando a lixeira está vazia, a distância medida é igual à altura total.
    - A porcentagem cheia é dada por:
          ((altura_total - distance) / altura_total) * 100
    """
    config = SENSOR_CONFIG.get(sensor_id)
    if not config:
        print(f"Configuração para {sensor_id} não encontrada. Usando altura padrão de 100 cm.")
        config = {"shape": "cylinder", "height": 100}
    
    total_height = config["height"]
    effective_height = total_height - distance
    if effective_height < 0:
        effective_height = 0

    fill_percentage = (effective_height / total_height) * 100
    return fill_percentage

def write_sensor_data(sensor_data):
    """
    Insere os dados do sensor no InfluxDB.
    Se o dicionário possuir "distance", ele converte para porcentagem de volume cheio.
    """
    try:
        sensor_id = sensor_data.get("sensor_id", "desconhecido")
        if "distance" in sensor_data:
            distance = sensor_data["distance"]
            fill_percentage = calculate_fill_percentage(sensor_id, distance)
        else:
            fill_percentage = sensor_data.get("fill_percentage", 0)
        
        point = (
            Point("dados_sensores")
            .tag("sensor_id", sensor_id)
            .field("fill_percentage", float(fill_percentage))
            .time(int(time.time()), WritePrecision.S)
        )
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"[InfluxDB] Dados inseridos com sucesso: {sensor_data} => Fill%: {fill_percentage}")
    except Exception as e:
        print("[InfluxDB] Erro ao escrever dados:", e)

def get_sensor_data():
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: 0)
      |> filter(fn: (r) => r._measurement == "dados_sensores" and r._field == "fill_percentage")
      |> group(columns: ["sensor_id"])
      |> last()
    '''
    result = client_influx.query_api().query(query, org=INFLUX_ORG)
    sensor_data_list = []
    for table in result:
        for record in table.records:
            sensor_data_list.append({
                "time": record.get_time(),
                "sensor_id": record.values.get("sensor_id"),
                "fill_percentage": record.get_value()
            })
    return sensor_data_list

def get_sensor_history(sensor_id):
    """
    Consulta o histórico do sensor especificado pelo sensor_id no InfluxDB.
    Retorna uma lista de registros, cada um contendo o timestamp e o valor de fill_percentage.
    """
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: 0)
      |> filter(fn: (r) => r._measurement == "dados_sensores")
      |> filter(fn: (r) => r._field == "fill_percentage")
      |> filter(fn: (r) => r.sensor_id == "{sensor_id}")
      |> sort(columns: ["_time"], desc: false)
    '''
    result = client_influx.query_api().query(query, org=INFLUX_ORG)
    sensor_history = []
    for table in result:
        for record in table.records:
            sensor_history.append({
                "time": record.get_time().isoformat() if record.get_time() else None,
                "fill_percentage": record.get_value()
            })
    return sensor_history

