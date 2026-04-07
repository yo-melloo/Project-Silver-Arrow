# 🚀 Quick Start - ESP32 Telemetry Client (Arduino IDE)

## ⚡ Começar em 5 minutos

### Passo 1: Preparar o Ambiente
1. Instale a [Arduino IDE 2.x](https://www.arduino.cc/en/software)
2. No Gerenciador de Placas (Board Manager), instale o suporte para **ESP32** (by Espressif Systems)
3. No Gerenciador de Bibliotecas (Library Manager), instale:
   - `ArduinoJson` (by Benoit Blanchon)
   - `WebSockets` (by Markus Sattler)
   - `Adafruit NeoPixel` (by Adafruit)

### Passo 2: Configurar o Código (Segurança)
1. No diretório do projeto, localize `config.h.example`.
2. Faça uma cópia e renomeie para `config.h`.
3. Edite o `config.h` com seu **SSID**, **Senha** e o `BRIDGE_IP` do seu computador.
   - *Dica:* Veja [[docs/argentum_memory_mappings.md|Como encontrar o IP do Bridge]].

### Passo 3: Upload 🔌
1. Conecte o ESP32 via USB
2. Selecione a porta COM correta e o modelo da sua placa (ex: ESP32 Dev Module)
3. Clique em **Upload** (Seta para a direita)

---

## 🎮 Comportamento Visual

| Cor | Significado |
|-----|-------------|
| **Verde Suave (Breathe)** | Standby / Aguardando Simulador |
| **Verde Fixo** | Rotação OK |
| **Amarelo Pulsante** | **SHIFT NOW!** (Alerta de Troca) |
| **Vermelho Piscante** | **REDLINE** (Corte de Giro) |

---

## ❌ Diagnóstico Rápido

**Problema:** "WiFi Connection Failed" no Serial Monitor
- ✅ Verifique se o SSID/Senha estão corretos e se a rede é 2.4GHz.

**Problema:** "[WS] Connection Failed"
- ✅ Garanta que o `Argentum Bridge` está rodando no seu PC.
- ✅ Verifique se o Firewall do Windows não está bloqueando a porta `8001`.

**Problema:** LED não acende
- ✅ Verifique se o `LED_PIN` no código coincide com o pino da sua placa.
