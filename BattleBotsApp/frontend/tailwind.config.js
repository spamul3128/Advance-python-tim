/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // BattleBots-inspired palette — dark arena floor + neon sparks
        ink: {
          950: "#070a13",
          900: "#0c111d",
          800: "#131a2b",
          700: "#1b2336",
        },
        spark: {
          500: "#ff5722", // orange spark
          400: "#ff8a4c",
          300: "#ffb380",
        },
        signal: {
          500: "#22d3ee", // cyan data flow
          400: "#67e8f9",
        },
        winner: "#22c55e",
        loser: "#ef4444",
      },
      fontFamily: {
        display: ['"Bebas Neue"', "Impact", "system-ui", "sans-serif"],
        sans: ['"Inter"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 24px -2px rgba(34, 211, 238, 0.45)",
        spark: "0 0 24px -2px rgba(255, 87, 34, 0.55)",
      },
      animation: {
        "pulse-slow": "pulse 3s ease-in-out infinite",
        flow: "flow 1.6s linear infinite",
      },
      keyframes: {
        flow: {
          "0%": { strokeDashoffset: "48" },
          "100%": { strokeDashoffset: "0" },
        },
      },
    },
  },
  plugins: [],
};
