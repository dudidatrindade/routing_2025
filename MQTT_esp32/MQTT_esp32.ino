#include <WiFi.h>
#include <PubSubClient.h>

// Configurações de rede WiFi
const char* ssid = "HONORE 401";
const char* password = "23140719";

// Configurações do broker MQTT
const char* mqtt_server = "192.168.0.145";  // Altere para o endereço do seu broker
const int mqtt_port = 1883;

// Tópicos MQTT
const char* data_topic = "dados/sensor/esp32";
const char* command_topic = "comando/atualizacao";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastPublish = 0;
const unsigned long publishInterval = 60000; // 1 minuto (60000 ms)

// Conecta ao WiFi
void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando ao WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// Callback para processar mensagens MQTT recebidas
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Comando recebido no tópico ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(message);
  
  // Se o comando for recebido no tópico de atualização, dispara o envio imediato
  if (String(topic) == String(command_topic)) {
    Serial.println("Comando de atualização recebido. Enviando dados imediatamente...");
    publishSensors();
  }
}

// Função para reconectar ao broker MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("Conectado ao MQTT!");
      client.subscribe(command_topic);
    } else {
      Serial.print("Falha na conexão MQTT, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

// Função para simular e publicar os dados de 25 lixeiras
void publishSensors() {
  Serial.println("Publicando dados dos sensores...");
  for (int i = 1; i <= 25; i++) {
    String sensorId = "lixeira_";
    if (i < 10) {
      sensorId += "0";
    }
    sensorId += String(i);
    
    // Gera um valor aleatório de distância entre 0 e 40 (0 = lixeira cheia, 40 = lixeira vazia)
    float distance = random(0, 41);
    String payload = "{\"sensor_id\": \"" + sensorId + "\", \"distance\": " + String(distance, 2) + "}";
    
    Serial.print("Enviando: ");
    Serial.println(payload);
    client.publish(data_topic, payload.c_str());
    
    delay(100);  // Pequeno delay entre publicações
  }
}

void setup() {
  Serial.begin(115200);
  setupWiFi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  
  // Inicializa a semente para números aleatórios
  randomSeed(esp_random());
  
  lastPublish = millis();
}

void loop() {
  // Se não estiver conectado ao MQTT, tenta reconectar
  if (!client.connected()) {
    reconnect();
  }
  client.loop();  // Necessário para manter a conexão e processar callbacks
  
  // Verifica se é hora de publicar os dados simulados
  unsigned long now = millis();
  if (now - lastPublish >= publishInterval) {
    publishSensors();
    lastPublish = now;
  }
}
