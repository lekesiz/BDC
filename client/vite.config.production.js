import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'
import { compression } from 'vite-plugin-compression2'

export default defineConfig({
  plugins: [
    react({
      // Enable fast refresh for development
      fastRefresh: true,
      // Optimize for production
      babel: {
        plugins: [
          // Remove console.log in production
          ['transform-remove-console', { exclude: ['error', 'warn'] }]
        ]
      }
    }),
    // Gzip compression
    compression({
      algorithm: 'gzip',
      exclude: [/\.(br)$/, /\.(gz)$/]
    }),
    // Brotli compression
    compression({
      algorithm: 'brotliCompress',
      exclude: [/\.(gz)$/]
    }),
    // Bundle analyzer
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true
    })
  ],
  
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@pages': resolve(__dirname, './src/pages'),
      '@hooks': resolve(__dirname, './src/hooks'),
      '@utils': resolve(__dirname, './src/utils'),
      '@lib': resolve(__dirname, './src/lib'),
      '@assets': resolve(__dirname, './src/assets')
    }
  },

  build: {
    target: 'esnext',
    minify: 'terser',
    sourcemap: false,
    
    // Chunk size warnings
    chunkSizeWarningLimit: 600,
    
    // Advanced chunking strategy
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // React vendor chunk
          if (id.includes('node_modules/react/') || id.includes('node_modules/react-dom/')) {
            return 'react-vendor'
          }
          
          // Router chunk
          if (id.includes('node_modules/react-router') || id.includes('node_modules/@remix-run/router')) {
            return 'router-vendor'
          }
          
          // UI library chunk
          if (id.includes('node_modules/@radix-ui/') || id.includes('node_modules/lucide-react/')) {
            return 'ui-vendor'
          }
          
          // Charts chunk
          if (id.includes('node_modules/chart.js/') || id.includes('node_modules/react-chartjs-2/') || id.includes('node_modules/recharts/')) {
            return 'chart-vendor'
          }
          
          // Editor chunk
          if (id.includes('node_modules/@tiptap/') || id.includes('node_modules/katex/')) {
            return 'editor-vendor'
          }
          
          // Animation chunk
          if (id.includes('node_modules/framer-motion/')) {
            return 'animation-vendor'
          }
          
          // HTTP/API chunk
          if (id.includes('node_modules/axios/') || id.includes('node_modules/@tanstack/react-query/')) {
            return 'api-vendor'
          }
          
          // Utils chunk
          if (id.includes('node_modules/date-fns/') || id.includes('node_modules/clsx/') || id.includes('node_modules/class-variance-authority/')) {
            return 'utils-vendor'
          }
          
          // Other vendor chunk
          if (id.includes('node_modules/')) {
            return 'vendor'
          }
        },
        
        // File naming strategy
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const extType = info[info.length - 1]
          
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name)) {
            return `assets/images/[name]-[hash].${extType}`
          }
          
          if (/\.(css)$/i.test(assetInfo.name)) {
            return `assets/css/[name]-[hash].${extType}`
          }
          
          if (/\.(woff|woff2|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return `assets/fonts/[name]-[hash].${extType}`
          }
          
          return `assets/[name]-[hash].${extType}`
        }
      }
    },
    
    // Terser options for better minification
    terserOptions: {
      compress: {
        arguments: true,
        drop_console: ['log', 'debug', 'info'],
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.debug', 'console.info'],
        pure_getters: true,
        unsafe: true,
        unsafe_comps: true,
        unsafe_Function: true,
        unsafe_math: true,
        unsafe_symbols: true,
        unsafe_methods: true,
        unsafe_proto: true,
        unsafe_regexp: true,
        unsafe_undefined: true
      },
      mangle: {
        safari10: true
      }
    }
  },

  // Optimize deps
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      'axios',
      'jwt-decode'
    ]
  },

  // Performance hints
  performance: {
    hints: 'warning',
    maxEntrypointSize: 400000,
    maxAssetSize: 200000
  },

  // Environment variables prefix
  envPrefix: 'VITE_',

  // Server config for preview
  preview: {
    port: 4173,
    host: true,
    cors: true
  }
})