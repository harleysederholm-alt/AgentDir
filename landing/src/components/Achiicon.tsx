/**
 * Minimal oxidised-copper Achii badge — stylised front-view used as a
 * visual anchor on both the landing hero and the download page header.
 *
 * Pure SVG so it renders instantly on mobile cellular, no 3D runtime.
 */

interface Props {
  size?: number;
  glow?: boolean;
  className?: string;
}

export function Achiicon({ size = 180, glow = true, className }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 220 220"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Achii"
      className={className}
    >
      <defs>
        <radialGradient id="achii-body" cx="50%" cy="40%" r="65%">
          <stop offset="0%" stopColor="#3C556E" />
          <stop offset="55%" stopColor="#2C3E50" />
          <stop offset="100%" stopColor="#141D26" />
        </radialGradient>
        <radialGradient id="achii-eye" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stopColor="#FFF3D4" />
          <stop offset="40%" stopColor="#F39C12" />
          <stop offset="100%" stopColor="#7A4B06" />
        </radialGradient>
        <linearGradient id="achii-copper" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#D35400" />
          <stop offset="100%" stopColor="#7A2F00" />
        </linearGradient>
      </defs>

      {glow && (
        <circle cx="110" cy="110" r="100" fill="rgba(243,156,18,0.08)" />
      )}

      {/* Body shell */}
      <rect
        x="40"
        y="70"
        width="140"
        height="120"
        rx="28"
        fill="url(#achii-body)"
        stroke="rgba(0,0,0,0.5)"
        strokeWidth="1"
      />

      {/* Chest panel */}
      <rect
        x="72"
        y="118"
        width="76"
        height="42"
        rx="6"
        fill="#1A242E"
        stroke="rgba(243,156,18,0.25)"
      />
      <rect x="82" y="128" width="56" height="3" rx="1.5" fill="#D35400" opacity="0.75" />
      <rect x="82" y="136" width="34" height="3" rx="1.5" fill="#F39C12" opacity="0.55" />
      <rect x="82" y="144" width="46" height="3" rx="1.5" fill="#94A3B8" opacity="0.45" />

      {/* Head dome */}
      <rect
        x="60"
        y="32"
        width="100"
        height="58"
        rx="22"
        fill="url(#achii-body)"
        stroke="rgba(0,0,0,0.5)"
      />

      {/* Antenna */}
      <rect x="106" y="14" width="8" height="22" rx="2" fill="url(#achii-copper)" />
      <circle cx="110" cy="12" r="6" fill="#F39C12" />
      <circle cx="110" cy="12" r="10" fill="none" stroke="rgba(243,156,18,0.35)" strokeWidth="1" />

      {/* Eyes */}
      <circle cx="88" cy="58" r="10" fill="url(#achii-eye)" />
      <circle cx="132" cy="58" r="10" fill="url(#achii-eye)" />

      {/* Mouth slit */}
      <rect x="94" y="78" width="32" height="3" rx="1.5" fill="#0F0F0F" />

      {/* Arms */}
      <rect x="22" y="96" width="22" height="58" rx="8" fill="url(#achii-body)" />
      <rect x="176" y="96" width="22" height="58" rx="8" fill="url(#achii-body)" />

      {/* Wrench accent */}
      <rect
        x="176"
        y="146"
        width="6"
        height="28"
        rx="2"
        fill="url(#achii-copper)"
        transform="rotate(-20 179 160)"
      />
    </svg>
  );
}
