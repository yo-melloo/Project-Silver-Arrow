# 🛡️ Diretrizes de Segurança (@pm)

A segurança do **Project Silver Arrow** é baseada em isolamento de credenciais e proteção de hardware.

## 🔑 Gestão de Segredos

- **Zero Hardcoding:** É TERMINANTEMENTE PROIBIDO inserir SSIDs, Senhas ou IPs no código fonte commitado.
- **Estrutura .env:** Utilize sempre o `.env.example` como template. O arquivo `.env` real deve estar no `.gitignore`.
- **Firmware config.h:** Para ESP32, utilize o sistema `config.h` (externo ao `.ino`).

## 📡 Comunicação
- O tráfego de telemetria é local (LAN). Evite expor as portas do Bridge (`8001`) para a internet sem um túnel seguro ou VPN.

---
*Assinado: @pm (Arquiteto de Segurança)*
