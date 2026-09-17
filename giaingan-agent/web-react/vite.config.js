import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server chay o cong 5500 de dong bo voi huong dan cu.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5500,
    open: true,
  },
});
