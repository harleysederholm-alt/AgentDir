import { useCallback, useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { StatusPill } from "@/components/StatusPill";
import { OriginStory } from "@/components/OriginStory";
import { STORY_SEEN_KEY } from "@/origin_story";

type Phase = "loading" | "onboarding" | "nexus";

function readSeen(): boolean {
  try {
    return window.localStorage.getItem(STORY_SEEN_KEY) === "1";
  } catch {
    return false;
  }
}

function writeSeen(): void {
  try {
    window.localStorage.setItem(STORY_SEEN_KEY, "1");
  } catch {
    /* private mode / storage disabled — skip silently */
  }
}

export default function App() {
  const [phase, setPhase] = useState<Phase>("loading");

  useEffect(() => {
    setPhase(readSeen() ? "nexus" : "onboarding");
  }, []);

  const handleEngage = useCallback(() => {
    writeSeen();
    setPhase("nexus");
  }, []);

  if (phase === "loading") {
    return <div className="app-container grain" aria-busy="true" />;
  }

  if (phase === "onboarding") {
    return <OriginStory onEngage={handleEngage} />;
  }

  return (
    <div className="app-container grain">
      <Header />
      <main className="relative z-10 mx-auto w-full max-w-md px-4 pb-8">
        <section className="-mt-10 flex flex-col gap-3">
          <StatusPill tone="copper">builder&apos;s challenge · live demo</StatusPill>
          <h1 className="font-display text-3xl font-bold leading-tight tracking-tight text-ink_soft">
            Lopeta yappaus.
            <br />
            <span className="text-accent_amber">Ota Achii taskuun.</span>
          </h1>
          <p className="text-sm leading-relaxed text-ink_muted">
            Tämä on Sovereign Engine -mobiilidemo. Achii ajaa Gemma 4B -mallia lokaalisti NPU:lla,
            ja gatekeeper sanitoi syötteesi ennen kuin se näkee yhdenkään tavun. Ei pilveä, ei hallusinaatiota,
            ei tiedonvuotoa — vain valjaita.
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            <StatusPill tone="amber">latenssi · 2,5 s</StatusPill>
            <StatusPill tone="success">egress · 0 B</StatusPill>
            <StatusPill tone="muted">ctx · .yaml + .md</StatusPill>
          </div>
        </section>

        <ChatPanel />

        <section className="glass-panel mt-4 p-4">
          <div className="eyebrow">// achiin huomautus</div>
          <p className="mt-2 text-sm leading-relaxed text-ink_soft">
            <strong className="text-accent_amber">Isäntä!</strong> Varmista että akku on yli 50 %
            ennen raskaita valjaita. Herätän NPU:n, ja se vie virtaa. Jos jätät minut yksin
            latauksen jälkeen, järjestelen postilaatikkosi uudelleen — tiedoksi.
          </p>
        </section>

        <section className="mt-4 grid grid-cols-2 gap-3">
          <div className="glass-panel p-3">
            <div className="eyebrow">// inferenssi</div>
            <div className="mt-1 font-mono text-sm text-ink_soft">Gemma 4B · Q4_K_M</div>
            <div className="mt-0.5 text-[11px] text-ink_muted">Paikallinen, NPU-kiihdytetty</div>
          </div>
          <div className="glass-panel p-3">
            <div className="eyebrow">// sandbox</div>
            <div className="mt-1 font-mono text-sm text-ink_soft">Gatekeeper · ON</div>
            <div className="mt-0.5 text-[11px] text-ink_muted">Rust-pohjainen sanitisointi</div>
          </div>
          <div className="glass-panel p-3">
            <div className="eyebrow">// konteksti</div>
            <div className="mt-1 font-mono text-sm text-ink_soft">.yaml + .md</div>
            <div className="mt-0.5 text-[11px] text-ink_muted">Logiikka / konteksti eroteltu</div>
          </div>
          <div className="glass-panel p-3">
            <div className="eyebrow">// muisti</div>
            <div className="mt-1 font-mono text-sm text-ink_soft">Lokaali · Vektoritöntä</div>
            <div className="mt-0.5 text-[11px] text-ink_muted">RAG ilman pilveä</div>
          </div>
        </section>

        <footer className="mt-6 space-y-2 text-center font-mono text-[10.5px] uppercase tracking-[0.22em] text-ink_dim">
          <div>AgentDir × Achii · Sovereign Engine</div>
          <div>v1.0.4-beta · &ldquo;The Rusty Awakening&rdquo;</div>
          <div className="text-ink_dim/70">MIT + AGPL · Privacy (local-first) · Terms of Sovereignty</div>
        </footer>
      </main>
    </div>
  );
}
