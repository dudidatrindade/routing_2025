# Routing2025

## Visão Geral

Sistema de roteamento inteligente para coleta de lixo baseado em sensores de nível em lixeiras. O firmware (ESP01/ESP32) mede distância até o lixo e publica JSON via MQTT em `dados/sensor/#`. O backend em Flask consome essas mensagens, converte distância em volume, armazena em InfluxDB, resolve o problema do caixeiro viajante via OSRM + OR-Tools e gera um mapa interativo. O frontend exibe dashboards e controles de coleta.

## Arquitetura

1. **Firmware (ESP01/ESP32)**: coleta distância e publica em broker Mosquitto.
2. **Broker MQTT (Mosquitto)**: recebe pacotes JSON.
3. **Backend (Flask)**:

   * Blueprints: `routing` e `sensor_control`
   * Consome tópicos MQTT, grava em InfluxDB
   * Chama OSRM Table API (Docker) para matriz de custos
   * Resolve TSP com OR-Tools
   * Gera mapa HTML em `static/map`
4. **Banco de séries temporais**: InfluxDB
5. **Serviço de roteamento**: OSRM em container Docker
6. **Frontend**: app web em `frontend/public` consumindo APIs do backend

## Pré-requisitos

* Git
* Python 3.8+ e pip
* Bibliotecas Python: Tkinter, folium, ortools, requests, flask, flask-cors, paho-mqtt, influxdb-client
* Node.js e npm/yarn (necessário apenas para desenvolvimento do frontend)
* Docker e Docker Compose
* Broker MQTT (Mosquitto) na porta 1883 (libere no firewall se necessário)
* InfluxDB
* Serviço OSRM rodando na porta 5000 (dados já extraídos e contratados)

## Instalação

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/dudidatrindade/routing2025.git
   cd routing2025
   ```
2. \*\*Crie e configure o \*\*\`\` (variáveis abaixo).
3. **Backend**:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. **Frontend** (opcional para desenvolvimento local):

   ```bash
   cd frontend/public
   npm install
   ```
5. **Inicie serviços com Docker Compose**:

   ```bash
   docker-compose up -d mosquitto influxdb osrm
   ```
6. **Execute o backend**:

   ```bash
   cd backend
   python app.py
   ```
7. **Abra o frontend**:

   * Sirva `frontend/public` em um servidor estático ou use Live Server no VS Code.

## Variáveis de Ambiente (`.env`)

```dotenv
MQTT_BROKER=localhost
MQTT_PORT=1883
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=<seu_token>
INFLUXDB_ORG=<sua_org>
INFLUXDB_BUCKET=<seu_bucket>
OSRM_URL=http://localhost:5000
SECRET_KEY=<chave_secreta>
```

## Uso

* **Payload do sensor**:

  ```json
  {
    "sensor_id": "lixeira_01",
    "distancia_cm": 25,
    "timestamp": "2025-07-19T12:00:00Z"
  }
  ```
* **Endpoints REST**:

  * `GET /api/mapa?threshold=<percentual>`: retorna mapa interativo filtrado
  * `GET /api/sensor_control/list`: lista sensores configurados
  * `POST /api/sensor_control/add`: adiciona/atualiza sensor

## Contribuição

1. Fork este repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona feature'`)
4. Envie para o branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto é distribuído sob uma licença proprietária e **todos os direitos estão reservados**. O código-fonte só pode ser usado, modificado ou distribuído por pessoas explicitamente autorizadas pelo mantenedor. Se você precisar de acesso ou permissão, entre em contato através do e-mail [eduardotrindade553@gmail.com](mailto:eduardotrindade553@gmail.com).