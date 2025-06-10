import { defineConfig, splitVendorChunkPlugin } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { compression } from 'vite-plugin-compression2';
import { createHash } from 'crypto';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production';
  
  return {
    plugins: [
      react(),
      splitVendorChunkPlugin(),
      
      // Enhanced PWA Configuration
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
          cleanupOutdatedCaches: true,
          skipWaiting: true,
          clientsClaim: true,
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
                },
                cacheKeyWillBeUsed: async ({ request }) => {
                  return `${request.url}?version=1`;
                }
              }
            },
            {
              urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'gstatic-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
                }
              }
            },
            {
              urlPattern: /\/api\/.*\/*$/,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 * 24 // 1 day
                },
                networkTimeoutSeconds: 10,
                cacheKeyWillBeUsed: async ({ request }) => {
                  // Add auth token to cache key for user-specific data
                  const authToken = request.headers.get('Authorization');
                  const hash = createHash('md5').update(authToken || '').digest('hex').slice(0, 8);
                  return `${request.url}?auth=${hash}`;
                }
              }
            },
            {
              urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|ico)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'images-cache',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
                }
              }
            },
            {
              urlPattern: /\.(?:js|css)$/,
              handler: 'StaleWhileRevalidate',
              options: {
                cacheName: 'static-resources',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 * 24 * 7 // 7 days
                }
              }
            }
          ],
          maximumFileSizeToCacheInBytes: 3000000, // 3MB
          exclude: [/\.map$/, /manifest$/, /\.htaccess$/],
          // Custom service worker with enhanced features
          swSrc: 'public/sw-enhanced.js',
          swDest: 'sw.js'
        },
        includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
        manifest: {
          name: 'BDC - Beneficiary Development Center',
          short_name: 'BDC',
          description: 'Comprehensive beneficiary management and development platform',
          theme_color: '#3b82f6',
          background_color: '#ffffff',
          display: 'standalone',
          orientation: 'portrait',
          scope: '/',
          start_url: '/',
          icons: [
            {
              src: 'icons/pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'icons/pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            },
            {
              src: 'icons/pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable'
            }
          ],
          categories: ['business', 'productivity', 'utilities'],
          lang: 'en',
          dir: 'ltr',
          prefer_related_applications: false,
          screenshots: [
            {
              src: 'screenshots/desktop-home.png',
              sizes: '1280x720',
              type: 'image/png',
              form_factor: 'wide',
              label: 'Home screen on desktop'
            },
            {
              src: 'screenshots/mobile-dashboard.png',
              sizes: '750x1334',
              type: 'image/png',
              form_factor: 'narrow',
              label: 'Dashboard on mobile'
            }
          ],
          shortcuts: [
            {
              name: 'Dashboard',
              short_name: 'Dashboard',
              description: 'View main dashboard',
              url: '/dashboard',
              icons: [{ src: 'icons/shortcut-dashboard.png', sizes: '96x96' }]
            },
            {
              name: 'Beneficiaries',
              short_name: 'Beneficiaries',
              description: 'Manage beneficiaries',
              url: '/beneficiaries',
              icons: [{ src: 'icons/shortcut-beneficiaries.png', sizes: '96x96' }]
            },
            {
              name: 'Evaluations',
              short_name: 'Evaluations',
              description: 'View evaluations',
              url: '/evaluations',
              icons: [{ src: 'icons/shortcut-evaluations.png', sizes: '96x96' }]
            }
          ],
          edge_side_panel: {
            preferred_width: 400
          },
          display_override: ['window-controls-overlay', 'standalone', 'minimal-ui']
        },
        devOptions: {
          enabled: mode === 'development',
          type: 'module',
          navigateFallback: 'index.html'
        }
      }),
      
      visualizer({
        filename: 'stats.html',
        open: false,
        gzipSize: true,
        brotliSize: true,
        template: 'treemap'
      }),
      
      // Only enable compression in production
      ...(isProduction ? [
        compression({
          algorithm: 'gzip',
          ext: '.gz',
        }),
        compression({
          algorithm: 'brotliCompress',
          ext: '.br',
        })
      ] : [])
    ],
  server: {
    // Serve service worker from public directory in development
    middlewareMode: false,
  },
  publicDir: 'public',
  build: {
    target: ['es2015', 'safari11'],
    cssCodeSplit: true,
    sourcemap: mode === 'development',
    minify: isProduction ? 'terser' : false,
    terserOptions: {
      compress: {
        drop_console: isProduction,
        drop_debugger: isProduction,
        passes: 2,
        pure_getters: true,
        unsafe_comps: true,
        unsafe_math: true
      },
      mangle: {
        safari10: true
      },
      format: {
        safari10: true
      }
    },
    reportCompressedSize: isProduction,
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // PWA and service worker related
          if (id.includes('node_modules/workbox') || 
              id.includes('node_modules/vite-plugin-pwa')) {
            return 'pwa-vendor';
          }
          
          // React core (keep small for initial load)
          if (id.includes('node_modules/react/') || 
              id.includes('node_modules/react-dom/')) {
            return 'react-core';
          }
          
          // React ecosystem
          if (id.includes('node_modules/react-router-dom/') ||
              id.includes('node_modules/@tanstack/react-query')) {
            return 'react-ecosystem';
          }
          
          // UI Libraries (critical for layout)
          if (id.includes('node_modules/@radix-ui/')) {
            return 'ui-vendor';
          }
          
          // Chart libraries (heavy, lazy load)
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
          
          // Animation (can be lazy loaded)
          if (id.includes('node_modules/framer-motion/')) {
            return 'animation-vendor';
          }
          
          // Editor (heavy, lazy load)
          if (id.includes('node_modules/@tiptap/')) {
            return 'editor-vendor';
          }
          
          // PDF (lazy load)
          if (id.includes('node_modules/jspdf/')) {
            return 'pdf-vendor';
          }
          
          // Socket (lazy load)
          if (id.includes('node_modules/socket.io-client/')) {
            return 'socket-vendor';
          }
          
          // Date utilities
          if (id.includes('node_modules/date-fns/')) {
            return 'date-vendor';
          }
          
          // Icons (frequently used)
          if (id.includes('node_modules/lucide-react/') || 
              id.includes('node_modules/react-icons/')) {
            return 'icon-vendor';
          }
          
          // i18n (critical for initial load)
          if (id.includes('node_modules/i18next/') || 
              id.includes('node_modules/react-i18next/') ||
              id.includes('node_modules/i18next-browser-languagedetector/')) {
            return 'i18n-vendor';
          }
          
          // Utilities (frequently used)
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
    chunkSizeWarningLimit: 800,
    assetsInlineLimit: 4096, // 4kb
    cssCodeSplit: true,
    rollupOptions: {
      external: [],
      // Optimize for PWA caching
      output: {
        manualChunks: (id) => {
          // PWA and service worker related
          if (id.includes('node_modules/workbox') || 
              id.includes('node_modules/vite-plugin-pwa')) {
            return 'pwa-vendor';
          }
          
          // React core (keep small for initial load)
          if (id.includes('node_modules/react/') || 
              id.includes('node_modules/react-dom/')) {
            return 'react-core';
          }
          
          // React ecosystem
          if (id.includes('node_modules/react-router-dom/') ||
              id.includes('node_modules/@tanstack/react-query')) {
            return 'react-ecosystem';
          }
          
          // UI Libraries (critical for layout)
          if (id.includes('node_modules/@radix-ui/')) {
            return 'ui-vendor';
          }
          
          // Chart libraries (heavy, lazy load)
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
          
          // Animation (can be lazy loaded)
          if (id.includes('node_modules/framer-motion/')) {
            return 'animation-vendor';
          }
          
          // Editor (heavy, lazy load)
          if (id.includes('node_modules/@tiptap/')) {
            return 'editor-vendor';
          }
          
          // PDF (lazy load)
          if (id.includes('node_modules/jspdf/')) {
            return 'pdf-vendor';
          }
          
          // Socket (lazy load)
          if (id.includes('node_modules/socket.io-client/')) {
            return 'socket-vendor';
          }
          
          // Date utilities
          if (id.includes('node_modules/date-fns/')) {
            return 'date-vendor';
          }
          
          // Icons (frequently used)
          if (id.includes('node_modules/lucide-react/') || 
              id.includes('node_modules/react-icons/')) {
            return 'icon-vendor';
          }
          
          // i18n (critical for initial load)
          if (id.includes('node_modules/i18next/') || 
              id.includes('node_modules/react-i18next/') ||
              id.includes('node_modules/i18next-browser-languagedetector/')) {
            return 'i18n-vendor';
          }
          
          // Utilities (frequently used)
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
        // Consistent file names for better caching
        entryFileNames: (chunkInfo) => {
          return isProduction 
            ? `assets/[name]-[hash].js`
            : `assets/[name].js`;
        },
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `assets/images/[name]-[hash][extname]`;
          }
          if (/woff2?|eot|ttf|otf/i.test(ext)) {
            return `assets/fonts/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        }
      },
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false,
      },
    },
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
  // Enhanced optimization for PWA
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query',
      'framer-motion',
      'axios',
      'i18next',
      'react-i18next',
      'clsx',
      'tailwind-merge'
    ],
    exclude: ['@vite/client', '@vite/env', 'workbox-*'],
    force: mode === 'development'
  },
  
  // PWA-specific environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __SW_ENABLED__: JSON.stringify(isProduction || process.env.VITE_SW_DEV === 'true')
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    transformMode: {
      web: [/\.[jt]sx?$/],
      ssr: [],
    },
    env: {
      VITE_ROUTER_FUTURE_V7_START_TRANSITION: 'true',
      VITE_ROUTER_FUTURE_V7_RELATIVE_SPLAT_PATH: 'true',
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
  };
});