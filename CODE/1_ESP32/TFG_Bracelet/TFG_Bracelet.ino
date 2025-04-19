#include <Wire.h>
#include <TFT_eSPI.h>
#include <MPU6050_light.h>
#include <MAX30105.h>
#include "spo2_algorithm.h"

// Frames for display animation
#include "frame_000.h"
#include "frame_001.h"
#include "frame_002.h"
#include "frame_003.h"
#include "frame_004.h"
#include "frame_005.h"
#include "frame_006.h"
#include "frame_007.h"
#include "frame_008.h"
#include "frame_009.h"

// Create objects for display and sensors
TFT_eSPI tft = TFT_eSPI();
MPU6050 mpu(Wire);
MAX30105 particleSensor;

// Animation frames array
const unsigned short* frames[] = {
  frame_000, frame_001, frame_002, frame_003, frame_004,
  frame_005, frame_006, frame_007, frame_008, frame_009
};

// Timing for animation
int frameIndex = 0;
unsigned long previousMillis = 0;
const long FRAME_INTERVAL = 100; // ms between frames

// Button pins
const int BUTTON1_PIN = 0;
const int BUTTON2_PIN = 35;
unsigned long buttonPressStart = 0;
bool bothButtonsPressed = false;
bool showingAlert = false;

// MPU-6050 variables
float prevAccX = 0, prevAccY = 0, prevAccZ = 0;
int stepCount = 0;
bool isStepDetected = false;
const float FALL_THRESHOLD = 2.5;

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

// Function prototypes
void initDisplay();
void initMPU();
void initMAX();
void handleButtonsAndAnimation();
void handleMPU();
void handleMAX();

void setup() {
  Serial.begin(115200);
  initDisplay();
  initMPU();
  initMAX();
}

void loop() {
  // Manage buttons and background animation or alerts
  handleButtonsAndAnimation();

  // Update MPU sensor and display step count / fall alerts
  mpu.update();
  handleMPU();

  // Handle MAX30102 measurements and Serial output
  handleMAX();

  delay(200); // Small pause to avoid flooding Serial
}

// Initialize TFT display and button inputs
void initDisplay() {
  tft.begin();
  tft.setRotation(0);
  tft.setSwapBytes(true);
  tft.fillScreen(TFT_WHITE);

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
  delay(1000);
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
    while (1) delay(100);
  }
  particleSensor.setup(
    /* ledBrightness   */ 0x1F,
    /* sampleAverage   */ 4,
    /* ledMode         */ 2,
    /* sampleRate      */ FreqS,
    /* pulseWidth      */ 411,
    /* adcRange        */ 4096
  );
  Serial.println("MAX30102 listo.");
}

// Handle button inputs and display animation or alerts
void handleButtonsAndAnimation() {
  unsigned long currentMillis = millis();
  bool b1 = digitalRead(BUTTON1_PIN) == LOW;
  bool b2 = digitalRead(BUTTON2_PIN) == LOW;

  // Both buttons pressed -> long-press alert
  if (b1 && b2) {
    if (!bothButtonsPressed) {
      buttonPressStart = currentMillis;
      bothButtonsPressed = true;
    } else if (currentMillis - buttonPressStart >= 2500 && !showingAlert) {
      tft.fillScreen(TFT_RED);
      tft.setTextColor(TFT_WHITE);
      tft.setTextSize(2);
      tft.drawString("ALERTA:", 30, 90);
      tft.drawString("Ambos botones", 1, 120);
      tft.drawString("Presionados!", 1, 150);
      Serial.println("ALERTA: botones presionados");
      showingAlert = true;
      bothButtonsPressed = false;
      delay(2000); // Show alert for 2 seconds
    }
  } else {
    bothButtonsPressed = false;
    showingAlert = false;
  }

  // Single button press -> warning state
  if (b1 || b2) {
    tft.fillScreen(TFT_YELLOW);
    tft.setTextColor(TFT_BLACK);
    tft.setTextSize(2);
    tft.drawString("Boton", 30, 100);
    tft.drawString("Presionado!", 10, 130);
  }
  // No buttons pressed -> background animation
  else if (!showingAlert) {
    if (currentMillis - previousMillis >= FRAME_INTERVAL) {
      previousMillis = currentMillis;
      tft.pushImage(0, 0, 160, 235, frames[frameIndex]);
      frameIndex = (frameIndex + 1) % 10;
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
  if ((dX > FALL_THRESHOLD || dY > FALL_THRESHOLD || dZ > FALL_THRESHOLD) && !showingAlert) {
    tft.fillScreen(TFT_RED);
    tft.setTextColor(TFT_WHITE);
    tft.setTextSize(2);
    tft.drawString("ALERTA: CAIDA", 0, 90);
    Serial.println("ALERTA: Caida detectada");
    showingAlert = true;
  }

  // Step detection on Z-axis
  if (abs(accZ - prevAccZ) > 0.75) {
    stepCount++;
    isStepDetected = true;
  } else {
    isStepDetected = false;
  }

  prevAccX = accX;
  prevAccY = accY;
  prevAccZ = accZ;

  // Display step count and detection status
  tft.setTextColor(TFT_BLACK, TFT_WHITE);
  tft.setTextSize(2);
  tft.setCursor(10, 200);
  tft.printf("Pasos: %d", stepCount);
  tft.setCursor(10, 220);
  if (isStepDetected) {
    tft.printf("Paso detectado!");
  }
}

// Acquire data from MAX30102, compute HR/SpO2, and output to Serial
void handleMAX() {
  // Wait for a new sample
  while (!particleSensor.available()) {
    particleSensor.check();
  }
  uint32_t ir = particleSensor.getIR();
  uint32_t red = particleSensor.getRed();
  particleSensor.nextSample();

  // Finger removed -> show final results
  if (ir < IR_THRESHOLD) {
    if (maxState == ANALYSING) {
      fingerRemovedMillis = millis();
      maxState = SHOW_RESULTS;
    }
    if (maxState == SHOW_RESULTS && (millis() - fingerRemovedMillis) > 3000) {
      Serial.printf("RESULTADOS FINALES - AvgHR=%ld BPM AvgSpO2=%ld %%\n",
                    lastAvgHR, lastAvgSpO2);
      maxState = WAITING;
    }
    return;
  }

  // Start measurement when finger detected
  if (maxState == WAITING) {
    maxState = ANALYSING;
    sumHR = sumSpO2 = 0;
    countHR = countSpO2 = 0;
    firstFill = true;
    Serial.println("Dedo detectado: comenzando medicion");

  }

  // Fill or shift buffers
  if (firstFill) {
    for (int i = 0; i < BUFFER_SIZE; i++) {
      while (!particleSensor.available()) particleSensor.check();
      redBuffer[i] = particleSensor.getRed();
      irBuffer[i]  = particleSensor.getIR();
      particleSensor.nextSample();
    }
    firstFill = false;
  } else {
    // Shift existing data
    for (int i = 0; i < BUFFER_SIZE - FreqS; i++) {
      redBuffer[i] = redBuffer[i + FreqS];
      irBuffer[i]  = irBuffer[i + FreqS];
    }
    redBuffer[BUFFER_SIZE - FreqS] = red;
    irBuffer[BUFFER_SIZE - FreqS]  = ir;
    for (int j = BUFFER_SIZE - FreqS + 1; j < BUFFER_SIZE; j++) {
      while (!particleSensor.available()) particleSensor.check();
      redBuffer[j] = particleSensor.getRed();
      irBuffer[j]  = particleSensor.getIR();
      particleSensor.nextSample();
    }
  }

  // Compute HR and SpO2
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, BUFFER_SIZE,
    redBuffer,
    &spo2, &validSPO2,
    &heartRate, &validHR
  );

  // Filter and average results
  bool hrOK   = validHR   && heartRate  > 0 && heartRate  <= 200;
  bool spo2OK = validSPO2 && spo2       > 0 && spo2       <= 100;
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

  // Serial output
  if (hrOK && spo2OK) {
    Serial.printf("HR=%ld SpO2=%ld AvgHR=%ld AvgSpO2=%ld\n",
                  heartRate, spo2, lastAvgHR, lastAvgSpO2);
  } else {
    Serial.printf("Señal errónea - HR=%ld(%d) SpO2=%ld(%d)\n",
                  heartRate, validHR, spo2, validSPO2);
  }
}