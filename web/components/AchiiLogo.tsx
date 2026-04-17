interface Props {
  className?: string;
  size?: number;
}

/**
 * Wrench-Eye wordmark glyph. Pure SVG — paints inline without a network hop,
 * because "0 B egress" is a hero stat and linking a Google-hosted mark would
 * contradict that. The eye is the amber lens; the wrench is the copper arm.
 */
export function AchiiLogo({ className, size = 36 }: Props) {
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label="AgentDir × Achii"
      className={className}
    >
      <defs>
        <radialGradient id="lensA" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#FFD98A" />
          <stop offset="45%" stopColor="#F39C12" />
          <stop offset="100%" stopColor="#7A3A00" />
        </radialGradient>
        <linearGradient id="bodyA" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#3B4F63" />
          <stop offset="100%" stopColor="#1F2A36" />
        </linearGradient>
        <linearGradient id="copperA" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#E97B2D" />
          <stop offset="100%" stopColor="#9C3B00" />
        </linearGradient>
      </defs>
      {/* Oxidised plate */}
      <circle cx="32" cy="32" r="26" fill="url(#bodyA)" stroke="#0F0F0F" strokeWidth="1.5" />
      {/* Wrench arm */}
      <path
        d="M 48 14 l 6 -6 a 6 6 0 0 1 6 6 l -8 8 l -4 -4 z"
        fill="url(#copperA)"
        stroke="#0F0F0F"
        strokeWidth="1"
      />
      <path
        d="M 44 18 L 32 30"
        stroke="url(#copperA)"
        strokeWidth="3"
        strokeLinecap="round"
      />
      {/* Amber lens */}
      <circle cx="32" cy="32" r="12" fill="url(#lensA)" />
      <circle cx="32" cy="32" r="12" fill="none" stroke="#0F0F0F" strokeWidth="1.25" />
      <circle cx="30" cy="30" r="2.5" fill="#FFF2CC" opacity="0.9" />
      {/* Bolts */}
      <circle cx="12" cy="32" r="1.6" fill="#0F0F0F" />
      <circle cx="32" cy="12" r="1.6" fill="#0F0F0F" />
      <circle cx="32" cy="52" r="1.6" fill="#0F0F0F" />
    </svg>
  );
}
