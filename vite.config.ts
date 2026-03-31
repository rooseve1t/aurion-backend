import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import legacy from '@vitejs/plugin-legacy'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    legacy({
      targets: ['defaults', 'iOS >= 12', 'Safari >= 12'],
      modernPolyfills: true,
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'Aurion OS',
        short_name: 'Aurion',
        description: 'Персональный ИИ-ассистент нового поколения',
        theme_color: '#0a0a0f',
        background_color: '#0a0a0f',
        display: 'standalone',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\./,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-cache', expiration: { maxEntries: 50 } }
          },
          {
            urlPattern: /\/api\/v2\/feed/,
            handler: 'StaleWhileRevalidate',
            options: { cacheName: 'feed-cache', expiration: { maxEntries: 100, maxAgeSeconds: 86400 } }
          }
        ]
      }
    })
  ],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
  server: {
    proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts']
  }
})
