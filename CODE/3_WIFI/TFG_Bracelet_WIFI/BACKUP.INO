#include <Wire.h>
#include <TFT_eSPI.h>
#include <MPU6050_light.h>
#include <MAX30105.h>
#include "spo2_algorithm.h"

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

// Parámetros para step detection mejorada
const int WINDOW_SIZE = 20;           // tamaño de buffer para media móvil
float zBuffer[WINDOW_SIZE] = {0};     // buffer circular de muestras de accZ
int   zIndex = 0;
float zSum = 0;                       // suma de valores en buffer
unsigned long lastStepMillis = 0;
const unsigned long MIN_STEP_INTERVAL = 300;  // ms entre pasos
const float STEP_THRESHOLD = 1.2;     // umbral de pico en g (ajustable)

// MAX30102 (pulse oximeter) variables
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

// Variables auxiliares (declarar al inicio del archivo, junto a globals)
static uint16_t initialFillIndex = 0;
static uint16_t chunkIndex        = 0;
static uint32_t tempIR[FreqS];
static uint32_t tempRed[FreqS];

// Prototipos (encima de setup/loop)
void shiftBuffers(uint16_t shiftCount);
void displayRealtime(uint32_t hr, uint32_t sp);

// Function prototypes
void initDisplay();
void initMPU();
void initMAX();
void handleButtonsAndInputs();
void handleMPU();
void handleMAX();

void setup() {
  Serial.begin(115200);
  initDisplay();
  initMPU();
  initMAX();
}

void loop() {
  handleButtonsAndInputs();
  mpu.update();
  handleMPU();
  handleMAX();
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
  Wire.begin(21, 22);  // SDA=21, SCL=22
  Serial.println("Iniciando MPU-6050...");
  byte status = mpu.begin();
  if (status != 0) {
    Serial.print("Error iniciando MPU-6050: ");
    Serial.println(status);
    while (1); // Halt on error
  }
  Serial.println("Calibrando MPU-6050...");
  millis();
  mpu.calcOffsets(true, true);
  Serial.println("MPU-6050 listo.");
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
  unsigned long currentMillis = millis();
  bool b1 = digitalRead(BUTTON1_PIN) == LOW;
  bool b2 = digitalRead(BUTTON2_PIN) == LOW;

  // Both buttons pressed -> long-press alert
  if (b1 && b2) {
    if (!bothButtonsPressed) {
      buttonPressStart = currentMillis;
      bothButtonsPressed = true;
    } else if (currentMillis - buttonPressStart >= 2500) {
      tft.fillScreen(TFT_RED);
      tft.setTextColor(TFT_WHITE);
      tft.setTextSize(2);
      tft.drawString("ALERTA:", 30, 90);
      tft.drawString("Ambos botones", 1, 120);
      tft.drawString("Presionados!", 1, 150);
      Serial.println("ALERTA: botones presionados");
      bothButtonsPressed = false;
      delay(2000);
      tft.pushImage(0, 0, 160, 235, frame_001);  // fondo fijo
      displayRealtime();
    }
  } else {
    bothButtonsPressed = false;

    // Single button press -> warning state
    if (b1 || b2) {
      tft.fillScreen(TFT_YELLOW);
      tft.setTextColor(TFT_BLACK);
      tft.setTextSize(2);
      tft.drawString("Boton", 30, 100);
      tft.drawString("Presionado!", 10, 130);
      Serial.println("Aviso: 1 boton presionado");
      delay(500); 
      tft.pushImage(0, 0, 160, 235, frame_001);  // fondo fijo
      displayRealtime();
    }
    
  }
}


// Read MPU data, detect steps/falls, and update display/Serial
void handleMPU() {
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
