import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base_bg: "#0F0F0F",
        ink_soft: "#E8E5DE",
        ink_muted: "#8A8479",
        ink_dim: "#5A554C",
        panel_blue: "#2C3E50",
        panel_deep: "#1A2230",
        panel_fill: "#141414",
        panel_line: "rgba(232,229,222,0.08)",
        accent_amber: "#F39C12",
        accent_copper: "#D35400",
        accent_copper_warm: "#E67E22",
        accent_success: "#1BC47D",
        accent_error: "#E74C3C",
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "ui-sans-serif", "system-ui"],
        body: ["var(--font-inter)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-jetbrains-mono)", "ui-monospace", "SFMono-Regular"],
      },
      boxShadow: {
        copper:
          "0 16px 40px -12px rgba(211,84,0,0.55), inset 0 1px 0 rgba(255,255,255,0.12)",
        amber:
          "0 20px 60px -18px rgba(243,156,18,0.45), 0 0 0 1px rgba(243,156,18,0.22)",
        panel:
          "0 30px 80px -30px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.04)",
      },
      backgroundImage: {
        "grid-amber":
          "linear-gradient(to right, rgba(243,156,18,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(243,156,18,0.06) 1px, transparent 1px)",
        "radial-fade":
          "radial-gradient(60% 50% at 50% 40%, rgba(243,156,18,0.12), transparent 70%)",
      },
      keyframes: {
        "pulse-amber": {
          "0%,100%": { boxShadow: "0 0 0 0 rgba(243,156,18,0.55)" },
          "50%": { boxShadow: "0 0 0 14px rgba(243,156,18,0)" },
        },
        caret: { "0%,49%": { opacity: "1" }, "50%,100%": { opacity: "0" } },
        "amber-flicker": {
          "0%,100%": { opacity: "1" },
          "45%": { opacity: "0.92" },
          "55%": { opacity: "0.88" },
          "60%": { opacity: "1" },
        },
      },
      animation: {
        "pulse-amber": "pulse-amber 2.2s ease-in-out infinite",
        caret: "caret 1s steps(1,end) infinite",
        "amber-flicker": "amber-flicker 5.5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
