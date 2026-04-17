/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Strict AgentDir × Achii design tokens — do not add "close-enough" variants.
        base_bg: "#0F0F0F", // Teatterimusta
        accent_amber: "#F39C12", // Achiin silmät / aktiiviset tilat
        panel_oxidized: "#2C3E50", // Nuhruinen metalli paneelit
        copper_reveal: "#D35400", // Call-to-action / Run-painike
        ink_soft: "#E5E7EB",
        ink_muted: "#94A3B8",
      },
      fontFamily: {
        heading: ['"Space Grotesk"', "system-ui", "sans-serif"],
        code: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: {
        copper: "0 0 18px rgba(211, 84, 0, 0.35)",
        amber: "0 0 22px rgba(243, 156, 18, 0.45)",
        panel: "0 10px 40px rgba(0, 0, 0, 0.6)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
