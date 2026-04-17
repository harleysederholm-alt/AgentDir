import { ArrowRight, Cpu, Link2Off, ShieldCheck, Terminal, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { Achiicon } from "../components/Achiicon";

const FEATURES = [
  {
    icon: Cpu,
    title: "Edge-first inference",
    body: "Gemma 2B pyörii lokaalisti NPU:lla. Pilvi on valinta, ei vaatimus.",
  },
  {
    icon: ShieldCheck,
    title: "Harness Engineering",
    body: ".yaml = logiikka, .md = konteksti. Sanitoitu egress. Ei yappausta.",
  },
  {
    icon: Link2Off,
    title: "Ei lukitusta",
    body: "AgentDir-rakenne kuuluu sinulle. Achii on vain renki, ei portinvartija.",
  },
];

const FLOW = [
  {
    step: "01",
    title: "Kloonaa Valjaat",
    body: "Achii materialisoi .achii/templates + docs -rakenteen työkansioon.",
  },
  {
    step: "02",
    title: "Kirjoita kontekstia (.md)",
    body: "Kerro Achiille mitä yrität saada aikaan. Ei PRD-pohjia, ei turhaa.",
  },
  {
    step: "03",
    title: "Aja Valjas",
    body: "Lokaali malli tekee 90 %. Jäljellä oleva 10 % reititetään Opukseen vain tarvittaessa.",
  },
];

export function AchiiLandingPage() {
  return (
    <div className="min-h-screen">
      {/* NAV */}
      <header className="sticky top-0 z-50 border-b border-panel_oxidized/40 bg-base_bg/85 backdrop-blur-md">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
          <Link to="/" className="flex items-center gap-2">
            <span className="block h-2 w-2 rounded-full bg-accent_amber shadow-amber" />
            <span className="font-heading text-sm font-bold uppercase tracking-[0.3em] text-accent_amber">
              AgentDir
            </span>
            <span className="font-code text-[11px] uppercase tracking-[0.3em] text-ink_muted">
              × Achii
            </span>
          </Link>
          <div className="hidden items-center gap-6 sm:flex">
            <a
              href="#harness"
              className="font-code text-xs uppercase tracking-[0.2em] text-ink_muted transition-colors hover:text-ink_soft"
            >
              Harness
            </a>
            <a
              href="#flow"
              className="font-code text-xs uppercase tracking-[0.2em] text-ink_muted transition-colors hover:text-ink_soft"
            >
              Virta
            </a>
            <Link
              to="/download"
              className="font-code text-xs uppercase tracking-[0.2em] text-accent_amber hover:text-copper_reveal"
            >
              Lataa
            </Link>
          </div>
        </nav>
      </header>

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-12 px-5 py-16 sm:py-24 lg:grid-cols-[1.1fr_1fr]">
          <div className="space-y-6">
            <span className="eyebrow">
              <Terminal size={14} /> Builder's Challenge 2026
            </span>
            <h1 className="font-heading text-4xl font-bold leading-[1.05] text-ink_soft sm:text-6xl">
              Lopeta yappaus.
              <br />
              <span className="text-accent_amber">Aja Valjaat.</span>
            </h1>
            <p className="max-w-xl text-base text-ink_muted sm:text-lg">
              AgentDir × Achii on <span className="text-ink_soft">Sovereign Engine</span> — lokaali
              tekoälymaskotti, joka ei hallusinoi, ei vuoda salaisuuksia eikä lähetä yhtään
              tavua pilveen ilman sinun Valjaiden lupaa.
            </p>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link to="/download" className="copper-cta">
                <Zap size={16} /> Lataa demo
                <ArrowRight size={16} />
              </Link>
              <a
                href="https://github.com/harleysederholm-alt/AgentDir"
                className="secondary-cta"
              >
                Katso lähdekoodi
              </a>
            </div>
            <dl className="grid grid-cols-3 gap-4 pt-6 font-code text-xs text-ink_muted">
              <div>
                <dt className="tracking-[0.22em]">NPU</dt>
                <dd className="mt-1 text-lg text-ink_soft">2.5 s</dd>
              </div>
              <div>
                <dt className="tracking-[0.22em]">Egress</dt>
                <dd className="mt-1 text-lg text-ink_soft">0 B</dd>
              </div>
              <div>
                <dt className="tracking-[0.22em]">Hallusinaatiot</dt>
                <dd className="mt-1 text-lg text-ink_soft">—</dd>
              </div>
            </dl>
          </div>

          <div className="relative flex items-center justify-center">
            <div className="absolute inset-x-8 bottom-4 h-32 rounded-full bg-accent_amber/20 blur-3xl" />
            <div className="panel relative flex h-80 w-80 items-center justify-center">
              <Achiicon size={220} />
            </div>
          </div>
        </div>
      </section>

      {/* HARNESS FEATURES */}
      <section id="harness" className="border-y border-panel_oxidized/40 bg-base_bg/60">
        <div className="mx-auto max-w-6xl px-5 py-16">
          <h2 className="font-heading text-2xl font-semibold text-ink_soft sm:text-3xl">
            Harness-periaatteet
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-ink_muted">
            Kolme sääntöä, joista Achii ei anna periksi. Kaikki muu on implementaatiota.
          </p>
          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {FEATURES.map((f) => (
              <article key={f.title} className="panel p-6">
                <f.icon size={22} className="text-accent_amber" />
                <h3 className="mt-4 font-heading text-lg font-semibold text-ink_soft">
                  {f.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-ink_muted">{f.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* FLOW */}
      <section id="flow" className="mx-auto max-w-6xl px-5 py-16">
        <h2 className="font-heading text-2xl font-semibold text-ink_soft sm:text-3xl">
          Miten Valjas pyörii
        </h2>
        <ol className="mt-10 grid grid-cols-1 gap-4 md:grid-cols-3">
          {FLOW.map((s) => (
            <li key={s.step} className="panel relative overflow-hidden p-6">
              <span className="absolute right-4 top-4 font-code text-xs text-copper_reveal/80">
                {s.step}
              </span>
              <h3 className="mt-1 font-heading text-lg font-semibold text-ink_soft">
                {s.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-ink_muted">{s.body}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* CTA RAIL */}
      <section className="relative overflow-hidden border-t border-panel_oxidized/40">
        <div className="mx-auto max-w-6xl px-5 py-16 text-center">
          <h2 className="font-heading text-3xl font-bold text-ink_soft sm:text-4xl">
            Skannasit QR:n. Nyt on aika ottaa <span className="text-accent_amber">Achii taskuun</span>.
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-sm text-ink_muted">
            Lataa demo, liitä pitkä .md-konteksti ja katso miten lokaali NPU prosessoi sen
            alle kolmessa sekunnissa — ilman pilveä.
          </p>
          <div className="mt-8 flex justify-center">
            <Link to="/download" className="copper-cta">
              <Zap size={16} /> Siirry latauksiin
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-panel_oxidized/40 bg-base_bg/70">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-5 py-6 font-code text-[11px] uppercase tracking-[0.22em] text-ink_muted sm:flex-row">
          <span>AgentDir × Achii // Builder's Challenge 2026</span>
          <span>Sovereign Engine · v4.1</span>
        </div>
      </footer>
    </div>
  );
}
