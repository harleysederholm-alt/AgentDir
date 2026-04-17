/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base_bg: "#0F0F0F",
        panel_blue: "#2C3E50",
        panel_deep: "#1a2632",
        panel_fill: "#151b22",
        panel_line: "rgba(255,255,255,0.06)",
        accent_amber: "#F39C12",
        accent_copper: "#D35400",
        accent_copper_warm: "#E67E22",
        accent_success: "#2ECC71",
        ink_soft: "#E6E6E6",
        ink_muted: "#A0A0A0",
        ink_dim: "#6b6b6b"
      },
      fontFamily: {
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"]
      },
      boxShadow: {
        copper: "0 18px 50px -18px rgba(211,84,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08)",
        amber: "0 0 40px -6px rgba(243,156,18,0.35)",
        panel: "0 24px 60px -24px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.04)"
      },
      keyframes: {
        amberPulse: {
          "0%, 100%": { opacity: "0.7", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.08)" }
        },
        caret: {
          "0%, 49%": { opacity: "1" },
          "50%, 100%": { opacity: "0" }
        }
      },
      animation: {
        "pulse-amber": "amberPulse 1.8s ease-in-out infinite",
        caret: "caret 1s steps(1) infinite"
      }
    }
  },
  plugins: []
};
