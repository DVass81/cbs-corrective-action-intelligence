/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian: "#05070a",
        carbon: "#0c1016",
        graphite: "#171d26",
        steel: "#8a95a6",
        electric: "#28a8ff",
        cyanline: "#72ddff",
      },
      boxShadow: {
        glow: "0 0 42px rgba(40,168,255,.22)",
        panel: "0 18px 70px rgba(0,0,0,.32)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
