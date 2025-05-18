import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: true,
    cors: true,
    hmr: {
      host: '0.0.0.0',
      port: 3000,
      clientPort: 3000,
    },
    fs: {
      // 允许任何主机访问
      strict: false,
      allow: ['/']
    },
    watch: {
      usePolling: true,
    },
    proxy: {
      // 在开发环境中，直接代理到后端容器
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from:', req.url, proxyRes.statusCode);
          });
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        // Removing additionalData to prevent conflicts with @use directives
      }
    }
  },
  // 允许在前端开发中模拟后端接口
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('/api'),
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development')
  }
}) 