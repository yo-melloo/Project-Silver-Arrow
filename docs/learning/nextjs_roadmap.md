# 🗺️ Roadmap: Next.js para Dashboards (Silver Arrow)

Foco em criar interfaces de alto desempenho, reativas e com excelente experiência do usuário.

---

## 🏗️ Nível 1: Fundamentos Modernos
- [ ] **Next.js App Router**: `Layouts`, `Pages` e `Navigation`.
- [ ] **Componentes de Servidor vs Cliente**: Quando usar `"use client"`. No Silver Arrow, o dashboard de telemetria é 90% `"use client"`.
- [ ] **Hydration**: Entender por que o código roda no servidor e depois no cliente.

---

## 🚦 Nível 2: Estado e Reactividade
- [ ] **Hooks Essenciais**: `useState`, `useEffect`, `useCallback` e `useMemo`.
- [ ] **Gerenciamento de Estado**: `Zustand` (leve e rápido para alta taxa de atualização) ou `React Context`.
- [ ] **WebSockets nativos**: O que você já usou no projeto. Como gerenciar o ciclo de vida da conexão.

---

## 🎨 Nível 3: Data Visualization & UX
- [ ] **Tailwind CSS**: Estilização utilitária. Como o `Silver Arrow` é visualmente rico, você precisará dominar o sistema de design atômico.
- [ ] **Framer Motion**: Animações suaves para agulhas de RPM e transições de tela.
- [ ] **Charts**: `Recharts` ou `Chart.js` para históricos de telemetria (análise pós-volta).
- [ ] **Wake Lock API**: Aprofundamento no controle de periféricos do navegador.

---

## ⚡ Nível 4: Performance e Escala
- [ ] **Streaming & Suspense**: Carregamento progressivo de componentes.
- [ ] **Server Actions**: Como atualizar o banco de dados sem recarregar a página (Fase 5 do projeto).
- [ ] **Route Handlers**: Criação de APIs internas para o próprio dashboard.

---

### 📚 Recursos Recomendados
1. **Nextjs.org/Learn**: O curso oficial da Vercel é fenomenal.
2. **The Joy of React** (Josh Comeau): Ótimo para entender o React a fundo.
3. **TailwindCSS Docs**: A bíblia do design utility-first.

> [!TIP]
> Em telemetria de alta velocidade, menos renderizações é igual a mais performance. Use o `React DevTools` para monitorar se componentes estão renderizando sem necessidade!
