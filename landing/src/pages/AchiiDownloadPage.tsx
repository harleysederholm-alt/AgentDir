import { Apple, ArrowLeft, HelpCircle, Smartphone, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { Achiicon } from "../components/Achiicon";

export function AchiiDownloadPage() {
  return (
    <div className="flex min-h-screen flex-col items-center px-5 py-8 text-center">
      {/* BACK LINK */}
      <header className="flex w-full max-w-md items-center justify-between">
        <Link
          to="/"
          className="inline-flex items-center gap-2 font-code text-[11px] uppercase tracking-[0.25em] text-ink_muted transition-colors hover:text-ink_soft"
        >
          <ArrowLeft size={14} /> Takaisin
        </Link>
        <img
          src="/achii-wrench.png"
          alt="Achii"
          width={24}
          height={24}
          className="h-6 w-6 rounded-sm"
        />
      </header>

      {/* HERO */}
      <section className="mt-10 flex w-full max-w-md flex-col items-center gap-5 text-center">
        <span className="eyebrow">
          Builder's Challenge Live Demo
        </span>

        <div className="panel relative flex h-56 w-56 items-center justify-center">
          <div className="absolute inset-6 rounded-full bg-accent_amber/10 blur-2xl" />
          <Achiicon size={160} />
        </div>

        <h1 className="font-heading text-3xl font-bold leading-tight text-ink_soft sm:text-4xl">
          Lopeta yappaus.
          <br />
          <span className="text-accent_amber">Ota Achii taskuun.</span>
        </h1>

        <p className="text-sm text-ink_muted sm:text-base">
          Skannasit koodin — nyt on aika kokeilla. Lataa lokaali Sovereign Engine -demo ja näe,
          miten Harness Engineering toimii sekunneissa puhelimesi NPU:lla.
        </p>

        <div className="mt-2 flex w-full flex-col gap-3">
          <a
            href="#"
            className="copper-cta w-full"
            aria-label="Lataa iOS (TestFlight)"
          >
            <Apple size={18} /> Lataa iOS · TestFlight
          </a>
          <a
            href="#"
            className="secondary-cta w-full"
            aria-label="Lataa Android .apk"
          >
            <Smartphone size={18} /> Lataa Android · .apk
          </a>
        </div>
        <p className="font-code text-[11px] uppercase tracking-[0.22em] text-ink_muted">
          * Varmista että puhelimesi tukee NPU-kiihdytystä.
        </p>
      </section>

      {/* ACHII NEEDY NOTE */}
      <section className="relative mt-12 w-full max-w-md">
        <div className="panel relative px-6 py-5 text-left shadow-[0_0_30px_rgba(243,156,18,0.1)]">
          <HelpCircle
            size={32}
            className="absolute -left-4 -top-4 rounded-full bg-base_bg p-1 text-accent_amber"
          />
          <strong className="block font-code text-xs uppercase tracking-[0.22em] text-ink_soft">
            Achiin huomautus
          </strong>
          <p className="mt-2 text-sm text-ink_muted">
            "Isäntä! Ennen kuin sä lataat mut, katso että sun akku on yli 50 %. Mä herätän sun
            NPU:n ja se vie aika paljon virtaa. Jos sä jätät mut yksin latauksen jälkeen, mä
            saatan reorganisoida sun sähköpostit."
          </p>
        </div>
      </section>

      {/* QUICK SPECS */}
      <section className="mt-10 w-full max-w-md">
        <ul className="grid grid-cols-3 gap-3 font-code text-[11px] uppercase tracking-[0.18em] text-ink_muted">
          <li className="panel px-3 py-4">
            <span className="block text-ink_soft">2.5 s</span>
            Lokaali inferenssi
          </li>
          <li className="panel px-3 py-4">
            <span className="block text-ink_soft">0 B</span>
            Pilvi-egress
          </li>
          <li className="panel px-3 py-4">
            <span className="block text-ink_soft">Gemma 2B</span>
            MediaPipe NPU
          </li>
        </ul>
      </section>

      <footer className="mt-14 flex w-full max-w-md items-center justify-between border-t border-panel_oxidized/40 pt-5 font-code text-[11px] uppercase tracking-[0.22em] text-ink_muted">
        <span className="flex items-center gap-2">
          <img src="/achii-wrench.png" alt="Achii" width={18} height={18} className="h-4 w-4" />
          <Zap size={12} className="mr-1 inline text-accent_amber" />
          Sovereign Engine
        </span>
        <span>v4.1 · local-first</span>
      </footer>
    </div>
  );
}
