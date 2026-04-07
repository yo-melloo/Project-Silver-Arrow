/*
 * Argentum Silver Arrow - ESP32 Telemetry Client (ULTRA-FAST SYNC)
 * 
 * Sincronizado com OpenRGB e Dashboard:
 * - 60 FPS (16ms)
 * - Thresholds universais do Argentum
 */

#include <WiFi.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>
#include <Adafruit_NeoPixel.h>

#include "config.h"

// ==========================================
// CONFIGURAÇÕES AUTOMÁTICAS (DE CONFIG.H)
// ==========================================
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD; 
const char* bridge_ip = BRIDGE_IP; 
const uint16_t bridge_port = BRIDGE_PORT;

// Hardware (Now from config.h)
// #define LED_PIN from config.h
// #define NUM_LEDS from config.h
// #define BRIGHTNESS from config.h

// ==========================================
// ESTADOS E VARIÁVEIS GLOBAIS
// ==========================================
WebSocketsClient webSocket;
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

unsigned long last_update = 0;
int current_rpm = 0;
int max_rpm = 10000;

// ==========================================
// LÓGICA DE CORES UNIVERSAL (OPENRGB SYNC)
// ==========================================

void updateLEDs() {
  uint32_t color;
  bool should_pulse = false;
  float pulse_speed = 1.0;
  float min_bright = 0.2; 

  float rpm_pct = (max_rpm > 0) ? (float)current_rpm / max_rpm : 0;

  if (rpm_pct < 0.10) {
    float val = (exp(sin(millis() / 2000.0 * PI)) - 0.36787944) * 108.0;
    color = strip.Color(0, val, 0);
  } 
  else if (rpm_pct < 0.60) {
    color = strip.Color(0, 255, 0);
  } 
  else if (rpm_pct < 0.85) {
    color = strip.Color(255, 255, 0);
    should_pulse = true;
    pulse_speed = 1.5;
    min_bright = 0.6;
  } 
  else if (rpm_pct < 0.95) {
    color = strip.Color(255, 128, 0);
    should_pulse = true;
    pulse_speed = 0.8;
    min_bright = 0.85;
  } 
  else {
    color = strip.Color(255, 0, 0);
    should_pulse = true;
    pulse_speed = 4.0;
    min_bright = 0.1;
  }

  if (should_pulse) {
    float elapsed = (millis() / 1000.0) * 2.0 * PI * pulse_speed;
    float sine_val = sin(elapsed);
    float pulse = min_bright + (1.0 - min_bright) * (sine_val + 1.0) / 2.0;
    
    uint8_t r = (uint8_t)((color >> 16 & 0xFF) * pulse);
    uint8_t g = (uint8_t)((color >> 8 & 0xFF) * pulse);
    uint8_t b = (uint8_t)((color & 0xFF) * pulse);
    color = strip.Color(r, g, b);
  }

  for(int i=0; i<NUM_LEDS; i++) {
    strip.setPixelColor(i, color);
  }
  strip.show();
}

// ==========================================
// EVENTOS E REDE
// ==========================================

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] ❌ Desconectado!");
      break;
    case WStype_CONNECTED:
      Serial.println("[WS] ✅ CONECTADO AO BRIDGE!");
      break;
    case WStype_TEXT:
      {
        StaticJsonDocument<384> doc;
        if (!deserializeJson(doc, payload)) {
          current_rpm = doc["rpm"];
          max_rpm = doc["max_rpm"];
        }
      }
      break;
    case WStype_ERROR:
      Serial.println("[WS] ⚠️ Erro de Handshake!");
      break;
    default: break;
  }
}

void WiFiEvent(WiFiEvent_t event) {
  if (event == ARDUINO_EVENT_WIFI_STA_GOT_IP) {
    Serial.print("📡 WiFi OK! IP: ");
    Serial.println(WiFi.localIP());
  } else if (event == ARDUINO_EVENT_WIFI_STA_DISCONNECTED) {
    WiFi.begin(ssid, password);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1500); // Crucial: Dá tempo para o Serial USB sincronizar
  
  Serial.println("\n\n=== Argentum Ultra-Fast Client v2 ===");
  
  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.show();

  WiFi.mode(WIFI_STA);
  WiFi.onEvent(WiFiEvent);
  WiFi.setSleep(false);
  WiFi.begin(ssid, password);

  webSocket.begin(bridge_ip, bridge_port, "/ws?client=esp");
  webSocket.enableHeartbeat(5000, 3000, 2); 
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(2000);
}

void loop() {
  webSocket.loop();
  
  if (millis() - last_update > 16) {
    updateLEDs();
    last_update = millis();
  }
  yield();
}
