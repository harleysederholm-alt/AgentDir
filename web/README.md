# AgentDir × Achii — Web (Next.js)

Cognitive scaffolding: the public-facing landing for the Sovereign Engine.

## Stack

- Next.js 14 (App Router)
- React 18, TypeScript (strict)
- Tailwind CSS 3 (tokens mirror the desktop & mobile clients verbatim)
- Framer Motion 11 (section reveals, hover states)
- Space Grotesk (display), Inter (body), JetBrains Mono (technical data) — all self-loaded via `next/font`

## Tokens

| Name | Hex |
|------|-----|
| `base_bg` | `#0F0F0F` |
| `accent_amber` | `#F39C12` |
| `accent_copper` | `#D35400` |
| `panel_blue` | `#2C3E50` |

## Structure

- `app/layout.tsx` — shell, fonts, metadata
- `app/page.tsx` — landing composition
- `app/download/page.tsx` — QR destination
- `components/` — Header, Hero, VideoShowcase, SoulOfAchii (with Terminal), HarnessSpec, KnowledgeHub, MicDrop, Footer, AchiiLogo

## Scripts

```bash
npm install
npm run dev       # http://localhost:3000
npm run build     # production build
npm run lint
npm run typecheck
```

## Assets

All images are checked in under `public/images/`:

- `achii-hero.png` — hero portrait (reveal shot)
- `achii-wrench.jpg` — Harness Engineering visual
- `achii-eyes.jpg` — Soul of Achii close-up
- `achii-stage.jpg` — Builder's Challenge stage
- `achii-workbench.jpg` — video placeholder

Swap the placeholder `<Image>` in `VideoShowcase.tsx` for the Veo 3.1 render when ready — keep the `mask-radial` wrapper identical.
