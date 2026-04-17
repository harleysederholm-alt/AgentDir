"use client";

import { motion } from "framer-motion";
import { FileCode2, ShieldCheck, Cpu } from "lucide-react";
import Image from "next/image";

const PILLARS = [
  {
    Icon: FileCode2,
    title: "Huolten erottaminen",
    lead: "`.yaml` on logiikka. `.md` on konteksti.",
    body:
      "AgentDir pakottaa työnkulun strukturoituun kaksikkoon. `.yaml` määrittää askeleet, mallivalinnat, retry-käytännön ja tyyppisopimukset. `.md` tuo kontekstin — projektit, muistiot, eilisen päätökset, dokumentit. Kumpaakaan ei muokata ajon aikana. Tulos: jokainen ajo on diff-tattava ja peer-review-kelpoinen kuten mikä tahansa Pull Request. Prompt engineering menee eläkkeelle.",
    footer: "valjaat/01-scaffolding.yaml · docs/03-PRDs/",
  },
  {
    Icon: ShieldCheck,
    title: "Portinvartija-protokolla",
    lead: "Ei pilvikutsua ilman puhdistusta.",
    body:
      "Rust-taustapalvelu (Gatekeeper) siivoaa jokaisen pilveen lähtevän bytetason paketin: API-avaimet, Bearer-tokenit, henkilötiedot ja konfiguraatiosalat peittyvät regex-taulukolla ennen egressiä. Jos malli palauttaa epämuodostuneen YAML:n, Gatekeeper triggeröi `VALIDATION_ERROR`-tilan, loggaa diffin ja estää eskalaation — sinä näet tarkalleen mitä oli lähdössä ulos.",
    footer: "gatekeeper.rs · sanitizer::run()",
  },
  {
    Icon: Cpu,
    title: "Lokaali inferenssi edge:llä",
    lead: "Gemma 4B pyörii NPU:ssa, ei pilvessä.",
    body:
      "Oletusmoottori on Gemma 4B (q4_K_M) ajettuna työpöydällä MediaPipe LLM -runtimella, mobiilissa MLC:llä. NPU-kiihdytys (Snapdragon X Elite, Intel Core Ultra, Apple Neural Engine, Tensor G3) hoitaa 2,5 s latenssin keskimäärin — täysin offline. Pilvi (Opus, GPT-4, Sonnet) on olemassa vain eskalaatiopolkuna, ja sekin kulkee Gatekeeperin läpi kirjatussa audit-ketjussa.",
    footer: "local_ai.rs · gemma-4b.q4_K_M",
  },
];

const YAML_SAMPLE = `# valjaat/02-refactor-sweep.yaml
meta:
  name: refactor-sweep
  determinism: strict       # same input -> same output
  version: 1.0.4-beta

inputs:
  - kind: markdown          # .md context, immutable during run
    path: docs/03-PRDs/active.md
  - kind: codebase
    glob: "src/**/*.ts"

steps:
  - id: plan
    model: local/gemma-4b-q4
    temperature: 0           # no sampling, no guessing
    schema: schemas/plan.json
  - id: apply
    when: plan.risk == "low"
    tool: fs.patch
    guard: gatekeeper.sanitise

egress:
  allow: []                  # no cloud by default
  escalate_on:
    - plan.risk == "high"
    - plan.confidence < 0.6`;

const MD_SAMPLE = `# docs/03-PRDs/active.md

> Context-of-record — read-only at runtime.

## Tavoite
Vähennä \`apps/webserver/app/__init__.py\`:n
syklinen tuonti ilman että rikot
\`/health\`-reittiä (CI #1443).

## Rajoitteet
- Ei uusia riippuvuuksia.
- Ei lisenssin vaihtoa (AGPL sisällä).
- Tulos menee Gatekeeper::sanitise():in läpi.

## Audit-muistio
Viimeksi kosketti: @harleysederholm,
2026-04-11, commit \`a91c3e2\`.`;

export function HarnessSpec() {
  return (
    <section
      id="spec"
      className="section-pad relative isolate overflow-hidden border-t border-panel_line py-28 md:py-36"
    >
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-end">
          <div className="max-w-2xl">
            <div className="eyebrow mb-4">{"//"} 03 · Harness Engineering spec</div>
            <h2 className="font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
              Kolme valjasta.<br />
              <span className="text-accent_amber">Ei tilaa hallusinaatiolle.</span>
            </h2>
          </div>
          <p className="max-w-md font-body text-base leading-relaxed text-ink_soft/70">
            Sovereign Engine on rakennettu kolmelle pelimerkille. Kaikki muu —
            editorit, mobiili, QR-koodit — palvelee näitä kolmea.
          </p>
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {PILLARS.map((p, i) => (
            <motion.article
              key={p.title}
              initial={{ opacity: 0, y: 22 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.35 }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="panel relative flex h-full flex-col gap-5 p-7"
            >
              <div className="flex items-center gap-3">
                <div className="grid h-11 w-11 place-items-center rounded-lg border border-panel_line bg-panel_deep/70">
                  <p.Icon size={20} className="text-accent_amber" />
                </div>
                <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
                  0{i + 1}
                </span>
              </div>
              <div>
                <h3 className="font-display text-xl font-semibold text-ink_soft">
                  {p.title}
                </h3>
                <p className="mt-1 font-mono text-[12.5px] text-accent_copper">
                  {p.lead}
                </p>
              </div>
              <p className="font-body text-[15px] leading-relaxed text-ink_soft/75">
                {p.body}
              </p>
              <div className="mt-auto border-t border-panel_line pt-4 font-mono text-[11px] uppercase tracking-[0.18em] text-ink_muted">
                {p.footer}
              </div>
            </motion.article>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.25 }}
          transition={{ duration: 0.55 }}
          className="mt-16 grid gap-6 lg:grid-cols-2"
        >
          <article className="panel overflow-hidden">
            <header className="flex items-center justify-between border-b border-panel_line bg-panel_deep/40 px-5 py-3">
              <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-accent_amber">
                .yaml · logiikka
              </span>
              <span className="font-mono text-[10.5px] uppercase tracking-[0.22em] text-ink_muted">
                deterministic
              </span>
            </header>
            <pre className="overflow-x-auto px-5 py-4 font-mono text-[12.5px] leading-relaxed text-ink_soft/85">
              <code>{YAML_SAMPLE}</code>
            </pre>
          </article>
          <article className="panel overflow-hidden">
            <header className="flex items-center justify-between border-b border-panel_line bg-panel_deep/40 px-5 py-3">
              <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-accent_copper">
                .md · konteksti
              </span>
              <span className="font-mono text-[10.5px] uppercase tracking-[0.22em] text-ink_muted">
                read-only at runtime
              </span>
            </header>
            <pre className="overflow-x-auto px-5 py-4 font-mono text-[12.5px] leading-relaxed text-ink_soft/85">
              <code>{MD_SAMPLE}</code>
            </pre>
          </article>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="panel mt-8 p-7"
        >
          <h3 className="font-display text-xl font-semibold text-ink_soft">
            Miten tämä estää hallusinaation lokaalisti
          </h3>
          <div className="mt-4 grid gap-6 md:grid-cols-3">
            <div>
              <div className="eyebrow mb-2">1 · Skeeman validointi</div>
              <p className="font-body text-[14.5px] leading-relaxed text-ink_soft/75">
                Jokainen step-ulostulo validoidaan JSON-skemaa vasten ennen kuin
                seuraava step saa suorittaa. Malli ei voi &ldquo;luoda uutta
                kenttää&rdquo; — kenttää ei olemassa, jos skemaa ei hyväksytty.
              </p>
            </div>
            <div>
              <div className="eyebrow mb-2">2 · Ei mukautuvaa samplingia</div>
              <p className="font-body text-[14.5px] leading-relaxed text-ink_soft/75">
                <code className="font-mono text-accent_amber">temperature: 0</code>{" "}
                on oletus. Jos ajoihin tarvitaan luovaa vaihtelua, se pyydetään
                eksplisiittisesti tilamuuttujalla, ja diff-loggi näyttää miksi.
              </p>
            </div>
            <div>
              <div className="eyebrow mb-2">3 · Eskalaatio vaatii hallitsijan</div>
              <p className="font-body text-[14.5px] leading-relaxed text-ink_soft/75">
                Pilvieskalaatio (Opus / Sonnet / GPT-4) tapahtuu vain{" "}
                <code className="font-mono text-accent_amber">escalate_on</code>-
                säännön täyttyessä. Käyttäjä vahvistaa diffin ennen egressiä.
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="relative mt-12 overflow-hidden rounded-2xl border border-panel_line shadow-panel"
        >
          <div className="relative aspect-[21/9] w-full">
            <Image
              src="/images/achii-wrench.jpg"
              alt="Achii korjaa järjestelmää jakoavaimella — holografinen vuokaavio näyttää .yaml → gatekeeper → lokaali inferenssi -polun."
              fill
              className="object-cover"
              sizes="100vw"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-base_bg/90 via-base_bg/10 to-transparent" />
          </div>
          <div className="absolute inset-x-0 bottom-0 flex flex-col gap-1 p-6 md:p-10">
            <span className="eyebrow">Harness visual — suorituspolku</span>
            <h3 className="font-display text-2xl font-semibold text-ink_soft md:text-3xl">
              input → gatekeeper → local_ai → output
            </h3>
            <p className="max-w-2xl font-body text-sm text-ink_soft/70">
              Jokainen nuoli on sopimus. Jos tyyppi ei täsmää, ajo pysähtyy
              ennen pilveä. Valjaat eivät jousta.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
