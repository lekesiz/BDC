// Minimal vite config for Docker production builds
const path = require('path');

module.exports = {
  build: {
    outDir: 'dist',
    minify: true,
    sourcemap: false,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@lib': path.resolve(__dirname, './src/lib'),
      '@assets': path.resolve(__dirname, './src/assets')
    }
  }
};