/** @type {import('next').NextConfig} */
const nextConfig = {
  // Permitir acesso de recursos de desenvolvimento (HMR) de outros dispositivos na rede
  // O Next.js bloqueia por padrão por segurança
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', '192.168.0.9:3000', '172.26.32.13:3000'],
    },
  },
  // Conforme sugerido pelo erro (Next.js 14+)
  allowedDevOrigins: ['192.168.0.9', '172.26.32.13', 'localhost'],
};

module.exports = nextConfig;
