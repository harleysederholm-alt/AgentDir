# AgentDir × Achii — Landing Page

Vite + React + TS (strict) + Tailwind micro-site. Two routes:

- `/` → `AchiiLandingPage` — hero, Harness principles, flow, CTA rail.
- `/download` → `AchiiDownloadPage` — the destination behind the pitch-deck
  QR code. Portrait-first, mobile-optimised, TestFlight + APK buttons.

Shares the exact AgentDir × Achii design tokens with `/desktop` and
`/mobile` (`base_bg #0F0F0F`, `accent_amber #F39C12`, `panel_oxidized
#2C3E50`, `copper_reveal #D35400`; fonts Space Grotesk + JetBrains Mono).

## Commands

```bash
cd landing
npm install
npm run dev        # http://localhost:4173
npm run build      # tsc --noEmit && vite build → dist/
npm run preview
```
