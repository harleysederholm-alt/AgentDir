# AgentDir × Achii — Sovereign Engine Mobile (PWA)

Installable mobile PWA for the AgentDir × Achii demo. Theater-dark aesthetic,
local-first messaging, and the full brand asset set (favicons, apple-touch,
maskable icons, manifest).

## Stack

- Vite 5 + React 18 + TypeScript (strict)
- Tailwind CSS (shared design tokens w/ desktop & landing)
- Pure PWA: `/manifest.json` + `display: standalone` + masked icons

## Design tokens

| Role | Color |
| --- | --- |
| Base background | `#0F0F0F` |
| Panel (oxidised metal) | `#2C3E50` |
| Accent amber (Achii eyes) | `#F39C12` |
| Accent copper (CTA) | `#D35400` |

Fonts: Space Grotesk (display), Inter (body), JetBrains Mono (meta).

## Asset inventory

| Path | Role |
| --- | --- |
| `public/favicon.ico` | 16 / 32 / 48 multi-size ICO |
| `public/apple-touch-icon.png` | 180×180 iOS home-screen icon |
| `public/icons/icon-192.png` | PWA |
| `public/icons/icon-512.png` | PWA + maskable |
| `public/icons/icon-1024.png` | App-store source |
| `public/achii-mobile-bg.jpg` | Portrait Achii-in-panel background |
| `src/assets/wrench-bulb.png` | Master wrench-eye+bulb (1024²) |
| `src/assets/achii-mobile-bg.jpg` | Master background (4:7) |

All icons are generated from `src/assets/wrench-bulb.png` via ImageMagick.
Regenerate with:

```bash
convert src/assets/wrench-bulb.png -background "#0F0F0F" -gravity center \
  -resize 1024x1024 -extent 1024x1024 public/icons/icon-1024.png
convert public/icons/icon-1024.png -resize 512x512 public/icons/icon-512.png
convert public/icons/icon-1024.png -resize 192x192 public/icons/icon-192.png
convert public/icons/icon-1024.png -resize 180x180 public/apple-touch-icon.png
convert public/icons/icon-1024.png -resize 16x16 /tmp/16.png
convert public/icons/icon-1024.png -resize 32x32 /tmp/32.png
convert public/icons/icon-1024.png -resize 48x48 /tmp/48.png
convert /tmp/16.png /tmp/32.png /tmp/48.png public/favicon.ico
```

## Scripts

```bash
npm install
npm run dev        # vite dev server on :5174
npm run build      # tsc -b && vite build
npm run preview    # vite preview on :4174
npm run typecheck  # tsc --noEmit
```

## PWA install flow

1. `npm run build && npm run preview`
2. Open the preview URL on a mobile browser or Chrome desktop.
3. Browser offers **Install Achii** / **Add to Home Screen** — accepts the
   manifest, copper theme colour, masked icons, and portrait orientation.
4. Launched standalone, the URL bar disappears and Achii fills the viewport.

## Background scaling note

`.app-container` uses `background-size: cover; background-position: center bottom`
so Achii's face stays on screen and the component-panel edges reach the viewport
edge on every aspect ratio. No stretching — per Achii's explicit request.
