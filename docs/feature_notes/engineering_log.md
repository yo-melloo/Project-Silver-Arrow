# Engineering Log - Argentum Core

## [2026-04-06] Inicialização do Core Modular

### Decisões Técnicas (ADRs):
1. **Frequência de 20 FPS:** Definida para equilibrar fluidez visual e baixo impacto de CPU no terminal Windows (`cmd.exe`).
2. **Interface Baseada em Classes:** Separação total entre `TelemetryProvider` (Dados), `ArgentumUI` (Visual) e `ArgentumEngine` (Sincronismo).

### Mapeamento de Tipos para Firmware (ESP32):
Para a **Fase 2**, os dados enviados via Serial/Bluetooth devem seguir este cabeçalho binário:
| Dado | Tipo C++ | Tamanho |
| :--- | :--- | :--- |
| RPM | uint16_t | 2 bytes |
| Speed | uint16_t | 2 bytes |
| Gear | uint8_t | 1 byte |
| Flag (DRS/ABS) | uint8_t | 1 byte |

**Total do Pacote:** 6 bytes por frame.

### [2026-04-06] Milestone: Argentum Full Stack
- **Backend:** Bridge FastAPI/WebSockets operacional (30 FPS).
- **Frontend:** Dashboard Next.js funcional com telemetria reativa.
- **UI/UX:** Implementação de marchas, velocidade, RPM progressivo e pedais.
- **Próximo Desafio:** Expansão de dados ou integração de hardware (ESP32).
