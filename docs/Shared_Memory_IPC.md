---
id: SM_IPC_01
title: Shared Memory IPC (Inter-Process Communication)
tags: [architecture, python, assembly, performance]
---

# 🧠 Shared Memory IPC (Argentum Core)

O **Argentum Core** utiliza o conceito de **Mapeamento de Memória (mmap)** para extrair dados do Assetto Corsa. Esta é a forma mais rápida de IPC (Inter-Process Communication), pois evita o overhead de sockets ou arquivos temporários para a troca de dados entre o executável do simulador (C++) e o script Python.

## 🧱 Como Funciona?
1.  **Simulador:** O Assetto Corsa escreve continuamente estruturas de dados em um bloco de memória RAM chamado "Shared Memory".
2.  **Identificadores:** Esses blocos possuem nomes específicos (`acpmf_physics`, `acpmf_static`).
3.  **Python:** O script Argentum utiliza a biblioteca `mmap` para "espiar" esse endereço de memória em tempo real.

## 🧬 Anatomia da Decodificação (Python)

A leitura não é feita por chaves/valores, mas por **offsets fixos** (posições de bytes). 

### Exemplo: Extraindo RPM
No Assetto Corsa, o RPM está na estrutura `physics` na posição de byte **20** e é um inteiro de 4 bytes (`i`).

```python
import mmap
import struct

# 1. Mapeia a memória
shm = mmap.mmap(0, 1024, "acpmf_physics", access=mmap.ACCESS_READ)

# 2. Busca o offset 20
shm.seek(20)

# 3. Desempacota (struct.unpack) o binário para inteiro
rpm = struct.unpack("i", shm.read(4))[0]
```

## 📉 Didática: O Desafio dos Tipos
-   `i`: Inteiro (4 bytes) - Usado para RPM, Gear, Packet ID.
-   `f`: Float (4 bytes) - Usado para Speed, Throttle, Brake.
-   `utf-16`: Codificação de texto - Usado para o nome do carro e piloto.

## 🔗 Referências Internas
- [[argentum_memory_mappings.md|Mapas de Memória Detalhados]]
- [[protocol_spec.md|Protocolo de Sincronismo (Fase 2)]]

---
*Mentoria: @mentor (Obsidian Vault Ready)*
