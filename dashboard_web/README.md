# 🌐 Argentum Silver Arrow - Dashboard Web (Next.js)

Interface de visualização em tempo real para telemetria de alta fidelidade. O dashboard conecta-se ao [[scripts_python/argentum_bridge.py|Argentum Bridge]] via WebSockets para exibir dados processados do simulador.

## 🚀 Como Iniciar (Desenvolvimento)

1. **Instalação de Dependências:**
   ```bash
   cd dashboard_web
   npm install
   ```

2. **Configuração de Ambiente:**
   O dashboard utiliza o arquivo **`.env`** localizado na raiz do projeto para saber onde encontrar o Bridge.
   
   Certifique-se de que a variável abaixo está correta no seu `.env`:
   ```env
   NEXT_PUBLIC_BRIDGE_URL=ws://localhost:8001/ws
   ```

3. **Execução:**
   ```bash
   npm run dev
   ```
   Acesse: [http://localhost:3000](http://localhost:3000)

## 🏛️ Fluxo de Conexão

- O Dashboard age como um cliente **Web** no Bridge.
- Recebe o objeto JSON completo (com pedais, G-Force e tempos de volta).
- Taxa de atualização: ~60 FPS (sincronizado com o Bridge).

## 🛠️ Tecnologias
- **Framework:** Next.js (React)
- **Styling:** Tailwind CSS / Vanilla CSS
- **Comunicação:** WebSockets nativo
- **Ícones:** Lucide React

---
Desenvolvido como parte da **Fase 3** do Project Silver Arrow. Veja a [[README.md|Estrutura Geral]] para mais detalhes.
