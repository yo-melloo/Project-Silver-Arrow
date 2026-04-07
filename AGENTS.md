# 🤖 Matriz de Agentes — Project-Silver-Arrow

## 👥 Responsabilidades Locais
- **@dev**: Firmware C++ (ESP32), Drivers de Hardware, Dashboard Next.js.
- **@devops**: Automação `arduino-cli`, Flash via Script.
- **@qa**: Monitoramento de Jitter em telemetria, Validação de ISR.
- **@glitch**: Buffer Overflow em strings C++, Injeção de ruído no barramento I2C.

## ✅ Critérios de Sucesso
1. Latência de telemetria fixa < 50ms.
2. Firmware estável em 24h de runtime.
3. Abstração de Hardware (Gustavo -> Universal) concluída.
