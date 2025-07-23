# Historial de Software de la pulsera

Este documento recoge los **hitos y versiones** más relevantes del software de la pulsera de seguimiento de paciente, con dos versiones finales consolidadas.


# Sobre el hardware usado

![esquema_prototipo](https://github.com/user-attachments/assets/c1c0bda9-d543-4e63-9689-f735c7d1760e)


## Componentes principales

- **TTGO T-Display (16 MB)**  
  Microcontrolador ESP32 con 16 MB de flash, Wi‑Fi/Bluetooth integrado, pantalla TFT 1.14″ y dos botones.  
  _Uso:_ gestión de la interfaz, almacenamiento de imágenes animadas, conexión a red y control de usuario.

- **MPU‑6050**  
  Acelerómetro de 3 ejes + giroscopio.  
  _Uso:_ medir movimientos (X, Y, Z) para conteo de pasos y detección de posibles caídas.

- **GY‑MAX30102**  
  Sensor óptico de frecuencia cardíaca y oximetría (SpO₂).  
  _Uso:_ lectura de pulsaciones por minuto (BPM) y nivel de oxigenación sanguínea.
## 1. Versión por Componentes (`1_Components`)
Cada subcarpeta contiene un sketch independiente para probar una función concreta:

- **0_Creation_of_wallpaper_for_the_band**  
  - Convierte GIFs o imágenes en arrays para Arduino TTGO T‑Display (16 MB).  
  - Demuestra un fondo animado en bucle y el manejo de botones para cambiar/pausar la animación.

- **1_GY-MAX30102_Azul**  
  - Prueba de lectura del sensor GY‑MAX30102:  
    - Pulsaciones por minuto (BPM).  
    - Nivel de oxigenación en sangre (SpO₂).  
  - Salida de datos por Serial para validación.

- **2_mpu650_test**  
  - Test del módulo MPU‑6050 (acelerómetro + giroscopio).  
  - Obtiene coordenadas X, Y, Z y ángulos de giro en tiempo real.

- **3_WIFI**  
  - Conexión básica Wi‑Fi en ESP32.  
  - Ejemplo de publicación MQTT a un broker local.

---

## 2. Prototipo Integrado Sin Red (`2_Prototype`)

- **Funciones incluidas**:  
  - Animación de pantalla.  
  - Sensor GY‑MAX30102 (HR/SpO₂).  
  - MPU‑6050 (pasos y detección de caídas).  
  - Botones y alertas visuales.  
- **Sin** conectividad Wi‑Fi ni MQTT.  
- ▶️ Demo en vídeo: https://www.youtube.com/watch?v=mRuG5VgCNkM

---

## 3. Prototipo con Wi‑Fi y MQTT (`3_WifiPrototype`)

- **Mejoras sobre el prototipo anterior**:  
  - Fondo de pantalla simplificado (ahorro de memoria).  
  - Sincronización NTP para hora UTC.  
  - Publicación periódica de métricas (`step_count`, `bpm`, `spo2`, `ts`).  
  - Alertas vía MQTT (`ALERTA_CAIDA`, `ALERTA_BOTON`, `ALERTA_BOTONES`).  

---

## Requisitos y Configuración

- **Hardware**: TTGO T‑Display ESP32 (16 MB), GY‑MAX30102, MPU‑6050.  
- **Librerías Arduino**:  
  - #include <Wire.h>
  - #include <TFT_eSPI.h>
  - #include <MPU6050_light.h>
  - #include <MAX30105.h>
  - #include "spo2_algorithm.h"
  - #include <WiFi.h>
  - #include <PubSubClient.h
  - #include <time.h>

