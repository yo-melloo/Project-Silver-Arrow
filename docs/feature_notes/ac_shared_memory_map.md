# Assetto Corsa Shared Memory Map (acpmf_)

Este documento mapeia os endereços de memória (Offsets) utilizados pelo Argentum para extrair telemetria em tempo real.

## 1. Physics Map (`acpmf_physics`)
**Frequência:** ~60Hz | **Tamanho do Buffer:** ~800-1024 bytes

| Offset | Tipo | Variável | Descrição |
| :--- | :--- | :--- | :--- |
| 0 | int | packetId | Contador de frames (Heartbeat) |
| 4 | float | gas | Posição do acelerador (0.0 a 1.0) |
| 8 | float | brake | Posição do freio (0.0 a 1.0) |
| 12 | float | fuel | Litros de combustível restantes |
| 16 | int | gear | Marcha (0=R, 1=N, 2=1ª...) |
| 20 | int | rpms | Rotação atual do motor |
| 24 | float | steerAngle | Ângulo do volante (Rad) |
| 28 | float | speedKmh | Velocidade em KM/H |
| 32 | float | clutch | Posição da embreagem (0.0 a 1.0) |
| 44 | float | wheelAngularSpeed[4] | Velocidade angular das 4 rodas |

## 2. Static Map (`acpmf_static`)
**Frequência:** Escrita única no início da sessão.

| Offset | Tipo | Variável | Descrição |
| :--- | :--- | :--- | :--- |
| 0 | wchar_t[15] | smVersion | Versão da Shared Memory |
| 30 | wchar_t[15] | acVersion | Versão do Assetto Corsa |
| 68 | wchar_t[33] | carModel | Nome/Modelo do carro |
| 134 | wchar_t[33] | track | Nome da pista |
| 200 | wchar_t[33] | playerName | Nome do piloto (UTF-16) |
| 500 | int | maxRpm | Rotação máxima suportada pelo motor |

---
*Nota: wchar_t em Windows utiliza 2 bytes por caractere (UTF-16).*
