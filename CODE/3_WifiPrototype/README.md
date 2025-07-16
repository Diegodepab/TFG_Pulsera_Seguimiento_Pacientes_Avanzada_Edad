# Preparar y ejecutar el broker MQTT
Se puede usar Mosquitto para trabajar con el protocolo. Recomendamos probar el envío de mensajes desde el propio dispositivo, tanto en localhost como en la red local.

En Linux o WSL:
```
mosquitto_sub -h localhost -t pulsera/test -v
# en otra pestaña:
mosquitto_pub -h localhost -t pulsera/test -m "Test local OK"
```

Repite la prueba usando la dirección IPv4 de tu equipo, por ejemplo si es 192.168.135.238:
```
mosquitto_sub -h 192.168.135.238 -t pulsera/test -v
mosquitto_pub -h 192.168.135.238 -t pulsera/test -m "Test LAN OK"
```

## Configuración de Mosquitto
Si el broker no acepta conexiones externas, edita su configuración para simplificar el listener.

En Linux, añade al inicio de /etc/mosquitto/mosquitto.conf:
```
listener 1883 0.0.0.0
allow_anonymous true
```
Luego reinicia el servicio:

```
sudo systemctl restart mosquitto
```
En Windows, crea un archivo user_mosq.conf con:

```
listener 1883
allow_anonymous true
```
Y arranca Mosquitto en PowerShell:
```
cd "C:\Program Files\mosquitto"
.\mosquitto.exe -c .\user_mosq.conf -v
```
## Apertura del puerto 1883 en Windows Firewall
Para permitir conexiones entrantes al puerto MQTT (1883):

Pulsa Win + R, escribe wf.msc y pulsa Enter.

En Reglas de entrada, haz clic en Nueva regla….

Selecciona Puerto, elige TCP y especifica 1883.

Marca Permitir la conexión y sigue los pasos (perfiles: Dominio, Privado, Público).

Nombra la regla (por ejemplo, MQTT TCP 1883) y finaliza.

O bien, en PowerShell (ejecutado como administrador):

```
netsh advfirewall firewall add rule `
  name="MQTT Inbound" `
  dir=in action=allow `
  protocol=TCP localport=1883 `
  profile=Domain,Private,Public
```

## Uso de ESP32
Copia el ejemplo en Arduino IDE y añade las librerías necesarias.

Sustituye los marcadores:

```
const char* SSID        = "<TU_SSID>";
const char* PASSWORD    = "<TU_PASSWORD>";
const char* MQTT_BROKER = "<IP_BROKER>";
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "pulsera/test";
```
En setup(), sincroniza NTP y conecta a Wi‑Fi/MQTT.

En loop(), publica o suscribe mensajes según tu lógica.

Mientras Mosquitto esté activo y el firewall permita el puerto 1883, el ESP32 podrá enviar y recibir mensajes en pulsera/test.