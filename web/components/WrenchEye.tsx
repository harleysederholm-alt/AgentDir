import type { SVGProps } from "react";

/**
 * Inline "wrench-eye" brand glyph.
 * Deterministic, no network hop, scales with font size.
 * Used in the sticky header so the PNG app icon is not loaded in-app.
 */
export function WrenchEye(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 48 48"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      {...props}
    >
      <defs>
        <radialGradient id="lens" cx="0.5" cy="0.45" r="0.55">
          <stop offset="0%" stopColor="#FFD98A" />
          <stop offset="55%" stopColor="#F39C12" />
          <stop offset="100%" stopColor="#A8620B" />
        </radialGradient>
        <linearGradient id="body" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#3B4D5E" />
          <stop offset="100%" stopColor="#1F2B36" />
        </linearGradient>
        <linearGradient id="copper" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#E67E22" />
          <stop offset="100%" stopColor="#8B3E06" />
        </linearGradient>
      </defs>
      <path
        d="M12 8 L20 14 L14 22 L10 18 Z M30 32 L38 38 L34 44 L28 40 Z"
        fill="url(#copper)"
        opacity="0.9"
      />
      <circle cx="24" cy="24" r="11" fill="url(#body)" stroke="#0F0F0F" strokeWidth="1.4" />
      <circle cx="24" cy="24" r="6.5" fill="url(#lens)" />
      <circle cx="21.5" cy="22" r="1.4" fill="#FFF8E6" opacity="0.85" />
    </svg>
  );
}
