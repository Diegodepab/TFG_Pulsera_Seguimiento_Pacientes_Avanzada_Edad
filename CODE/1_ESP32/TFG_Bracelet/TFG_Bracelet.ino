#include <Wire.h>
#include <MPU6050_light.h>
#include <TFT_eSPI.h> // Librería de la pantalla TFT

// Incluir los archivos .h generados para cada fotograma
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

// Crear objeto TFT y MPU
TFT_eSPI tft = TFT_eSPI();
MPU6050 mpu(Wire);

const unsigned short* frames[] = {frame_000, frame_001, frame_002, frame_003, frame_004, frame_005, frame_006, frame_007, frame_008, frame_009};

int frameIndex = 0;
unsigned long previousMillis = 0;  // Almacena el tiempo anterior
const long interval = 100;         // Intervalo entre fotogramas en milisegundos

// Definir pines de los botones
const int button1 = 0;  // GPIO0
const int button2 = 35; // GPIO35

// Variables para controlar el tiempo de presionado de ambos botones
unsigned long buttonPressStart = 0;
bool bothButtonsPressed = false;
bool showingAlert = false;

// Variables para detección de pasos y caídas
float prevAccX = 0.0, prevAccY = 0.0, prevAccZ = 0.0; // Solo una vez
int stepCount = 0;
bool isStepDetected = false;

// Umbral para detección de caídas
const float FALL_THRESHOLD = 2.5;  // Ajusta según sea necesario

void setup() {
  // Inicialización de la pantalla
  tft.begin();
  tft.setRotation(0);
  tft.setSwapBytes(true);  // Colores correctos
  tft.fillScreen(TFT_WHITE);  // Fondo blanco

  // Configurar pines de botones como entrada
  pinMode(button1, INPUT_PULLUP);
  pinMode(button2, INPUT_PULLUP);

  // Inicializar la comunicación serie para el MPU-6050
  Serial.begin(9600);

  // Inicializar el MPU-6050
  Wire.begin(21, 22); // SDA en GPIO 21, SCL en GPIO 22
  Serial.println("Iniciando el MPU-6050...");
  byte status = mpu.begin();
  
  if (status != 0) {
    Serial.print("Error al iniciar el MPU-6050. Código: ");
    Serial.println(status);
    while (1);  // Detener si hay un error
  }

  Serial.println("Calibrando el MPU-6050...");
  delay(1000);
  mpu.calcOffsets(true, true);  // Calibración automática
  
  Serial.println("MPU-6050 iniciado y calibrado.");
}

void loop() {
  unsigned long currentMillis = millis();  // Captura el tiempo actual

  // Leer el estado de los botones
  bool button1State = digitalRead(button1) == LOW;
  bool button2State = digitalRead(button2) == LOW;

  // Manejo de botones
  if (button1State && button2State) {
    if (!bothButtonsPressed) {
      buttonPressStart = currentMillis;
      bothButtonsPressed = true;
    } else if (currentMillis - buttonPressStart >= 2500 && !showingAlert) {
      tft.fillScreen(TFT_RED);  // Alerta en rojo
      tft.setTextColor(TFT_WHITE);
      tft.setTextSize(2);
      tft.drawString("ALERTA: ", 30, 90);
      tft.drawString("Ambos botones", 1, 120);
      tft.drawString("Presionados!", 1, 150);
      delay(2000);  // Mantener la alerta visible 2 segundos
      showingAlert = true;
      // Enviar alerta por serial
      Serial.println("ALERTA: botones presionados");
      bothButtonsPressed = false;
    }
  } else {
    bothButtonsPressed = false;
    showingAlert = false;
  }

  // Si un solo botón está presionado
  if (button1State || button2State) {
    tft.fillScreen(TFT_YELLOW);
    tft.setTextColor(TFT_BLACK);
    tft.setTextSize(2);
    tft.drawString("Boton", 30, 100);
    tft.drawString("Presionado!", 10, 130);

  } else if (!showingAlert) {
    // Animación cuando no hay botones presionados
    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;
      tft.pushImage(0, 0, 160, 235, frames[frameIndex]);

      frameIndex++;
      if (frameIndex >= 10) {
        frameIndex = 0;
      }
    }
  }

  // Lectura y actualización de datos del MPU-6050
  mpu.update();

  // Detección básica de pasos basada en cambios de aceleración en el eje Z
  float accX = mpu.getAccX();
  float accY = mpu.getAccY();
  float accZ = mpu.getAccZ();
  
  // Detección de caídas
  float deltaAccX = abs(accX - prevAccX);
  float deltaAccY = abs(accY - prevAccY);
  float deltaAccZ = abs(accZ - prevAccZ);

  if (deltaAccX > FALL_THRESHOLD || deltaAccY > FALL_THRESHOLD || deltaAccZ > FALL_THRESHOLD) {
    if (!showingAlert) {
      tft.fillScreen(TFT_RED);  // Alerta en rojo
      tft.setTextColor(TFT_WHITE);
      tft.setTextSize(2);
      tft.drawString("ALERTA: CAÍDA DETECTADA", 0, 90);
      showingAlert = true;

      // Enviar alerta por serial
      Serial.println("ALERTA: Caída detectada");
    }
  }

  // Detección de pasos basada en cambios de aceleración en el eje Z
  if (abs(accZ - prevAccZ) > 0.75) {  // Ajusta el umbral según sea necesario
    stepCount++;
    isStepDetected = true;
  } else {
    isStepDetected = false;
  }

  prevAccX = accX;
  prevAccY = accY;
  prevAccZ = accZ;

  // Mostrar número de pasos y si se detecta un paso en la pantalla
  tft.setTextColor(TFT_BLACK, TFT_WHITE); // Texto negro con fondo blanco para mejor visibilidad
  tft.setTextSize(2);  // Tamaño más grande para los datos

  tft.setCursor(10, 200);  // Establecer posición para los datos
  tft.printf("Pasos: %d", stepCount);

  tft.setCursor(10, 220);  // Nueva línea para mostrar el estado de la detección
  if (isStepDetected) {
    tft.printf("Paso detectado!");
  } else {
    tft.printf("");
  }

  delay(200);  // Pausa pequeña para no saturar el serial
}
