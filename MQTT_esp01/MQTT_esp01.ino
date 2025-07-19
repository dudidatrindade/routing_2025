#include <ESP8266WiFi.h>       // Biblioteca para ESP8266
#include <PubSubClient.h>
#include <NewPing.h>

// Configurações da rede WiFi (declaração como array de char)
char ssid[] = "J02";
char password[] = "23140719";

// Configurações do broker MQTT
const char* mqtt_server = "192.168.0.121"; // Substitua pelo IP/hostname do seu broker
const int mqtt_port = 1883;

// Instância do sensor HC-SR04
#define TRIGGER_PIN 0     // Pino de Trigger, fio azul
#define ECHO_PIN 2        // Pino de Echo, fio verde
#define MAX_DISTANCE 400  // Distância máxima em cm

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

// Instâncias dos clientes WiFi e MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Configurações de tempo para atualização periódica (1 minuto)
unsigned long lastUpdateTime = 0;
const unsigned long updateInterval = 60000;  // 60.000 ms = 1 minuto

// Identificação do sensor e tópicos MQTT
const char* sensor_id = "lixeira_01";
const char* data_topic = "dados/sensor/lixeira_01";
const char* command_topic = "comando/atualizacao";

// Callback para processar mensagens MQTT recebidas
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Mensagem recebida no tópico ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(message);
  
  // Se a mensagem for o comando de atualização, envia a leitura imediatamente
  if (String(topic) == String(command_topic)) {
    Serial.println("Comando de atualização recebido. Publicando leitura imediata.");
    publishSensorReading();
  }
}

// Função para reconectar ao broker MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conexão MQTT...");
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("Conectado!");
      client.subscribe(command_topic);
    } else {
      Serial.print("Falha na conexão, rc=");
      Serial.print(client.state());
      Serial.println(". Tentando novamente em 5 segundos.");
      delay(5000);
    }
  }
}

// Função para realizar múltiplas medições e calcular a média da distância
float readDistance() {
  const int numReadings = 5;
  unsigned int total = 0;
  int validReadings = 0;
  for (int i = 0; i < numReadings; i++) {
    unsigned int d = sonar.ping_cm();
    if (d > 0) {
      total += d;
      validReadings++;
    }
    delay(50);
  }
  if (validReadings == 0) return 0;
  return total / (float)validReadings;
}

// Função para publicar a leitura do sensor via MQTT
void publishSensorReading() {
  float distance = readDistance();
  String payload = "{\"sensor_id\": \"" + String(sensor_id) + "\", \"distance\": " + String(distance, 2) + "}";
  Serial.println("Enviando payload: " + payload);
  client.publish(data_topic, payload.c_str());
}

void setup() {
  Serial.begin(115200);
  delay(10);
  
  // Conecta ao WiFi
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
  
  // Configura o MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  
  lastUpdateTime = millis();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Publica a leitura a cada 1 minuto
  unsigned long currentTime = millis();
  if (currentTime - lastUpdateTime >= updateInterval) {
    publishSensorReading();
    lastUpdateTime = currentTime;
  }
}
