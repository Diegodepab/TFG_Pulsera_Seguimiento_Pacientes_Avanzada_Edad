#include <WiFi.h>
#include <time.h>
#include <TFT_eSPI.h>
#include <PubSubClient.h>

// ——— Configuración Wi-Fi y NTP —————————————————————————————————————
const char* SSID     = "TFGDiegoDePablo";
const char* PASSWORD = "TFGde10!";
const char* NTP1     = "pool.ntp.org";
const char* NTP2     = "time.nist.gov";

// ——— Configuración MQTT (Mosquitto local) ——————————————————————————
const char* MQTT_BROKER = "192.168.135.238";  // IP fija de tu PC en la LAN
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "pulsera/test";

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);

// ——— Pantalla TFT ————————————————————————————————————————————————
TFT_eSPI tft = TFT_eSPI();

// ——— Funciones auxiliares ————————————————————————————————————————
void connectWiFi() {
  tft.fillScreen(TFT_BLACK);
  tft.drawString("Iniciando WiFi...", 10, 50);

  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);
  Serial.print("Conectando a Wi-Fi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" ¡Conectado!");
    Serial.print("IP: "); Serial.println(WiFi.localIP());
    tft.fillScreen(TFT_BLACK);
    tft.drawString("WiFi Conectado", 10, 50);
    tft.drawString(WiFi.localIP().toString(), 10, 80);
  } else {
    Serial.println(" Error al conectar Wi-Fi");
    tft.fillScreen(TFT_RED);
    tft.drawString("WiFi FAILED", 10, 50);
    while (true) delay(1000);
  }
}

void initTime() {
  configTime(0, 0, NTP1, NTP2);
  Serial.print("Sincronizando hora");
  while (time(nullptr) < 100000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" ¡Hora lista!");
}

String getISOTime() {
  time_t now = time(nullptr);
  struct tm* tmInfo = gmtime(&now);
  char buf[25];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", tmInfo);
  return String(buf);
}

void connectMQTT() {
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  Serial.print("Conectando MQTT...");
  while (!mqtt.connected()) {
    if (mqtt.connect("ESP32Client")) {
      Serial.println(" ¡MQTT OK!");
    } else {
      Serial.print(" fallo, rc=");
      Serial.print(mqtt.state());
      Serial.println(", retry en 2s");
      delay(2000);
    }
  }
}

// ——— Setup y loop —————————————————————————————————————————————
void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLACK);
  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE);

  connectWiFi();
  initTime();
  connectMQTT();
}

void loop() {
  // Mantener vivo MQTT
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();

  // Obtener timestamp ISO
  String ts = getISOTime();
  Serial.println(ts);

  // Mostrar hora en TFT
  tft.fillScreen(TFT_BLACK);
  tft.drawString("Hora UTC:", 10, 20);
  tft.drawString(ts,      10, 50);

  // Publicar un mensaje de prueba con la hora
  String msg = "Hola ESP32 @ " + ts;
  mqtt.publish(MQTT_TOPIC, msg.c_str());

  Serial.print("Publicado: ");
  Serial.println(msg);

  delay(5000);
}