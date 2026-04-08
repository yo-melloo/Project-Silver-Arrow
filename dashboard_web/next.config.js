/** @type {import('next').NextConfig} */
const nextConfig = {
  // Permitir acesso de recursos de desenvolvimento (HMR) de outros dispositivos na rede
  // O Next.js bloqueia por padrão por segurança
  experimental: {
    serverActions: {
      allowedOrigins: [
        "localhost:3000",
        "192.168.0.9:3000",
        "172.26.32.13:3000",
        "192.168.32.3",
      ],
    },
  },
  // Conforme sugerido pelo erro (Next.js 14+)
  allowedDevOrigins: [
    "192.168.0.9",
    "192.168.32.3",
    "172.26.32.13",
    "localhost",
  ],
};

// NOTE: Toda vez que o usuário mudar de rede, deve consultar o IP e adicionar na lista, isso não é nada prático,
// então talvez seja necessário criar um campo de inserção para o IP na primeira interação ou quando o bridge não conectar.
// O ideal seria que o bridge tivesse um endereço fixo ou um nome de domínio, mas isso não é possível no momento.

module.exports = nextConfig;
