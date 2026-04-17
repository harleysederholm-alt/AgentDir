import Link from "next/link";
import { AchiiLogo } from "./AchiiLogo";

const COLUMNS = [
  {
    heading: "Tuote",
    links: [
      { href: "#lataa", label: "Lataa työpöytä" },
      { href: "/download", label: "Mobiilibetat" },
      { href: "#demo", label: "Demo-video" },
      { href: "#lataa", label: "Release notes" },
    ],
  },
  {
    heading: "Tapahtumat",
    links: [
      { href: "#areena", label: "Builder's Challenge 13.5." },
      { href: "#areena", label: "Turku Arena · agenda" },
      { href: "#areena", label: "Pyydä kutsu" },
      { href: "mailto:achii@agentdir.dev", label: "Suora sähköposti" },
    ],
  },
  {
    heading: "Teknologia",
    links: [
      { href: "#spec", label: "Harness Engineering" },
      { href: "#spec", label: "Gatekeeper-protokolla" },
      { href: "#tieto", label: "Security Whitepaper" },
      {
        href: "https://github.com/harleysederholm-alt/AgentDir",
        label: "GitHub · AgentDir"
      },
    ],
  },
  {
    heading: "Filosofia",
    links: [
      { href: "#filosofia", label: "Mitä tämä on?" },
      { href: "#sielu", label: "Achiin sielu" },
      { href: "#tieto", label: "Kontekstin hallinta" },
      { href: "#tieto", label: "NPU vs GPU" },
    ],
  },
];

export function Footer() {
  return (
    <footer
      id="footer"
      className="section-pad relative border-t border-panel_line py-20"
    >
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-12 lg:grid-cols-[1.1fr_2.2fr]">
          <div>
            <Link href="/" className="flex items-center gap-3">
              <AchiiLogo size={40} />
              <div className="leading-none">
                <div className="font-display text-base font-semibold tracking-[0.2em] text-ink_soft">
                  AGENTDIR × ACHII
                </div>
                <div className="mt-1 font-mono text-[11px] uppercase tracking-[0.28em] text-ink_muted">
                  sovereign engine · harness 1.0
                </div>
              </div>
            </Link>
            <p className="mt-6 max-w-sm font-body text-sm leading-relaxed text-ink_soft/60">
              Rakennettu Turussa, ajettu paikallisesti. AgentDir × Achii on
              avointa valjasarkkitehtuuria kaikille, jotka haluavat lopettaa
              tekoälyn yappauksen ja aloittaa rakentamisen.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-10 md:grid-cols-4">
            {COLUMNS.map((col) => (
              <div key={col.heading}>
                <div className="eyebrow mb-4">{col.heading}</div>
                <ul className="space-y-3">
                  {col.links.map((l) => (
                    <li key={l.label}>
                      <a
                        href={l.href}
                        className="font-body text-sm text-ink_soft/75 transition hover:text-accent_amber"
                      >
                        {l.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-14 flex flex-col items-start justify-between gap-4 border-t border-panel_line pt-8 font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted md:flex-row md:items-center">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
            <span>v1.0.4-beta &ldquo;The Rusty Awakening&rdquo;</span>
            <span>© 2026 AgentDir × Achii</span>
            <span>MIT · AGPL (Harness Core)</span>
          </div>
          <div className="flex items-center gap-5">
            <a href="#filosofia" className="transition hover:text-accent_amber">
              Privacy · Local-first
            </a>
            <a href="#spec" className="transition hover:text-accent_amber">
              Terms of Sovereignty
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
