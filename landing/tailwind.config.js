/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base_bg: "#0F0F0F",
        accent_amber: "#F39C12",
        panel_oxidized: "#2C3E50",
        copper_reveal: "#D35400",
        ink_soft: "#E5E7EB",
        ink_muted: "#94A3B8",
        panel_fill: "#1A1A1A",
      },
      fontFamily: {
        heading: ["'Space Grotesk'", "system-ui", "sans-serif"],
        code: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      boxShadow: {
        copper: "0 0 20px rgba(211, 84, 0, 0.45)",
        amber: "0 0 25px rgba(243, 156, 18, 0.55)",
        panel: "0 18px 45px rgba(0, 0, 0, 0.55)",
      },
    },
  },
  plugins: [],
};
