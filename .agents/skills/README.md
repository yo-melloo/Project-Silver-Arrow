# 🛠️ Skills e Workflow Operacional

Define como a equipe de agentes se organiza para entregar código e conhecimento de alta fidelidade.

---

## 🔄 Workflow de Desenvolvimento

1.  **Explicação Teórica:** @professor / @architect detalham o conceito (IPC, Redes, Física) e registram em `docs/`.
2.  **Arquitetura:** @architect define os offsets e a estrutura do dado.
3.  **Implementação:** @firmware ou @engineer escrevem o código (Python/C++).
4.  **Estresse:** @glitch tenta quebrar a lógica ou injetar latência.
5.  **Validação de Aprendizado:** Gustavo (com @professor) explica o que foi feito.

---

## 🧰 Habilidades Técnicas por Agente

| Agente | Habilidade Primária (Skills) | Ferramenta |
|--------|------------------------------|------------|
| @architect | System Design, IPC, ADRs | Python (mmap/struct) |
| @firmware | ESP32, NeoPixel, WebSockets | C++, Arduino IDE |
| @race_engineer | Car Data, Gear Ratios, PIDs | AC Telemetry |
| @glitch | Mock Data, Fuzzing, Unit Tests | Python / Mock Providers |

---
*Para ver os passos de manutenção de documentos, veja [[workflows/resync_docs.md|Workflow: /resync_docs]].*
