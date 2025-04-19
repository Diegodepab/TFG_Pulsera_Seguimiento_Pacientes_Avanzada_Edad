#include <Wire.h>
#include <TFT_eSPI.h>
#include <MAX30105.h>
#include "spo2_algorithm.h"  // trae FreqS y BUFFER_SIZE

// —————————————————————————————————————————————
//  CONFIGURACIÓN HARDWARE
// —————————————————————————————————————————————
#define I2C_SDA 21
#define I2C_SCL 22
TFT_eSPI tft = TFT_eSPI();
MAX30105 particleSensor;

// —————————————————————————————————————————————
//   VARIABLES PARA SPO2 Y HR
// —————————————————————————————————————————————
int32_t spo2 = 0;
int8_t  validSPO2 = 0;
int32_t heartRate = 0;
int8_t  validHR = 0;

// Buffers de muestras (100 = 25 SPS × 4 s)
uint32_t irBuffer[BUFFER_SIZE];
uint32_t redBuffer[BUFFER_SIZE];

// Umbral para “hay dedo” (ajústalo si tu sensor da valores más bajos)
const uint32_t IR_THRESHOLD = 50000;

// PARA PROMEDIO DE DATOS
long sumHR = 0;
long sumSpO2 = 0;
uint16_t countHR = 0;
uint16_t countSpO2 = 0;
int32_t lastAvgHR = 0;
int32_t lastAvgSpO2 = 0;

// TIEMPOS
unsigned long fingerRemovedMillis = 0;

// ESTADOS
enum State { WAITING, ANALYSING, SHOW_RESULTS };
State state = WAITING;
bool firstFill = true;

void setup() {
  Serial.begin(115200);

  // Configuro I2C
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);

  // Inicializo pantalla
  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE);
  tft.setTextSize(2);

  // Inicializo sensor MAX30102
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    tft.fillScreen(TFT_RED);
    tft.setCursor(0, 0);
    tft.println("Sensor NO hallado");
    while (1) delay(100);
  }
  // Parámetros de sensor
  particleSensor.setup(
    /*ledBrightness=*/0x1F,
    /*sampleAverage=*/4,
    /*ledMode=*/2,
    /*sampleRate=*/FreqS,   // 25 SPS
    /*pulseWidth=*/411,
    /*adcRange=*/4096
  );

  // Pantalla inicial
  tft.setCursor(0, 0);
  tft.println("Esperando dedo...");
}

void loop() {
  // Lectura IR y RED
  while (!particleSensor.available()) particleSensor.check();
  uint32_t ir = particleSensor.getIR();
  uint32_t red = particleSensor.getRed();
  particleSensor.nextSample();

  // Detección de dedo
  if (ir < IR_THRESHOLD) {
    if (state == ANALYSING) {
      fingerRemovedMillis = millis();
      state = SHOW_RESULTS;
    }
    if (state == SHOW_RESULTS && (millis() - fingerRemovedMillis) > 3000) {
      // Muestro últimos promedios en pantalla permanentemente
      tft.fillScreen(TFT_BLACK);
      tft.setCursor(0, 0);
      tft.printf("HR avg: %ld BPM\n", lastAvgHR);
      tft.printf("SpO2 avg: %ld %%\n", lastAvgSpO2);
      tft.println("Pase el dedo para medir otra vez");
      Serial.printf("RESULTADOS FINALES - HR avg=%ld SpO2 avg=%ld\n", lastAvgHR, lastAvgSpO2);
      state = WAITING;
    }
    return;
  }

  // Inicio de medición
  if (state == WAITING) {
    state = ANALYSING;
    sumHR = sumSpO2 = 0;
    countHR = countSpO2 = 0;
    firstFill = true;
    // Aviso en pantalla
    tft.fillScreen(TFT_BLACK);
    tft.setCursor(0, 0);
    tft.println("Dedo detectado");
    tft.println("Comenzar analisis");
    // Aviso en Serial
    Serial.println("Dedo detectado: comenzando medicion");
    delay(1000);
  }

  // Llenado o desplazamiento de buffers
  if (firstFill) {
    for (int i = 0; i < BUFFER_SIZE; i++) {
      while (!particleSensor.available()) particleSensor.check();
      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = particleSensor.getIR();
      particleSensor.nextSample();
    }
    firstFill = false;
  } else {
    for (int i = 0; i < BUFFER_SIZE - FreqS; i++) {
      redBuffer[i] = redBuffer[i + FreqS];
      irBuffer[i] = irBuffer[i + FreqS];
    }
    redBuffer[BUFFER_SIZE - FreqS] = red;
    irBuffer[BUFFER_SIZE - FreqS] = ir;
    for (int j = BUFFER_SIZE - FreqS + 1; j < BUFFER_SIZE; j++) {
      while (!particleSensor.available()) particleSensor.check();
      redBuffer[j] = particleSensor.getRed();
      irBuffer[j] = particleSensor.getIR();
      particleSensor.nextSample();
    }
  }

  // Cálculo de métricas
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, BUFFER_SIZE,
    redBuffer,
    &spo2, &validSPO2,
    &heartRate, &validHR
  );

  // Filtrar valores anómalos y promediar
  bool hrOK = validHR && heartRate > 0 && heartRate <= 200;
  bool spo2OK = validSPO2 && spo2 > 0 && spo2 <= 100;
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

  // Muestro promedios en pantalla
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0, 0);
  tft.printf("HR avg: %ld BPM\n", lastAvgHR);
  tft.printf("SpO2 avg: %ld %%\n", lastAvgSpO2);

  // Serial Monitor
  if (hrOK && spo2OK) {
    Serial.printf("HR=%ld SpO2=%ld AvgHR=%ld AvgSpO2=%ld\n", heartRate, spo2, lastAvgHR, lastAvgSpO2);
  } else {
    Serial.printf("Señal errónea - HR=%ld(%d) SpO2=%ld(%d)\n", heartRate, validHR, spo2, validSPO2);
  }
}
