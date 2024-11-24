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
unsigned long previousMillis = 0; // Almacena el tiempo anterior
const long interval = 100;  // Intervalo entre fotogramas en milisegundos

void setup() {
  tft.begin(); // Inicia la pantalla correctamente
  tft.setRotation(0);  // Establece la orientación de la pantalla (prueba con 0, 1, 2, o 3)
  tft.setSwapBytes(true);  // Esto es necesario o los colores no sé leeran correctamente
  tft.fillScreen(TFT_WHITE); // establecer que aquellas partes que no sé cubran sea en blanco inicialmente
}

void loop() {
  unsigned long currentMillis = millis();  // Captura el tiempo actual

  // Si el tiempo actual menos el tiempo anterior es mayor que el intervalo
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;  // Actualiza el tiempo anterior

    // Dibuja el fotograma 
    tft.pushImage(0, 0, 160, 235, frames[frameIndex]);

    // Avanza al siguiente fotograma
    frameIndex++;
    if (frameIndex >= 10) {
      frameIndex = 0;  // Vuelve al primer fotograma cuando termine
    }
  }
}
