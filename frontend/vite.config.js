import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      'unvoted-histological-marleen.ngrok-free.dev', // Add ngrok URL here
      'localhost', // Optional: if you want localhost as well
    ],
  },
});
