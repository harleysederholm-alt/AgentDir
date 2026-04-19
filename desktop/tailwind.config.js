/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brändikirja v4.6 (Opus) — kovakoodatut arvot
        'theater':    '#0F0F0F',   // Syvä pimeys, poistaa visuaalisen kohinan
        'copper':     '#D35400',   // Rusty Copper — sääntöpohjainen logiikka
        'amber':      '#F39C12',   // Glowing Amber — Achiin silmät, status, elo
        'steel':      '#607D8B',   // Dull Steel — polut, lokit, toissijainen info
        'dirty-white':'#E0E0E0',   // Luettavuus ilman kirkkautta
        'deep-black': '#080808',   // Syvempi musta paneelipohjille
      },
      fontFamily: {
        'display': ['"Space Grotesk"', 'sans-serif'],   // Isot otsikot
        'body':    ['"Inter"', 'sans-serif'],            // Leipäteksti
        'mono':    ['"JetBrains Mono"', 'monospace'],    // Status, koodi, lokit
      },
      animation: {
        'glow-pulse': 'glow-pulse 3s ease-in-out infinite',
        'tube-flicker': 'tube-flicker 4s ease-in-out infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '0.8' },
        },
        'tube-flicker': {
          '0%, 100%': { opacity: '0.85' },
          '20%': { opacity: '0.95' },
          '50%': { opacity: '0.75' },
          '80%': { opacity: '0.9' },
        },
      },
    },
  },
  plugins: [],
}
