# Argentum Memory Mappings & Offsets

## Overview

Este documento registra todos os offsets descobertos da memória compartilhada do Assetto Corsa, incluindo sucessos e tentativas fallidas.

**Data de Atualização:** 6 de Abril de 2026

---

## ✅ Offsets Confirmados & Funcionando

### Static Map (`acpmf_static` - 1024 bytes)

| Offset | Tamanho  | Tipo      | Campo          | Status        | Notas                          |
| ------ | -------- | --------- | -------------- | ------------- | ------------------------------ |
| 68     | 66 bytes | UTF-16 LE | Car Model Name | ✅ CONFIRMADO | Ex: `mclaren_mp412c_gt3`       |
| 200    | 66 bytes | UTF-16 LE | Pilot Name     | ✅ CONFIRMADO | Ex: `Mello`                    |
| 412    | 4 bytes  | Int32     | Max RPM        | ✅ CONFIRMADO | ~7500 para McLaren MP4-12C GT3 |

### Physics Map (`acpmf_physics` - 1024 bytes)

| Offset | Tamanho | Tipo  | Campo              | Status        | Notas                   |
| ------ | ------- | ----- | ------------------ | ------------- | ----------------------- |
| 0      | 4 bytes | Int32 | Packet ID          | ✅ CONFIRMADO | Incrementa a cada frame |
| 4      | 4 bytes | Float | Gas/Throttle (0-1) | ✅ CONFIRMADO | Valor normalizado       |
| 8      | 4 bytes | Float | Brake (0-1)        | ✅ CONFIRMADO | Valor normalizado       |
| 16     | 4 bytes | Int32 | Gear Raw           | ✅ CONFIRMADO | -1=R, 0=N, 1+=Gears     |
| 20     | 4 bytes | Int32 | RPM                | ✅ CONFIRMADO | Valor absoluto em RPM   |
| 24     | 4 bytes | Float | Steering Angle     | ✅ CONFIRMADO | Em graus (-450 a +450)  |
| 28     | 4 bytes | Float | Speed KM/H         | ✅ CONFIRMADO | Valor absoluto          |
| 328    | 4 bytes | Float | Clutch (0-1)       | ✅ CONFIRMADO | Valor normalizado       |

---

## ⚠️ Offsets Testados Mas Inválidos

| Offset                                          | Esperado | Encontrado                      | Motivo da Falha                    |
| ----------------------------------------------- | -------- | ------------------------------- | ---------------------------------- |
| 96, 380, 484, 488, 500, 504, 508, 512, 516, 520 | Max RPM  | Valores incorretos ou inválidos | Testados com filtro 4000-15000 RPM |

---

## ❌ Pendente: Session Time (Tempo de Sessão)

### Status: INVESTIGAÇÃO EM PROGRESSO

O tempo da sessão do Assetto Corsa **não foi localizado** nos primeiros 1024 bytes de ambos os mmaps.

**Possibilidades:**

1. ❓ Pode estar em um novo mmap que não foi descoberto ainda
2. ❓ Pode estar em uma estrutura diferente (não no static/physics map padrão)
3. ❓ Pode estar em centésimos ou milissegundos com transformação especial
4. ❓ Assetto Corsa v1.16.4 pode ter movido esse dado

**Scripts de Debug Criados:**

- `debug_session_time.py` - Procura por valores específicos (2700 para 45 min)
- `debug_realtime_values.py` - Monitora mudanças em tempo real

**Próximos Passos:**

- Testar com diferentes durations de sessão (1h, 30min, etc)
- Procurar em offsets > 1024 bytes
- Verificar documentação oficial do Assetto Corsa API

---

## 🎨 Tratamento de Dados

### Formatação de Nome de Carro

```python
def format_car_name(name: str) -> str:
    """
    Transforma: "ferrari_f430" → "Ferrari F430"
    - Remove underscores e converte para espaços
    - Aplica Title Case (capitaliza cada palavra)
    """
    formatted = name.replace("_", " ").title()
    return formatted
```

**Exemplos:**

- `porsche_911_carrera` → `Porsche 911 Carrera`
- `lamborghini_huracan` → `Lamborghini Huracan`
- `bmw_m3_evo` → `Bmw M3 Evo`

### Conversão de Valores Normalizados

```python
# Pedais (0-1 float para %)
throttle_percent = gas * 100
brake_percent = brake * 100
clutch_percent = clutch * 100

# Gear handling
gear_display = "R" if gear_raw == -1 else "N" if gear_raw == 0 else str(gear_raw)
```

---

## 🚀 Implementação: Dashboard Web

### Integração com WebSocket (port 8001)

A dashboard React se conecta ao bridge FastAPI via WebSocket:

```typescript
const url = `ws://${window.location.hostname}:8001/ws`;
const socket = new WebSocket(url);

socket.onmessage = (event) => {
  const telemetry = JSON.parse(event.data);
  // Atualizar UI com dados do jogo
};
```

### Informações Exibidas

- ✅ **Driver Name** (pilot)
- ✅ **Car Model** (formatado)
- ✅ **Data Source** (AC ou MOCK)
- ✅ **Timestamp** (tempo do sistema)
- ✅ **Speed** (KM/H)
- ✅ **Gear** (R/N/1-6)
- ✅ **RPM** (com barra % até max)
- ✅ **Throttle, Brake, Clutch** (%)
- ✅ **Steering Angle** (-450° a +450°)
- ✅ **Packet Count** (frame counter)

### Status: ✅ COMPLETO

---

## 🔧 Resolução de Problemas

### [RESOLVIDO] Tailwind CSS não carregava

**Problema:** Usando v4 (`@tailwindcss/postcss`) com globals.css v3  
**Solução:** Trocar `@tailwind base/components/utilities` por `@import "tailwindcss"`

### [RESOLVIDO] RPM bar não chegava a 100%

**Problema:** Max RPM estava em offset 500 (valor incorreto)  
**Solução:** Descobrir offset correto: **412** (lê ~7500 para McLaren)

### [RESOLVIDO] WebSocket não conectava do celular

**Problema:** Port 8000 em uso, Firewall bloqueando, cliente em localhost  
**Solução:**

1. Port mudado para 8001
2. Bridge listen em `0.0.0.0` (não apenas localhost)
3. Adicionar rule no Windows Firewall

### [PENDENTE] Tempo de sessão diverge

**Problema:** Dashboard exibe tempo do sistema, não sincroniza com pausa do jogo  
**Status:** Em investigação - offset do session time não encontrado ainda

---

## 📋 Arquivos Afetados

### Backend (Python)

- `argentum_core.py` - Provider class com offsets
- `argentum_bridge.py` - FastAPI WebSocket server (port 8001)
- `debug_ac_memory.py` - Dump completo de memória
- `debug_session_time.py` - Busca especializada por session time
- `debug_realtime_values.py` - Monitor em tempo real

### Frontend (React/Next.js)

- `dashboard_web/src/app/page.tsx` - Dashboard UI completa
- `dashboard_web/src/app/globals.css` - Styles com Tailwind v4
- `dashboard_web/postcss.config.js` - Config para PostCSS com v4
- `dashboard_web/tailwind.config.js` - Tailwind configuration

---

## 📚 Versões Utilizadas

- **Assetto Corsa:** v1.16.4
- **Python:** 3.x
- **FastAPI:** latest
- **React:** 19.x (latest)
- **Next.js:** 16.2.2 (com Turbopack)
- **Tailwind CSS:** v4
- **Node.js:** latest

---

## 🎯 Checklist de Funcionalidades

- [x] Ler dados do Assetto Corsa via mmap
- [x] Validar offsets de physics map
- [x] Validar offsets de static map (car, driver, max_rpm)
- [x] WebSocket server funcionando
- [x] Dashboard conectando ao WebSocket
- [x] Formatação de nomes de carros
- [x] Exibição de RPM com barra colorida
- [x] Exibição de pedais (throttle, brake, clutch)
- [x] Exibição de steering angle com visualizador
- [x] Modo mock para teste sem jogo
- [ ] Sincronizar tempo de sessão com o jogo
- [ ] Detectar pause/unpause do jogo
- [ ] Adicionar histórico de telemetria
- [ ] Melhorar UI para mobile

---

## 🤝 Contatos & Referências

- **Projeto:** Project Silver Arrow
- **Data Início:** 6 de Abril de 2026
- **Status:** Em desenvolvimento ativo
