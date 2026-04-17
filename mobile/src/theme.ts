/**
 * Strict AgentDir × Achii design tokens — kept identical to the desktop
 * shell (`desktop/tailwind.config.js`). Any drift between the two surfaces
 * is a bug: Achii is the same character on every device.
 */
export const tokens = {
  colors: {
    base_bg: "#0F0F0F", // teatterimusta
    accent_amber: "#F39C12", // Achiin silmät / aktiiviset tilat
    panel_oxidized: "#2C3E50", // nuhruinen metalli paneelit
    copper_reveal: "#D35400", // call-to-action / Run painike
    ink_soft: "#E5E7EB",
    ink_muted: "#94A3B8",
    panel_fill: "#1A1A1A",
    success: "#4ADE80",
    error: "#EF4444",
  },
  fonts: {
    heading: "SpaceGrotesk_600SemiBold",
    headingRegular: "SpaceGrotesk_400Regular",
    code: "JetBrainsMono_500Medium",
  },
  radius: {
    sm: 6,
    md: 10,
    lg: 14,
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
} as const;

export type Tokens = typeof tokens;
