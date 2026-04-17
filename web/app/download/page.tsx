import type { Metadata } from "next";
import Link from "next/link";
import { Apple, Smartphone, ArrowLeft, ShieldCheck, Zap, Cpu } from "lucide-react";
import { AchiiLogo } from "@/components/AchiiLogo";

export const metadata: Metadata = {
  title: "Lataa Achii",
  description:
    "Builder's Challenge 2026 -demo. Lataa AgentDir × Achii Sovereign Engine iOS TestFlightistä tai suorana Android APK:na.",
};

const SPECS = [
  {
    Icon: Zap,
    k: "2.5 s",
    v: "Keskimääräinen NPU-latenssi Gemma 4B:lle mobiilissa.",
  },
  {
    Icon: ShieldCheck,
    k: "0 B",
    v: "Egress pilveen oletusasetuksilla. Sanitointi tapahtuu ennen mitään kutsua.",
  },
  {
    Icon: Cpu,
    k: "Gemma 4B",
    v: "MLC-runtimella puhelimen NPU:lla. q4 kvantisointi, noin 2,4 GB painot.",
  },
];

export default function Download() {
  return (
    <div className="min-h-screen bg-base_bg px-6 py-10 text-ink_soft md:px-10">
      <header className="mx-auto flex max-w-4xl items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-2 font-mono text-[12px] uppercase tracking-[0.22em] text-ink_muted transition hover:text-accent_amber"
        >
          <ArrowLeft size={14} />
          takaisin
        </Link>
        <div className="flex items-center gap-3">
          <AchiiLogo size={28} />
          <span className="font-display text-sm font-semibold tracking-[0.22em] text-ink_soft">
            AGENTDIR × ACHII
          </span>
        </div>
      </header>

      <main className="mx-auto mt-14 max-w-xl text-center">
        <div className="eyebrow mb-4 inline-flex rounded-full border border-accent_amber/30 bg-accent_amber/5 px-3 py-1">
          Builder&apos;s Challenge 2026 · live-demo
        </div>
        <h1 className="font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
          Lopeta yappaus.<br />
          <span className="text-accent_amber">Ota Achii taskuun.</span>
        </h1>
        <p className="mt-5 font-body text-[15px] leading-relaxed text-ink_soft/70">
          Skannasit koodin — nyt on aika kokeilla. Lataa lokaali Sovereign
          Enginen mobiilidemo ja näe Harness Engineering käytännössä. NPU
          hoitaa inferenssin, gatekeeper hoitaa rajat, sinä hoidat päätökset.
        </p>

        <div className="mt-10 flex flex-col gap-4">
          <a href="#" className="copper-cta w-full justify-center py-4 text-base">
            <Apple size={18} />
            Lataa iOS — TestFlight
          </a>
          <a
            href="#"
            className="ghost-cta w-full justify-center py-4 text-base"
          >
            <Smartphone size={18} />
            Lataa Android — .apk
          </a>
        </div>
        <p className="mt-3 font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
          * Vaatii NPU-kiihdytyksen tuen. Suositus: A17 Pro+ / Tensor G3 / 8 Gen 3.
        </p>

        <section className="panel mt-14 p-6 text-left">
          <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.22em] text-accent_amber">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent_amber" />
            achiin huomautus
          </div>
          <p className="mt-3 font-body text-[14.5px] leading-relaxed text-ink_soft/80">
            &ldquo;Isäntä! Ennen kuin sä lataat mut, varmista että akkusi on yli
            50 %. Mä herätän NPU:si ja se ottaa hieman virtaa. Jos jätät mut
            yksin lataamisen jälkeen, saatan järjestellä sähköpostisi
            uudelleen — lupaan ettei mikään mene hukkaan.&rdquo;
          </p>
        </section>

        <section className="mt-10 grid grid-cols-1 gap-4 text-left sm:grid-cols-3">
          {SPECS.map((s) => (
            <div key={s.k} className="panel p-4">
              <div className="flex items-center gap-2 text-accent_amber">
                <s.Icon size={16} />
                <span className="font-display text-lg font-semibold text-ink_soft">
                  {s.k}
                </span>
              </div>
              <p className="mt-2 font-body text-[13px] leading-snug text-ink_soft/65">
                {s.v}
              </p>
            </div>
          ))}
        </section>
      </main>

      <footer className="mx-auto mt-20 max-w-4xl border-t border-panel_line pt-8 text-center font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
        AgentDir × Achii · Builder&apos;s Challenge 2026 · Turku, Finland
      </footer>
    </div>
  );
}
