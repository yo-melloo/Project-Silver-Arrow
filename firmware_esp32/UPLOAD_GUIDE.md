# 🔌 Guia de Upload - Argentum Firmware (C++)

Este guia detalha o processo de gravação do firmware utilizando a **Arduino IDE**.

## 1. Pré-requisitos de Software

### ✅ Arduino IDE 2.x
O projeto foi desenvolvido para a versão 2.0+ da Arduino IDE. [Download aqui](https://www.arduino.cc/en/software).

### ✅ Core ESP32
1. Vá em **File > Preferences**.
2. No campo **Additional Boards Manager URLs**, adicione:
   `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. Vá em **Tools > Board > Boards Manager**, procure por **ESP32** (by Espressif Systems) e instale.

### ✅ Bibliotecas Necessárias
No **Library Manager** (ícone de livros na barra lateral), instale as seguintes versões ou superiores:
*   `ArduinoJson` (v6.x ou v7.x)
*   `WebSockets` (v2.4.x - por Markus Sattler)
*   `Adafruit NeoPixel` (v1.12.x)

---

## 2. Configuração de Hardware no Código

Edite os seguintes parâmetros no arquivo `argentum_esp32_client.ino`:

```cpp
#define LED_PIN     2    // GPIO 2 é o padrão para LED azul integrado na maioria das placas
#define NUM_LEDS    1    // Mude para o número de LEDs da sua fita (ex: 8, 16, 24)
#define BRIGHTNESS  50   // Brilho (0-255). Cuidado: fita de LEDs consome muita corrente em brilho máximo!
```

---

## 3. Realizando o Upload

1. Conecte sua placa via USB.
2. No menu **Tools > Port**, selecione a porta correta (ex: `COM3`, `/dev/ttyUSB0`).
3. No menu **Tools > Board**, selecione o modelo da sua placa (Ex: `ESP32 Dev Module`).
4. Clique no botão **Upload** (Seta para a direita).
5. O monitor serial (**Ctrl+Shift+M**) deve estar configurado para **115200 baud**.

---

## ⚠️ Problemas Comuns de Upload

### 🔴 "Failed to connect to ESP32: No serial data received"
**Causa:** O ESP32 não entrou em modo de gravação.
**Solução:** Quando aparecer `Connecting...` no console, mantenha pressionado o botão **BOOT** da placa até que o upload comece.

### 🔴 Erro de Compilação: "ArduinoJson.h: No such file or directory"
**Causa:** Biblioteca não instalada.
**Solução:** Siga o passo "Bibliotecas Necessárias" acima.

### 🔴 Monitor Serial mostrando caracteres estranhos (Gritch)
**Causa:** Baud rate incorreto.
**Solução:** Mude a velocidade do Monitor Serial para **115200**.
