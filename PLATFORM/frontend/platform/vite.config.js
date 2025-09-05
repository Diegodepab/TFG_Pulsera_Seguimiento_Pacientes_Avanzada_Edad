import { svelteTesting } from '@testing-library/svelte/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  build: {
    assetsInlineLimit: 0
  },
  server: {
    fs: {
      allow: ['static']
    },
      hmr: false,
    watch: {
      usePolling: true
    },
    proxy: {
        '/v1': {
      // Apuntamos al host de Docker en el puerto que mapea tu API
      target: 'http://host.docker.internal:8001',
      changeOrigin: true,
      secure: false,
      ws: true   
    }
  }
},
  test: {
    workspace: [
      {
        extends: './vite.config.js',
        plugins: [svelteTesting()],
        test: {
          name: 'client',
          environment: 'jsdom',
          clearMocks: true,
          include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
          exclude: ['src/lib/server/**'],
          setupFiles: ['./vitest-setup-client.js']
        }
      },
      {
        extends: './vite.config.js',
        test: {
          name: 'server',
          environment: 'node',
          include: ['src/**/*.{test,spec}.{js,ts}'],
          exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
        }
      }
    ]
  }
});
