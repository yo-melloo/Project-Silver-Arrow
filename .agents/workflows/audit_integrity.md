---
description: Auditoria completa de integridade (Documentação, Lógica e Ambiente).
---

# /audit_integrity - Procedimento de Auditoria Tática

Este workflow coordena os agentes @qa, @devops e @architect para uma revisão profunda da robustez e escalabilidade do projeto.

---

## 👥 Papéis e Responsabilidades

- **@architect:** Foca no desacoplamento de hardware e arquitetura de serviços.
- **@devops:** Foca em variáveis de ambiente, portabilidade e segredos.
- **@qa:** Foca em tratamento de erros, caminhos de exceção e integridade de dependências.

---

## 🔍 Pilares de Análise (Checklist)

### 1. Integridade de Documentação
- [ ] **Sincronia:** O README reflete a estrutura atual de pastas e dependências?
- [ ] **Setup Zero-Step:** O projeto sobe apenas com o `.env` e comandos documentados?
- [ ] **Exemplo (.env):** O `.env.example` está completo e didático?

### 2. Integridade de Lógica e Código
- [ ] **Desacoplamento:** A integração com hardware está isolada (sem dependências circulares)?
- [ ] **Resiliência:** O sistema falha graciosamente se uma variável de ambiente estiver incorreta?
- [ ] **Segurança:** Existem hardcoded strings (IPs, senhas) fora do `.env`?

### 3. Integridade de Ambiente
- [ ] **Dependências:** Existem versões conflitantes ou redundâncias?
- [ ] **Portabilidade:** Os scripts utilizam caminhos relativos em vez de absolutos?

---

## 📝 Protocolo de Saída (Relatório de Saúde)

Ao final da auditoria, os agentes devem gerar um `docs/audit_report.md` contendo:

1.  **Status de Integridade:** (✅ APROVADO | ⚠️ REQUER AJUSTES | 🚨 CRÍTICO).
2.  **Lista de Débitos Técnicos:** Inconsistências encontradas.
3.  **Sugestões de Refatoração:** Melhorias imediatas para robustez.

---
// turbo-all
*Execução sugerida antes de cada Major Release ou mudança de Fase.*
