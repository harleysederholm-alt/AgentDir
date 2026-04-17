# VIEWPORT_SYNC — AgentDir × Achii surface audit

> Sementoi brändin värikoodit ja fontit arkkitehtuuriin. Jokainen
> surface (CLI · Desktop · Web · Mobile) sitoutuu samaan tokenpalettiin;
> poikkeama tässä taulukossa on regressio.

Viimeisin vahvistus: **v1.0.4-beta "The Rusty Awakening"** — kaikki
neljä surfacea ajettu vastaavan haaran HEAD-commitilla.

---

## Design tokens (canonical)

| Token             | Hex       | Rooli                                                     |
| ----------------- | --------- | --------------------------------------------------------- |
| `base_bg`         | `#0F0F0F` | Theatre-musta pääpohja (tausta kaikilla surfaceilla)      |
| `panel_blue`      | `#2C3E50` | Oksidoituneen metallipaneelin perussävy                    |
| `accent_amber`    | `#F39C12` | Achiin silmän hehku, aktiivitilat, `[LOG: …]` -leimat    |
| `accent_copper`   | `#D35400` | Kuparoituneet CTA-napit, ensisijaiset korostukset          |
| `accent_steel`    | `#607D8B` | Dull steel / blue-gray — metatiedot, polkuleimat          |
| `accent_success`  | `#1BC47D` / `#2ECC71` | `[STATUS: READY. ENGINE_ARMED]`, egress-rauhoittaja |

Pure black `#000000` on CLI:n terminaalitausta (ei base_bg siellä —
terminaali piirtää itse, ja ANSI-paletti olettaa puhtaan mustan).

## Tyypografia

| Perhe           | Käyttö                                       | Itse-hostattu |
| --------------- | --------------------------------------------- | :-----------: |
| Space Grotesk   | Otsikot (h1–h3), display, numeerinen data UI | Web ✓ · muut Google Fonts CDN¹ |
| Inter           | Leipäteksti, UI-liitännät                     | Web ✓ · muut Google Fonts CDN¹ |
| JetBrains Mono  | Tekninen data, CLI, koodilohkot, rautarekisterit | kaikki ✓ (fallback: `ui-monospace`) |

¹ Follow-up: peilata `next/font/local` -toteutus landing/mobile-surfaceille,
jotta "egress · 0 B" -mittari kertoo totuuden mobiilissa esillä ollessaan.

---

## Per-surface vahvistus

### CLI — `cli_theme.py` (PR #6, `devin/1776444770-cli-harness-rebrand`)

| Surface-token     | Arvo                        | Lähdelohko                                |
| ----------------- | --------------------------- | ------------------------------------------ |
| `COPPER`          | `\x1b[38;2;211;84;0m`        | `cli_theme.py` — "brand palette" lohko    |
| `AMBER`           | `\x1b[38;2;243;156;18m`     | `cli_theme.py`                             |
| `STEEL`           | `\x1b[38;2;96;125;139m`     | `cli_theme.py`                             |
| `PANEL`           | `\x1b[38;2;44;62;80m`       | `cli_theme.py`                             |
| Terminaalitausta | pure black (ei ANSI)        | oletettu — ei paletissa                   |
| Banner-fontti    | figlet slant (ei verkkohaku) | `cli_theme._BANNER_ART`                   |

### Desktop — Tauri + React/Vite (PR #1, `devin/1776424990-desktop-sovereign-engine`)

| Surface-token  | Arvo        | Lähde                             |
| -------------- | ----------- | --------------------------------- |
| `--bg-main`    | `#0F0F0F`   | `desktop/src/styles/globals.css`  |
| `--panel`      | `#2C3E50`   | `desktop/src/styles/globals.css`  |
| `--accent-amber` | `#F39C12` | `desktop/src/styles/globals.css`  |
| `--accent-copper` | `#D35400`| `desktop/src/styles/globals.css`  |
| Tyypografia    | Space Grotesk + Inter + JetBrains Mono | `desktop/index.html` |

### Landing (Vite) — PR #3, `devin/1776432558-mic-drop-landing`

Identtinen tokenisto kuin desktop + mobile; Tailwind-konfiguraatio
`landing/tailwind.config.js` käyttää samoja `base_bg / accent_amber /
accent_copper / panel_blue` -nimiä.

### Web (Next.js App Router) — PR #4, `devin/1776441434-cognitive-scaffolding`

`web/tailwind.config.ts`:

```ts
base_bg:       "#0F0F0F",
panel_blue:    "#2C3E50",
accent_amber:  "#F39C12",
accent_copper: "#D35400",
accent_success: "#1BC47D",   // landing-variantti success-vihreälle
```

Fontit `next/font/local`:lla self-hosted (`web/app/fonts.ts`) — ei
runtime-CDN-hakua.

### Mobile PWA — PR #5 + `devin/1776447083-origin-story-mobile`

`mobile/tailwind.config.js`:

```js
base_bg:       "#0F0F0F",
panel_blue:    "#2C3E50",
panel_deep:    "#1a2632",
panel_fill:    "#151b22",
accent_amber:  "#F39C12",
accent_copper: "#D35400",
accent_copper_warm: "#E67E22",
accent_success: "#2ECC71",
```

`globals.css` taustakuva `.app-container` — `background-size: cover`
(ei venytystä), sama token-kerros.

---

## Delta vs. canonical

Ainoa havaittu poikkeama:

- **`accent_success`** on `#1BC47D` (web/landing) vs. `#2ECC71`
  (mobile). Molemmat ovat sallituja onnistumis-toneja eikä kumpikaan
  ole canonical-palet­tissa. **Action:** valitse toinen v1.0.5-beetassa
  ja poista toinen. Ei blockeri MVP:lle.

Kaikki muut tokenit ovat 1:1 kaikilla neljällä surfacella.

---

## "Keep it local" egress-lupaus

| Surface | Fontit | Kuvat | Mallipainot |
| ------- | ------ | ----- | ----------- |
| CLI     | — (terminaalin oma) | — | ei mallinhaku CLI:stä käsin |
| Desktop | Google Fonts CDN (follow-up) | paikalliset | paikalliset / Tauri IPC |
| Landing | Google Fonts CDN (follow-up) | paikalliset | n/a |
| Web     | `next/font/local` self-hosted | paikalliset | n/a |
| Mobile  | Google Fonts CDN (follow-up) | paikalliset + inline SVG `WrenchEye` | MediaPipe / MLC LLM (client-side) |

Seuraava audit ajetaan ennen v1.0.5-beeta tag-painallusta.
