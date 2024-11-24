#include <TFT_eSPI.h>

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

// Crear un array de punteros a los datos de los fotogramas
const unsigned short* frames[] = {frame_000, frame_001, frame_002, frame_003, frame_004, frame_005, frame_006, frame_007, frame_008, frame_009};

void setup() {
  tft.begin();         // Inicia la pantalla correctamente
  tft.setRotation(0);  // Establece la orientación de la pantalla (prueba con 0, 1, 2, o 3)
  tft.setSwapBytes(true); //IMPORTANTE SIN ESTO LOS COLORES SE INVIERTEN
  tft.fillScreen(TFT_WHITE);
}

void loop() {



  // FONDO DE PANTALLA
  for (int i = 0; i < 10; i++) {
    // Dibuja cada fotograma en la pantalla
    tft.pushImage(0, 0, 160, 235, frames[i]);
    
    // Ajusta el tiempo de espera entre fotogramas (velocidad de la animación)
    delay(100);  // 100 ms entre fotogramas, ajusta este valor para cambiar la velocidad
  }
}