import { defineConfig, splitVendorChunkPlugin } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { compression } from 'vite-plugin-compression2';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    splitVendorChunkPlugin(),
    visualizer({
      filename: 'stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
      template: 'treemap' // or 'sunburst', 'network'
    }),
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
  ],
  server: {
    // Serve service worker from public directory in development
    middlewareMode: false,
  },
  publicDir: 'public',
  build: {
    target: 'es2015',
    cssCodeSplit: true,
    sourcemap: mode === 'development',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: mode === 'production',
        drop_debugger: mode === 'production',
      },
    },
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // React core
          if (id.includes('node_modules/react/') || 
              id.includes('node_modules/react-dom/') ||
              id.includes('node_modules/react-router-dom/')) {
            return 'react-vendor';
          }
          
          // UI Libraries
          if (id.includes('node_modules/@radix-ui/')) {
            return 'ui-vendor';
          }
          
          // Chart libraries
          if (id.includes('node_modules/chart.js/') || 
              id.includes('node_modules/react-chartjs-2/') ||
              id.includes('node_modules/recharts/')) {
            return 'chart-vendor';
          }
          
          // Form libraries
          if (id.includes('node_modules/react-hook-form/') || 
              id.includes('node_modules/@hookform/') ||
              id.includes('node_modules/zod/')) {
            return 'form-vendor';
          }
          
          // Animation
          if (id.includes('node_modules/framer-motion/')) {
            return 'animation-vendor';
          }
          
          // Editor
          if (id.includes('node_modules/@tiptap/')) {
            return 'editor-vendor';
          }
          
          // PDF
          if (id.includes('node_modules/jspdf/')) {
            return 'pdf-vendor';
          }
          
          // Socket
          if (id.includes('node_modules/socket.io-client/')) {
            return 'socket-vendor';
          }
          
          // Date utilities
          if (id.includes('node_modules/date-fns/')) {
            return 'date-vendor';
          }
          
          // Icons
          if (id.includes('node_modules/lucide-react/') || 
              id.includes('node_modules/react-icons/')) {
            return 'icon-vendor';
          }
          
          // i18n
          if (id.includes('node_modules/i18next/') || 
              id.includes('node_modules/react-i18next/') ||
              id.includes('node_modules/i18next-browser-languagedetector/')) {
            return 'i18n-vendor';
          }
          
          // Utils
          if (id.includes('node_modules/axios/') || 
              id.includes('node_modules/clsx/') ||
              id.includes('node_modules/tailwind-merge/') ||
              id.includes('node_modules/class-variance-authority/')) {
            return 'utils-vendor';
          }
        },
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop().split('.')[0] : 'chunk';
          return `assets/${facadeModuleId}-[hash].js`;
        },
      },
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false,
      },
    },
    chunkSizeWarningLimit: 600,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@context': path.resolve(__dirname, './src/context'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@lib': path.resolve(__dirname, './src/lib'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@store': path.resolve(__dirname, './src/store'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
      },
    },
    hmr: {
      overlay: true,
    },
    watch: {
      usePolling: false,
    },
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query',
      'framer-motion',
    ],
    exclude: ['@vite/client', '@vite/env'],
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    transformMode: {
      web: [/\.[jt]sx?$/],
      ssr: [],
    },
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test',
        '**/*.d.ts',
        '**/*.test.{js,jsx}',
        '**/index.{js,jsx}',
      ],
      thresholds: {
        statements: 65,
        branches: 60,
        functions: 65,
        lines: 65
      }
    }
  },
}));