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
    allowedHosts: [
      'localhost',
      'kylinking.com',
      'www.kylinking.com'
    ],
    hmr: {
      host: 'localhost',
      port: 3000,
      protocol: 'ws'
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
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to backend:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from backend:', req.url, proxyRes.statusCode);
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
    'process.env': {
      NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'development'),
    },
    'import.meta.env.VITE_APP_TITLE': JSON.stringify(
      process.env.VITE_APP_TITLE || 'KylinKing云膜智能管理系统'
    ),
    'import.meta.env.VITE_APP_ENV': JSON.stringify(
      process.env.VITE_APP_ENV || 'development'
    ),
    'import.meta.env.VITE_API_URL': JSON.stringify('/api'),
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        // 分包策略
        manualChunks: {
          vendor: ['react', 'react-dom'],
          antd: ['antd'],
          router: ['react-router-dom'],
        },
      },
    },
  },
}) 