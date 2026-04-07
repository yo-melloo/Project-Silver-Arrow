---
description: Procedimento para sincronizar documentação técnica com mudanças no código.
---

# /resync_docs - Fluxo de Sincronia de Documentação

Este workflow deve ser executado sempre que houver mudanças em APIs, offsets de memória, configurações de hardware ou segurança.

// turbo-all

1.  **Auditoria de Segredos:**
    - Verifique se `.env` e `config.h` estão no `.gitignore`.
    - Garanta que `.env.example` e `config.h.example` estão atualizados com novas variáveis.

2.  **Sincronia de READMEs:**
    - Atualize o `README.md` da raiz com as novas funcionalidades.
    - Sincronize os READMEs locais (`firmware_esp32/`, `open_RGB/`, `dashboard_web/`) se houver mudanças nos setups específicos.

3.  **Atualização de Specs:**
    - Se o formato JSON do Bridge mudou, atualize `docs/protocol_spec.md`.
    - Se novos offsets foram descobertos, atualize `docs/argentum_memory_mappings.md`.

4.  **Criação de Notas Atômicas:**
    - Documente novos conceitos técnicos em `Zettelkasten/` usando `[[Wikilinks]]`.

5.  **Verificação Final:**
    - Verifique se todos os links internos estão funcionais.
    - Gere um `walkthrough.md` resumindo as atualizações de documentação.

---
*Este workflow garante que o cérebro digital do projeto nunca fique obsoleto.*
