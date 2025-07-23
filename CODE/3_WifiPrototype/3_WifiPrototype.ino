#include <Wire.h>
#include <TFT_eSPI.h>
#include <MPU6050_light.h>
#include <MAX30105.h>
#include "spo2_algorithm.h"

#include <WiFi.h>
#include <PubSubClient.h>
#include <time.h>

// Frames for display animation
#include "frame_001.h"

// Create objects for display and sensors
TFT_eSPI tft = TFT_eSPI();
MPU6050 mpu(Wire);
MAX30105 particleSensor;

// Button pins
const int BUTTON1_PIN = 0;
const int BUTTON2_PIN = 35;
unsigned long buttonPressStart = 0;
bool bothButtonsPressed = false;

// MPU-6050 variables
float prevAccX = 0, prevAccY = 0, prevAccZ = 0;
int stepCount = 0;
const float FALL_THRESHOLD =3.5;
bool mpuOk = true;

const int WINDOW_SIZE = 20;         
float zBuffer[WINDOW_SIZE] = {0};
int   zIndex = 0;
float zSum = 0; 
unsigned long lastStepMillis = 0;
const unsigned long MIN_STEP_INTERVAL = 300;
const float STEP_THRESHOLD = 1.2; 

// MAX30102 (pulse oximeter) 
bool maxOk = true;
int32_t spo2 = 0;
int8_t validSPO2 = 0;
int32_t heartRate = 0;
int8_t validHR = 0;
uint32_t irBuffer[BUFFER_SIZE];
uint32_t redBuffer[BUFFER_SIZE];
const uint32_t IR_THRESHOLD = 50000;
long sumHR = 0, sumSpO2 = 0;
uint16_t countHR = 0, countSpO2 = 0;
int32_t lastAvgHR = 0, lastAvgSpO2 = 0;
unsigned long fingerRemovedMillis = 0;
enum MAXState { WAITING, ANALYSING, SHOW_RESULTS };
MAXState maxState = WAITING;
bool firstFill = true;

static uint16_t initialFillIndex = 0;
static uint16_t chunkIndex        = 0;
static uint32_t tempIR[FreqS];
static uint32_t tempRed[FreqS];

void shiftBuffers(uint16_t shiftCount);
void displayRealtime(uint32_t hr, uint32_t sp);

// ———  Wi-Fi y NTP ————————————————————————————————————————————————
const char* SSID     = "TFGDiegoDePablo";
const char* PASSWORD = "TFGde10!";
const char* NTP1     = "pool.ntp.org";
const char* NTP2     = "time.nist.gov";

// ——— Configuración MQTT (Mosquitto local) ——————————————————————————
const char* MQTT_BROKER = "192.168.248.238";  // IP cambiala
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "pulsera/test";

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);

bool wifiConnected   = false;
bool mqttConnected   = false;


unsigned long lastMinuteMillis = 0;
enum AlertState { NONE, SINGLE, BOTH };
AlertState alertState       = NONE;
unsigned long alertStart    = 0;
const unsigned long SINGLE_DURATION = 500;   // ms que dura el amarillo
const unsigned long BOTH_THRESHOLD  = 2500;  // ms para pasar a rojo
const unsigned long BOTH_DURATION   = 2000;  // ms que dura el rojo

// Function prototypes
void initDisplay();
void initMPU();
void initMAX();
void handleButtonsAndInputs();
void handleMPU();
void handleMAX();
void connectWiFi();
void connectMQTT();
void displayClock();


void setup() {
  Serial.begin(115200);
  tft.begin();
  tft.setRotation(0);
  tft.fillScreen(TFT_WHITE);
  initDisplay();

  connectWiFi();
  initTime();
  connectMQTT();

  initMPU();
  initMAX();

  lastMinuteMillis = millis();
}

void loop() {
  displayClock(); 
  handleButtonsAndInputs();
  mpu.update();
  handleMPU();
  handleMAX();
  // 60 000 ms
  if (millis() - lastMinuteMillis >= 60000) {
  lastMinuteMillis += 60000;
  sendMetrics();   
  }

}

// Initialize TFT display and button inputs
void initDisplay() {
  tft.begin();
  tft.setRotation(0);
  tft.setSwapBytes(true);
  tft.fillScreen(TFT_WHITE);
  tft.pushImage(0, 0, 160, 235, frame_001);  // fondo fijo

  pinMode(BUTTON1_PIN, INPUT_PULLUP);
  pinMode(BUTTON2_PIN, INPUT_PULLUP);
}

// Initialize MPU-6050 sensor
void initMPU() {
  Wire.begin(21, 22);
  Serial.println("Iniciando MPU-6050...");
  byte status = mpu.begin();
  if (status != 0) {
    Serial.printf("Error iniciando MPU: %d\n", status);
    mpuOk = false;
    sendMQTT("ERROR_SENSOR", "\"sensor\":\"MPU6050\"");  // notifica fallo
  } else {
    Serial.println("MPU-6050 listo.");
    mpu.calcOffsets(true, true);
  }
}
// Initialize MAX30102 sensor
void initMAX() {
  Wire.setClock(400000);
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("Error: MAX30102 no encontrado");
    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE);
    tft.setCursor(0, 0);
    tft.println("Sensor NO hallado");
    maxOk = false;
    sendMQTT("ERROR_SENSOR", "\"sensor\":\"MAX30102\"");  // notifica fallo

  }
  particleSensor.setup(
    /* ledBrightness   */ 0x1F,
    /* sampleAverage   */ 2,
    /* ledMode         */ 2,
    /* sampleRate      */ 100,
    /* pulseWidth      */ 411,
    /* adcRange        */ 4096
  );
  Serial.println("MAX30102 listo.");
}

// Handle button inputs and simple screen refresh (no animation)
void handleButtonsAndInputs() {
  unsigned long now = millis();
  bool b1 = digitalRead(BUTTON1_PIN) == LOW;
  bool b2 = digitalRead(BUTTON2_PIN) == LOW;


  if (b1 && b2) {
    if (alertState != BOTH) {
      if (alertState == NONE) alertStart = now;
      if (now - alertStart >= BOTH_THRESHOLD) {
        alertState = BOTH;
        alertStart = now;              
        
        tft.fillScreen(TFT_RED);
        tft.setTextColor(TFT_WHITE);
        tft.setTextSize(2);
        tft.drawString("ALERTA:", 30, 90);
        tft.drawString("Ambos botones",  1, 120);
        tft.drawString("Presionados!",    1, 150);
        sendMQTT("ALERTA_BOTONES", "\"type\":\"long_press\"");
        Serial.println("ALERTA: botones presionados");
      } else {
        // durante la cuenta atrás seguimos mostrando amarillo
        if (alertState != SINGLE) {
          alertState = SINGLE;
          alertStart = now;   // inicia el contador de duración amarillo
          tft.fillScreen(TFT_YELLOW);
          tft.setTextColor(TFT_BLACK);
          tft.setTextSize(2);
          tft.drawString("Boton",         30, 100);
          tft.drawString("Presionado!",   10, 130);
          Serial.println("Aviso: 1 boton presionado");
        }
      }
    }
  }
  else if (b1 || b2) {
    // Only 1 buttom adverstiment
    if (alertState != SINGLE) {
      alertState = SINGLE;
      alertStart = now;
      tft.fillScreen(TFT_YELLOW);
      tft.setTextColor(TFT_BLACK);
      tft.setTextSize(2);
      tft.drawString("Boton",         30, 100);
      tft.drawString("Presionado!",   10, 130);
      Serial.println("Aviso: 1 boton presionado");
    } else {

      alertStart = now;
    }
  }
  else {
    // no buttom
    if (alertState == SINGLE && now - alertStart >= SINGLE_DURATION) {
      alertState = NONE;
      tft.pushImage(0, 0, 160, 235, frame_001);
      displayRealtime();
    }
    else if (alertState == BOTH && now - alertStart >= BOTH_DURATION) {
      alertState = NONE;
      tft.pushImage(0, 0, 160, 235, frame_001);
      displayRealtime();
    }
  }
}


// Read MPU data, detect steps/falls, and update display/Serial
void handleMPU() {
  if (!mpuOk) {
    initMPU();
    return;
  }
  float accX = mpu.getAccX();
  float accY = mpu.getAccY();
  float accZ = mpu.getAccZ();

  // Fall detection
  float dX = abs(accX - prevAccX);
  float dY = abs(accY - prevAccY);
  float dZ = abs(accZ - prevAccZ);
  if ((dX > FALL_THRESHOLD || dY > FALL_THRESHOLD || dZ > FALL_THRESHOLD)) {
    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE);
    tft.setTextSize(2);
    tft.drawString("ALERTA", 10, 90);
    tft.drawString("CAIDA", 10, 110);
    Serial.println("ALERTA: Caida detectada");
    sendMQTT("ALERTA_CAIDA", "\"dx\":" + String(dX)
                          + ",\"dy\":" + String(dY)
                          + ",\"dz\":" + String(dZ));
    delay(2000);
    tft.pushImage(0, 0, 160, 235, frame_001);  // fondo fijo
    displayRealtime();

  }

  // --- STEP DETECTION AREA ---
  // 1) Simple moving average (high-pass) filtering
  zSum -= zBuffer[zIndex];
  zBuffer[zIndex] = accZ;
  zSum += zBuffer[zIndex];
  zIndex = (zIndex + 1) % WINDOW_SIZE;
  // we subtract the buffer average to remove slow components
  float zMean = zSum / WINDOW_SIZE;
  float zFiltered = accZ - zMean;

  // 2) Threshold and minimum time peak detector
  unsigned long now = millis();
  if (zFiltered > STEP_THRESHOLD
      && (now - lastStepMillis) > MIN_STEP_INTERVAL) {
    stepCount++;
    lastStepMillis = now;
  } 
  prevAccX = accX;
  prevAccY = accY;
  prevAccZ = accZ;

  // Display step count and detection status
  tft.setTextColor(TFT_BLACK, TFT_WHITE);
  tft.setTextSize(2);
  tft.setCursor(15, 200);
  tft.printf("Pasos: %d", stepCount);
  tft.setCursor(10, 220);

}

// Acquire data from MAX30102, compute HR/SpO2, and output to Serial
void handleMAX() {
  if (!maxOk) {
    initMAX();
    return;
  }

  // Update and check FIFO without blocking
  particleSensor.check();
  if (!particleSensor.available()) return;

  // Reed IR and RED
  uint32_t ir  = particleSensor.getIR();
  uint32_t red = particleSensor.getRed();
  particleSensor.nextSample();

  // Finger removed -> state transition
  if (ir < IR_THRESHOLD) {
    if (maxState == ANALYSING) {
      fingerRemovedMillis = millis();
      maxState = SHOW_RESULTS;
    }
    if (maxState == SHOW_RESULTS && millis() - fingerRemovedMillis > 3000) {
      Serial.printf("RESULTADOS FINALES - AvgHR=%ld BPM AvgSpO2=%ld %%\n",
                    lastAvgHR, lastAvgSpO2);
      maxState = WAITING;
      initialFillIndex = chunkIndex = 0;
      tft.fillRect(10, 220, 140, 16, TFT_WHITE);
      sendMetrics(); 

    }
    return;
  }

  // Start analysis when finger is detected
  if (maxState == WAITING) {
    maxState = ANALYSING;
    sumHR = sumSpO2 = 0;
    countHR = countSpO2 = 0;
    firstFill = true;
    initialFillIndex = chunkIndex = 0;
    Serial.println("Dedo detectado: comenzando medicion");
  }

  // Initial buffer filling (sample by sample)
  if (firstFill) {
    irBuffer[initialFillIndex]  = ir;
    redBuffer[initialFillIndex] = red;
    if (++initialFillIndex >= BUFFER_SIZE) {
      firstFill = false;
      initialFillIndex = 0;
    }
    // Show current average still empty
    displayRealtime();
    return;
  }

  //  Grouping in FreqS chunks
  tempIR[chunkIndex]  = ir;
  tempRed[chunkIndex] = red;
  if (++chunkIndex < FreqS) {
    displayRealtime();
    return;
  }

  //  Grouping in FreqSS chunks, moving buffer and copying new data
  shiftBuffers(FreqS);
  memcpy(irBuffer  + BUFFER_SIZE - FreqS, tempIR,  FreqS * sizeof(uint32_t));
  memcpy(redBuffer + BUFFER_SIZE - FreqS, tempRed, FreqS * sizeof(uint32_t));
  chunkIndex = 0;

  // HR and SpO2 calculation
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, BUFFER_SIZE,
    redBuffer,
    &spo2, &validSPO2,
    &heartRate, &validHR
  );

  // Filtering and averaging
  bool hrOK   = validHR   && heartRate > 0 && heartRate <= 200;
  bool spo2OK = validSPO2 && spo2      > 0 && spo2      <= 100;
  if (hrOK) {
    sumHR += heartRate;
    countHR++;
    lastAvgHR = sumHR / countHR;
  }
  if (spo2OK) {
    sumSpO2 += spo2;
    countSpO2++;
    lastAvgSpO2 = sumSpO2 / countSpO2;
  }

  // Display real-time average
  displayRealtime();

  // Serial Output
  if (hrOK && spo2OK) {
    Serial.printf("HR=%ld SpO2=%ld AvgHR=%ld AvgSpO2=%ld\n",
                  heartRate, spo2, lastAvgHR, lastAvgSpO2);
  } else {
    Serial.printf("Señal errónea - HR=%ld(%d) SpO2=%ld(%d)\n",
                  heartRate, validHR, spo2, validSPO2);
  }
}

// Output SerialShift buffers to the left ‘shiftCount’ positions
template <typename T>
void genericShift(T* buffer, uint16_t length, uint16_t shiftCount) {
  memmove(buffer, buffer + shiftCount, (length - shiftCount) * sizeof(T));
}

void shiftBuffers(uint16_t shiftCount) {
  genericShift(irBuffer,  BUFFER_SIZE, shiftCount);
  genericShift(redBuffer, BUFFER_SIZE, shiftCount);
}


void displayRealtime() {
  tft.setTextSize(2);
  tft.setTextColor(TFT_BLACK, TFT_WHITE);


  tft.fillRect(80, 35, 60, 16, TFT_WHITE);
  tft.setCursor(80, 35);
  tft.printf("%ld", lastAvgHR);

  tft.fillRect(80, 80, 60, 16, TFT_WHITE);
  tft.setCursor(80, 80);
  tft.printf("%ld%%", lastAvgSpO2);


  if (maxState == ANALYSING) {

    tft.setCursor(10, 220);
    tft.printf("ANALIZANDO ...");
    
  }
}

// — Conection Wi-Fi 
void connectWiFi() {
  WiFi.begin(SSID, PASSWORD);
  Serial.print("Conectando a WiFi...");
  unsigned long start = millis();
  // 5s
  while (WiFi.status() != WL_CONNECTED && millis() - start < 5000) {
    delay(200);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println(" OK. IP: " + WiFi.localIP().toString());
  } else {
    wifiConnected = false;
    Serial.println(" FALLÓ.");

    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE);
    tft.setTextSize(2);
    tft.drawString("WiFi NO",  20,  80);
    tft.drawString("conectado", 10, 110);
    delay(2000);
    tft.pushImage(0, 0, 160, 235, frame_001);
    displayRealtime();

  }
}

void initTime() {
  if (wifiConnected) {
    configTime(0, 0, NTP1, NTP2);
    unsigned long start = millis();
    while (time(nullptr) < 100000 && millis() - start < 5000) {
      delay(200);
    }
    if (time(nullptr) < 100000) {
      Serial.println("WARNING: NTP timeout, usando hora de compilación");
    } else {
      Serial.println("NTP OK");
      return;
    }
  }
  
  // -- Fallback: cargar __DATE__ y __TIME__ --
  Serial.println("Inicializando hora desde compilación");
  struct tm tm;  
  char monthStr[4];
  int day, year, hour, minute, second;

  sscanf(__DATE__, "%3s %d %d", monthStr, &day, &year);
  sscanf(__TIME__, "%d:%d:%d",    &hour,     &minute,  &second);

  // Convert monthStr a tm.tm_mon (0–11)
  const char* months = "JanFebMarAprMayJunJulAugSepOctNovDec";
  tm.tm_mon = (strstr(months, monthStr) - months) / 3;

  tm.tm_mday  = day;
  tm.tm_year  = year - 1900;
  tm.tm_hour  = hour;
  tm.tm_min   = minute;
  tm.tm_sec   = second;
  tm.tm_isdst = 0;

  time_t t = mktime(&tm);
  struct timeval tv = { .tv_sec = t, .tv_usec = 0 };
  settimeofday(&tv, nullptr);

  Serial.printf("Hora inicial: %02d:%02d:%02d %02d/%02d/%04d\n",
                tm.tm_hour, tm.tm_min, tm.tm_sec,
                tm.tm_mday, tm.tm_mon+1, tm.tm_year+1900);
}

// ISO 8601 UTC
String getISOTime() {
  time_t now = time(nullptr);
  struct tm ts; gmtime_r(&now, &ts);
  char buf[25];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &ts);
  return String(buf);
}

void connectMQTT() {
  if (!wifiConnected) {
    mqttConnected = false;
    return;
  }
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  Serial.print("Conectando a MQTT...");
  if (mqtt.connect("ESP32Client")) {
    mqttConnected = true;
    Serial.println(" OK");
  } else {
    mqttConnected = false;
    Serial.println(" FALLÓ");
    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE);
    tft.setTextSize(2);
    tft.drawString("MQTT NO",  20,  80);
    tft.drawString("conectado", 10, 110);
    delay(2000);
    tft.pushImage(0, 0, 160, 235, frame_001);
  }
}


void publishJSON(const String& payload) {
  if (!mqtt.connected()) connectMQTT();
  mqtt.publish(MQTT_TOPIC, payload.c_str());
}

void sendMQTT(const char* eventType, const String& data) {
  String js = "{";
  js += "\"ts\":\"" + getISOTime() + "\",";
  js += "\"event\":\"" + String(eventType) + "\",";
  js += data;
  js += "}";
  publishJSON(js);
  Serial.println("MQTT >> " + js);
}

void sendMetrics() {
  if (!wifiConnected) {
    Serial.println("WARN: Sin WiFi, reintentando conexión...");
    connectWiFi();
    if (!wifiConnected) {
      Serial.println("ERROR: No hay WiFi. Métricas descartadas.");
      return;
    }
  }
  if (!mqttConnected) {
    Serial.println("INFO: MQTT desconectado, reintentando...");
    connectMQTT();
    if (!mqttConnected) {
      Serial.println("ERROR: No hay MQTT. Métricas descartadas.");
      return;
    }
  }

  String payload = "{";
  payload += "\"step_count\":" + String(stepCount)   + ",";
  payload += "\"bpm\":"        + String(lastAvgHR)   + ",";
  payload += "\"spo2\":"       + String(lastAvgSpO2) + ",";
  payload += "\"ts\":\""       + getISOTime()        + "\"";
  payload += "}";
  mqtt.publish(MQTT_TOPIC, payload.c_str());
  Serial.println("MQTT METRICS >> " + payload);
}

void displayClock() {
  time_t now = time(nullptr);
  struct tm ts;
  localtime_r(&now, &ts);

  char buf[6];
  sprintf(buf, "%02d:%02d", ts.tm_hour, ts.tm_min);   //  “HH:MM”

  tft.setTextSize(2);
  tft.setTextColor(TFT_BLACK, TFT_WHITE);
  tft.setCursor(40, 5);   
  tft.print(buf);
}