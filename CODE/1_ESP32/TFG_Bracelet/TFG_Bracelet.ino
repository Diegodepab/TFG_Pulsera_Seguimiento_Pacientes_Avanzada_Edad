#include <TFT_eSPI.h> // Al usar un TTGO es mejor trabajar con la librería <TFT_eSPI.h> 

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

TFT_eSPI tft = TFT_eSPI();  // Crear el objeto TFT

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

void setup() {
  tft.begin();             // Inicia la pantalla correctamente
  tft.setRotation(0);      // Establece la orientación de la pantalla
  tft.setSwapBytes(true);  // Necesario para que los colores se lean correctamente
  tft.fillScreen(TFT_WHITE);  // Establecer fondo blanco inicialmente

  // Configurar los pines de los botones como entradas
  pinMode(button1, INPUT_PULLUP);  // Usamos PULLUP ya que no tienen resistencia externa
  pinMode(button2, INPUT_PULLUP);
}

void loop() {
  unsigned long currentMillis = millis();  // Captura el tiempo actual

  // Leer el estado de los botones
  bool button1State = digitalRead(button1) == LOW;  // LOW significa que el botón está presionado
  bool button2State = digitalRead(button2) == LOW;

  // Si ambos botones están presionados
  if (button1State && button2State) {
    if (!bothButtonsPressed) {
      buttonPressStart = currentMillis;  // Registrar el tiempo cuando ambos se presionan
      bothButtonsPressed = true;
    } else if (currentMillis - buttonPressStart >= 5000 && !showingAlert) {
      // Si ambos botones han estado presionados por 5 segundos
      tft.fillScreen(TFT_RED);  // Cambiar pantalla a rojo
      tft.setTextColor(TFT_WHITE);
      tft.setTextSize(2);  // Aumentar el tamaño del texto
      tft.drawString("ALERTA: ", 30, 90);
      tft.drawString("Ambos botones", 1, 120);
      tft.drawString("Presionados!", 1, 150);
      delay(2000);  // Mantener la alerta visible 2 segundos
      showingAlert = true;  // Marcar que la alerta fue mostrada
      bothButtonsPressed = false;  // Resetear el estado de los botones
    }
  } else {
    bothButtonsPressed = false;  // Reiniciar si no están ambos botones presionados
    showingAlert = false;        // Resetear alerta
  }

  // Si solo se presiona un botón
  if (button1State || button2State) {
    tft.fillScreen(TFT_YELLOW); 
    tft.setTextColor(TFT_BLACK);
    tft.setTextSize(2);  
    tft.drawString("Boton", 30, 100);
    tft.drawString("Presionado!", 10, 130);

  } else if (!showingAlert) {
    // Si no hay botones presionados, mostrar la animación
    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;  // Actualizar el tiempo anterior

      // Dibuja el fotograma correspondiente
      tft.pushImage(0, 0, 160, 235, frames[frameIndex]);

      // Avanza al siguiente fotograma
      frameIndex++;
      if (frameIndex >= 10) {
        frameIndex = 0;  // Vuelve al primer fotograma cuando termine
      }
    }
  }

  delay(100);  // Pausa pequeña para evitar lecturas repetitivas
}