# Routing\_2025

Este repositório contém a aplicação de roteirização e monitoramento, dividida em serviços de MQTT (Mosquitto), banco de séries temporais (InfluxDB), servidor de rotas (OSRM) e aplicações de backend/frontend.

---

## Branches

* **main**: Versão principal com Docker Compose para todos os serviços (Mosquitto, InfluxDB, OSRM, backend e frontend).

---

## Visão Geral da Arquitetura

1. **Mosquitto**: Broker MQTT para troca de mensagens.
2. **InfluxDB**: Armazena métricas e telemetria.
3. **OSRM**: Calcula rotas usando dados OSRM.
4. **Backend**: API em Flask.
5. **Frontend**: Interface web.

---

## Pré-requisitos

* Git
* Docker & Docker Compose
* Estrutura de dados pré-populada em `data/` (OSRM) e `influxdb-data/` (InfluxDB)

---

## Clonando o Repositório

```bash
git clone https://github.com/dudidatrindade/routing_2025.git
cd routing_2025
```

---

## Arquivo de Ambiente

O arquivo `.env` deve estar na raiz do projeto e também está disponível no mesmo drive onde residem os dados geográficos e do InfluxDB. Exemplos de variáveis:

```env
# Mosquitto
MQTT_BROKER=localhost
MQTT_PORT=1883

# InfluxDB
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=seu_token_aqui
INFLUXDB_ORG=sua_org
INFLUXDB_BUCKET=seu_bucket

# OSRM
OSRM_URL=http://osrm:5000
```

---

## Executando com Docker Compose

```bash
docker-compose up -d mosquitto influxdb osrm backend frontend
```

> **Importante**: antes de subir os serviços, garanta que as pastas `data/` e `influxdb-data/` já contenham todos os arquivos necessários.

---

## Acessando a Aplicação

* **Frontend**: [http://localhost:8000](http://localhost:8000)
* **API (Flask)**: [http://localhost:5000](http://localhost:5000)
* **InfluxDB UI**: [http://localhost:8086](http://localhost:8086) (use o mesmo drive de geodados para navegar nos buckets)

---

## Links Úteis

* Dados geográficos e InfluxDB: [Drive Compartilhado](https://drive.google.com/drive/folders/1E4rVM3cOQVnZlB26YH8m3vfqafWeesKd?usp=sharing)

---