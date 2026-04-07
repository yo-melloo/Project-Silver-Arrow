# 🛡️ Modelagem de Ameaças - Project Silver Arrow

Uma análise crítica de segurança focada em telemetria, hardware e exposição de dados. Elaborado sob a perspectiva do **@pm** e **@redteam**.

## 🎯 Objetivos de Segurança
1.  **Privacidade do Piloto:** Garantir que credenciais de WiFi e tokens de API não vazem em repositórios públicos.
2.  **Integridade da Telemetria:** Evitar que dados falsos sejam injetados no dashboard ou shift-lights.
3.  **Disponibilidade local:** Garantir que o Bridge e o ESP32 operem sem interferência externa na rede local.

---

## 🔍 Análise de Vetores de Ataque

### 1. Hardcoding de Segredos (Risco: Crítico 🔴)
- **Cenário:** O desenvolvedor insere a senha do WiFi doméstico diretamente no código `.ino` e realiza o Git Push.
- **Mitigação:** Uso obrigatório de [[firmware_esp32/argentum_esp32_client/config.h.example|config.h]] e [[.env.example|.env]]. O arquivo `.gitignore` atua como a última linha de defesa.

### 2. Eavesdropping na Rede Local (Risco: Médio 🟡)
- **Cenário:** Um atacante na mesma rede local intercepta pacotes WebSocket (JSON em texto claro).
- **Impacto:** O atacante pode ler as estatísticas de telemetria em tempo real (marcha, RPM).
- **Observação:** Como o projeto é para uso local e doméstico (SimRacing), não utilizamos criptografia TLS (WSS) para minimizar latência no ESP32, mas o usuário deve estar ciente da natureza aberta do tráfego.

### 3. Abuso de CORS no Argentum Bridge (Risco: Baixo 🟢)
- **Cenário:** O script [[scripts_python/argentum_bridge.py|argentum_bridge.py]] possui `allow_origins=["*"]`.
- **Análise:** Necessário para permitir dashboards móveis (celulares/tablets) sem barreiras de porta/DNS. Em ambientes corporativos, isso seria uma vulnerabilidade de CSRF. No contexto local, é uma funcionalidade necessária para interoperabilidade.

---

## 🛡️ Recomendações de Blindagem
1.  **Network Isolation:** Recomenda-se rodar o ESP32 e o simulador em uma VLAN de IoT isolada se possível.
2.  **Audit Logs:** Implementar logging básico de IPs conectados no Bridge para detectar acessos não autorizados.
3.  **Pre-Commit Hooks:** Utilizar ferramentas como `git-secrets` para prevenir commits acidentais de chaves de API caso o projeto evolua para a Fase 4 (Nuvem).

---
*Assinado: @pm (Arquiteto de Segurança)*
