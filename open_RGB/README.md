# OpenRGB Shift Lights Integration

Integração com **OpenRGB** para controlar luzes RGB do seu computador baseado nos dados de telemetria do Assetto Corsa. Funciona como shift-lights virtuais enquanto o ESP32 não está programado.

## 🎯 Objetivo

- Ler dados em tempo real do Assetto Corsa (RPM, velocidade, marcha)
- Controlar dispositivos RGB conectados ao computador via OpenRGB SDK
- **Sincronizar com Argentum Bridge para obter maxRpm do carro** (novo!)
- Criar efeito de shift-lights dinâmico com **animações sincronizadas**
  - 🟢 **Verde** (steady): Rotações normais/ocioso
  - 🟡 **Amarelo** (pulsante): Elevações de rotação detectadas
  - 🟠 **Laranja** (steady): Motor em rotações críticas
  - 🔴 **Vermelho** (pulsante forte): Motor sendo forçado/redline

## 🌟 Novidade: RPM Dinâmicos por Carro

**O sistema agora detecta o RPM máximo de cada carro automaticamente!**

Em vez de usar thresholds fixos (ex: redline=9000 para todos), o OpenRGB:

- ✅ Lê `maxRpm` direto do Assetto Corsa
- ✅ Calcula thresholds como % do maxRpm (75%, 90%, 100%)
- ✅ Funciona com qualquer carro (F1 15000 RPM, SUV 5500 RPM, etc)
- ✅ Se disponível, sincroniza com **Argentum Bridge** para dados adicionais

### 📊 Exemplo de Thresholds Dinâmicos

| Carro   | MaxRPM | Idle | Warning | Critical | Redline |
| ------- | ------ | ---- | ------- | -------- | ------- |
| Ferrari | 8000   | 1200 | 6000    | 7200     | 8000    |
| F1 2023 | 15000  | 2250 | 11250   | 13500    | 15000   |
| SUV     | 5500   | 825  | 4125    | 4950     | 5500    |

## 🎨 Efeitos de Animação

O sistema detecta o estado do motor em tempo real:

| Estado           | Cores         | Efeito                  | Quando Ativa                         |
| ---------------- | ------------- | ----------------------- | ------------------------------------ |
| **Idle**         | Verde         | Steady                  | RPM < 2000                           |
| **Normal**       | Verde/Amarelo | Steady                  | 2000 ≤ RPM < 6000                    |
| **Rising**       | Amarelo       | Pulso suave (1.5 Hz)    | Quando detecta aumento rápido de RPM |
| **Critical**     | Laranja       | Pulso leve (0.8 Hz)     | 8000 ≤ RPM < 9000                    |
| **Forced**       | Vermelho      | Pulso moderado (2.5 Hz) | Motor sendo forçado                  |
| **Past Redline** | Vermelho      | Pulso rápido (4 Hz)     | RPM ≥ 9000                           |

### 🧠 Como Funciona a Detecção de Tendência

- Monitora histórico dos últimos 5 frames de RPM
- Calcula a taxa de mudança RPM/segundo
- Se aumenta > 500 RPM/sec → ativa efeito **Amarelo Pulsante**
- Perfeito para avisar quando você está acelerando forte

## 📋 Requisitos

- **Windows** com Assetto Corsa instalado
- **OpenRGB SDK Server** rodando
- Dispositivos RGB compatíveis conectados ao computador
- Python 3.8+

## 🔧 Instalação

### 1. Instalar OpenRGB

1. Download: [OpenRGB GitHub](https://github.com/CalcProgrammer1/OpenRGB)
2. Instalar a versão mais recente
3. Abrir OpenRGB e ir em `Settings → SDK Server`
4. Habilitar "SDK Server" e deixar rodando na porta 6742

### 2. Instalar dependências Python

```bash
# Na raiz do projeto ou em open_RGB/
pip install -r open_RGB/requirements.txt
```

### 3. Configuração (Segurança e Portabilidade)

O sistema agora prioriza o arquivo **`.env`** localizado na raiz do projeto. 

1. Localize o arquivo `.env.example` na raiz.
2. Crie uma cópia chamada `.env`.
3. Configure os parâmetros de host e porta do OpenRGB:
   ```env
   OPEN_RGB_HOST=localhost
   OPEN_RGB_PORT=6742
   ```

> [!TIP]
> O arquivo `rgb_config.json` ainda pode ser usado para configurações finas de cores e animações, mas os dados de conexão e dispositivos habilitados agora são lidos preferencialmente do `.env`.

### 4. Configurar dispositivos RGB

Execute o teste de cores para verificar quais dispositivos estão conectados:

```bash
python openrgb_controller.py
```

Isso vai:

- Descobrir todos os dispositivos RGB
- Testar com cores diferentes
- Mostrar informações de cada dispositivo

## 🚀 Uso

### Iniciar integração com Assetto Corsa

```bash
python ac_rgb_integration.py
```

A integração vai:

1. Conectar ao OpenRGB SDK Server
2. Aguardar Assetto Corsa iniciar
3. Ler telemetria em tempo real
4. Atualizar cores RGB baseado em RPM

### Configuração

Edite `rgb_config.json` para personalizar cores, thresholds e animações:

```json
{
  "openrgb_host": "localhost",
  "openrgb_port": 6742,
  "shift_light_thresholds": {
    "idle": 2000, // RPM para verde
    "warning": 6000, // RPM para amarelo
    "critical": 8000, // RPM para laranja
    "redline": 9000 // RPM para vermelho
  },
  "color_scheme": {
    "idle": [0, 255, 0],
    "warning": [255, 255, 0],
    "critical": [255, 128, 0],
    "redline": [255, 0, 0],
    "off": [0, 0, 0]
  },
  "enabled_devices": [],
  "animations": {
    "enabled": true, // Ativar/desativar animações
    "pulse_frequency": 2.0, // Freq. de pulso em Hz
    "pulse_min_brightness": 0.2, // Min. brilho (0.0-1.0)
    "rising_threshold": 500.0, // RPM/sec para detectar subida
    "rising_smoothing": 5, // Frames para suavizar trend
    "smooth_transition_frames": 10 // Frames para transição de cor
  }
}
```

#### 🎯 Seleção de Dispositivos

O campo `"enabled_devices"` controla quais dispositivos recebem o efeito:

- **`[]` (array vazio)**: Aplica efeito em **TODOS** os dispositivos RGB detectados (padrão recomendado)
- **`["Device Name 1", "Device Name 2"]`**: Aplica apenas nos dispositivos especificados

**Como descobrir o nome dos seus dispositivos?**

1. Execute: `python test_utilities.py`
2. Selecione opção `1` (Device Detection)
3. Os nomes aparecerão na lista de dispositivos

**Exemplo com filtro:**

```json
"enabled_devices": ["ASUS ROG", "Corsair H150i"]
```

#### 📊 Parâmetros de Animação

- **enabled**: Desabilita todos os efeitos de pulsação (cores apenas)
- **pulse_frequency**: Velocidade do pulso (Hz). Maior = mais rápido
- **pulse_min_brightness**: O quanto a cor fica escura no mínimo (0.1-0.3 é bom)
- **rising_threshold**: Taxa de mudança de RPM para detectar aceleração forte (RPM/segundo)
- **rising_smoothing**: Quantos frames usar para calcular tendência (mais = mais suave)

## 📊 Estrutura

```
open_RPG/
├── openrgb_controller.py           # Controlador OpenRGB (classe base)
├── led_animations.py               # Sistema de animações
├── dynamic_rpm_calculator.py       # Cálculo de thresholds dinâmicos ⭐ NEW!
├── bridge_sync.py                  # Sync com Argentum Bridge ⭐ NEW!
├── ac_rgb_integration.py           # Integração AC ↔ OpenRGB (principal)
├── test_utilities.py               # Testes interativos
├── rgb_config.json                 # Configuração (cores, thresholds, animações)
├── requirements.txt                # Dependências Python
└── README.md                       # Este arquivo
```

### 🆕 Novos Módulos (RPM Dinâmicos)

**`dynamic_rpm_calculator.py`**

- `RPMThresholdCalculator`: Lê maxRpm do AC shared memory
- `DynamicRPMConfig`: Combina dados do AC com config.json
- Calcula thresholds automaticamente como % do maxRpm

**`bridge_sync.py`**

- `ArgentumBridgeSyncClient`: Conecta ao Argentum Bridge via WebSocket
- `BridgeSyncManager`: Gerencia sincronização
- Permite sincronizar dados com o dashboard web

## 🔄 Fluxo de Dados - Versão com RPM Dinâmicos

```
┌─ AC (Assetto Corsa)                    ┌─ Argentum Bridge
│  └─ acpmf_static (maxRpm) ─┐          │  └─ WebSocket (/ws)
└────────────────────────────┼──────────┘
                             ↓
                 dynamic_rpm_calculator
                 ↓ (calcula % do maxRpm)
         DynamicRPMConfig
              ↓
    openrgb_controller
         (get_rpm_color)
             ↓
         OpenRGB SDK
             ↓
       Dispositivos RGB
```

## 🔄 Fluxo de Dados - Compatibilidade (Sem Bridge)

```
AC (Assetto Corsa)
    ↓
    Shared Memory (acpmf_physics)
    ↓
ac_rgb_integration.py (lê RPM)
    ↓
openrgb_controller.py (calcula cor)
    ↓
OpenRGB SDK Server
    ↓
Dispositivos RGB (mudam de cor)
```

## 🎮 Exemplos de Uso

### Testar cores específicas

```python
from openrgb_controller import OpenRGBShiftLights

controller = OpenRGBShiftLights()
controller.connect()
controller.set_color_all(255, 0, 0)  # Vermelho
controller.disconnect()
```

### Usar biblioteca OpenRGB em outro script

```python
from openrgb_controller import OpenRGBShiftLights

rgb = OpenRGBShiftLights()
rgb.connect()

# Simular RPM
for rpm in range(2000, 10000, 500):
    rgb.update_shift_lights(rpm)
    print(f"RPM: {rpm}")
    time.sleep(1)

rgb.disconnect()
```

## 🐛 Troubleshooting

### ImportError: "cannot import name 'Color' from 'openrgb.utils'"

**Solução**: A versão recente da biblioteca usa `RGBColor` em vez de `Color`.

- Atualize para a última versão: `pip install --upgrade openrgb-python`
- O código já está corrigido para usar `RGBColor`

### "Failed to connect to OpenRGB" erro de inicialização

**Solução**: O cliente OpenRGB usa `address` em vez de `host` como parâmetro.

- Verifique se OpenRGB SDK Server está rodando
- Padrão: `127.0.0.1:6742`

### ModuleNotFoundError: "No module named 'numpy'"

**Solução**: Instale as dependências Python:

```bash
cd open_RPG
python -m pip install -r requirements.txt
```

### "Failed to connect to OpenRGB"

- Verifique se OpenRGB está aberto e SDK Server está habilitado
- Tente conectar manualmente com teste:
  ```bash
  python -c "from openrgb_controller import OpenRGBShiftLights; OpenRGBShiftLights().connect()"
  ```

### "AC disconnected"

- Assetto Corsa não está rodando
- Ou a shared memory do AC está inacessível
- Certifique-se de que AC está em modo online/multiplayer

### Cores não aparecem

- Verifique modo de iluminação no OpenRGB
- Alguns dispositivos exigem configuração específica por tipo
- Teste manualmente com `test_utilities.py`:
  ```bash
  python test_utilities.py
  ```

### Melhorar performance

- Aumentar `update_interval` em `ac_rgb_integration.py` (padrão: 0.016s = 60 FPS)
- Reduzir em dispositivos com latência

## 📈 Roadmap

- [ ] GUI para configuração em tempo real
- [ ] Suporte para múltiplos perfis de cores
- [ ] Efeitos customizados (pulsante, raiante, etc)
- [ ] Integração com ESP32 (quando pronto)
- [ ] Suporte para outros simuladores (rFactor, iRacing, etc)
- [ ] Server remoto (RGB em outro PC)
- [ ] Logging e replay de sessões

## 📝 Notas Técnicas

### Assetto Corsa Shared Memory

- **acpmf_physics**: 1024 bytes, atualizado constantemente
  - RPM offset: 20 bytes (int32)
  - Speed offset: 28 bytes (float)
  - Gear offset: 16 bytes (int32)
  - E muito mais...

### OpenRGB SDK

- Protocolo de socket
- Porta 6742 (padrão)
- Suporta qualquer dispositivo RGB compatível
- Documentação: [OpenRGB GitHub](https://github.com/CalcProgrammer1/OpenRGB)

## 🤝 Contribuições

Sinta-se à vontade para:

- Melhorar configuração
- Adicionar novos efeitos
- Otimizar performance
- Adicionar suporte para novos simuladores

## 📄 Licença

Veja LICENSE no diretório raiz do projeto.
