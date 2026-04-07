# 🏎️ Argentum Silver Arrow - ESP32 Firmware

Firmware oficial para integração de hardware (Shift-Lights, LEDs, Displays) com o ecossistema de telemetria **Argentum**.

> [!IMPORTANT]  
> **Transição:** O projeto migrou do MicroPython para **Arduino (C++)** para maior performance e compatibilidade com bibliotecas de hardware.

## 🚀 Como Começar (Arduino IDE)

1.  **Instale as Bibliotecas:**
    *   `ArduinoJson` (by Benoit Blanchon)
    *   `WebSockets` (by Markus Sattler)
    *   `Adafruit NeoPixel` (se usar fita de LED ou LED RGB integrado)

2.  **Configuração (Segurança):**
    *   **NÃO** edite o arquivo `.ino` diretamente.
    *   Copie `config.h.example` para um novo arquivo chamado `config.h`.
    *   Insira seu **SSID**, **Senha** e o `BRIDGE_IP` no `config.h`.
    *   O arquivo `config.h` é automaticamente ignorado pelo Git para sua proteção de privacidade.

3.  **Upload:**
    *   Selecione sua placa (ex: ESP32 Dev Module, S3, C3).
    *   Configure o `LED_PIN` no código de acordo com o GPIO físico utilizado.

## 🎮 Comportamento Visual

*   **Standby (Simulador Offline):** O LED executa uma animação "Breathe" (Verde suave).
*   **Em Corrida:**
    *   🟢 **Verde:** RPM normal.
    *   🟡 **Amarelo Pulsante:** Aviso de troca de marcha (Shift Warning).
    *   🟠 **Laranja:** RPM Crítico.
    *   🔴 **Vermelho Piscante:** Redline / Corte de Giro.

## 🔗 Integração
O firmware conecta-se automaticamente ao endpoint `/ws?client=esp` na porta `8001` do Argentum Bridge.
