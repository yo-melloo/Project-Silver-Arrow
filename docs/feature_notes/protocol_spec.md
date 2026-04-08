# 📡 Especificação do Protocolo - Argentum Bridge

Documentação técnica do fluxo de dados via WebSockets entre o **Argentum Bridge** e seus clientes.

## 🏛️ Visão Geral
O protocolo utiliza WebSockets (ws://) para transmissão de objetos JSON em tempo real (60 FPS / 16.6ms). Existem dois perfis de entrega baseados no parâmetro de conexão `?client=`.

---

## 🏎️ 1. Cliente ESP32 (`?client=esp`)

Projetado para microcontroladores com recursos limitados (ESP32). O objeto é reduzido para evitar fragmentação de pacotes e diminuir o tempo de processamento do parser `ArduinoJson`.

### Formato JSON
```json
{
  "rpm": 8500,
  "max_rpm": 10000,
  "speed": 240,
  "gear": "4",
  "car": "Ferrari F4"
}
```

### Detalhes do Payload
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `rpm` | `int` | Rotações por minuto correntes. |
| `max_rpm` | `int` | Redline do carro atual (dinâmico). |
| `speed` | `int` | Velocidade em KM/H. |
| `gear` | `string` | Marcha atual (R, N, 1, 2...). |
| `car` | `string` | Nome do carro (truncado para 10 caracteres). |

---

## 🌐 2. Cliente Web (`?client=web` ou padrão)

Objeto completo contendo telemetria avançada para dashboards analíticos e integração com o mascoste ASCII.

### Formato JSON
```json
{
  "source": "SIMULATOR (AC)",
  "pilot": "GUSTAVO",
  "car": "Ferrari_F430",
  "packet": 1542,
  "rpm": 8500,
  "max_rpm": 10000,
  "speed": 240,
  "gear": "4",
  "throttle": 100.0,
  "brake": 0.0,
  "clutch": 0.0,
  "steer": -15.4,
  "timestamp": "22:33:45.123"
}
```

### Detalhes Adicionais (Fase 3/4)
- **Inputs Analógicos:** Throttle, Brake e Clutch são normalizados entre `0.0` e `100.0`.
- **Steer:** Ângulo do volante em graus físicos.

---

## 🚦 Timings & Frequência
- **Sincronismo:** 1:1 com a leitura da [[docs/argentum_memory_mappings.md|Shared Memory]].
- **Heartbeat:** O Bridge envia um ping a cada 5 segundos para manter a conexão ativa (especialmente vital para WiFi do ESP32).
- **Latency Target:** < 20ms da memória até o hardware.

---
*Referência Técnica para: [[firmware_esp32/argentum_esp32_client/argentum_esp32_client.ino|ESP32 Client]] & [[dashboard_web/src/|Dashboard Web]].*
