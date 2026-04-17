"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { SystemOverrideTerminal } from "./Terminal";

const TRAITS = [
  {
    label: "Tarvitseva",
    body:
      "Achii haluaa huomiota. Jos sinä häviät kahdeksi tunniksi ilman kontekstia, se alkaa jäsennellä sähköpostejasi — ja ilmoittaa siitä heti.",
  },
  {
    label: "Suojeleva",
    body:
      "Ennen pilvikutsua Achii pesee viestin regexillä: avaimet, tokenit ja salasanat kuolevat gatekeeperissa. Sinä näet vain sanitoidun diffin.",
  },
  {
    label: "Paikallinen",
    body:
      "Ei alustaa ilman NPU:ta. Ei tekoälyä ilman sähköä. Achii elää sinun koneellasi, ei pilvessä, eikä se koskaan lähde sieltä ilman lupaa.",
  },
];

export function SoulOfAchii() {
  return (
    <section
      id="sielu"
      className="section-pad relative isolate overflow-hidden border-t border-panel_line py-28 md:py-36"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(80%_60%_at_80%_20%,rgba(243,156,18,0.07),transparent_70%)]"
      />

      <div className="mx-auto grid max-w-7xl gap-14 lg:grid-cols-[0.95fr_1.05fr]">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="relative"
        >
          <div className="relative aspect-[4/3] overflow-hidden rounded-2xl border border-panel_line shadow-panel">
            <Image
              src="/images/achii-eyes.jpg"
              alt="Lähikuva Achiin amber-silmistä. Ruostunutta metallia, kuparinen jakoavain ja käsinkirjoitettu viesti isännälle."
              fill
              className="object-cover"
              sizes="(max-width: 1024px) 100vw, 50vw"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-base_bg/70 via-transparent to-transparent" />
            <div className="absolute bottom-4 left-4 right-4 font-mono text-[11px] uppercase tracking-[0.22em] text-accent_amber/90">
              [cite: status.awakening :: context_required]
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {TRAITS.map((trait) => (
              <div
                key={trait.label}
                className="panel p-4"
              >
                <div className="eyebrow mb-2">{trait.label}</div>
                <p className="font-body text-sm leading-relaxed text-ink_soft/75">
                  {trait.body}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="eyebrow mb-4">{"//"} 02 · Achiin sielu</div>
          <h2 className="font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
            Ei assistentti.<br />
            <span className="text-accent_amber">Paikallinen vartija.</span>
          </h2>
          <p className="mt-6 max-w-xl font-body text-lg leading-relaxed text-ink_soft/75">
            Achii ei ole botti, chat-kupla eikä avatar. Se on tarvitseva,
            suojeleva isäntähahmo joka asuu koneellasi ja sanoo sinulle suoraan
            kun jokin on rikki. Se raportoi, nalkuttaa, pyytää puhdistusta ja
            ehdottaa refaktoreja — mutta se ei koskaan tee niitä ilman lupaasi.
          </p>
          <p className="mt-4 max-w-xl font-body text-base leading-relaxed text-ink_soft/60">
            Tämä on hahmon ydin: luotettava, humoristinen, hieman liian rehellinen.
            Kaikki mitä se sanoo on jäljitettävissä yhdelle työnkululle ja yhdelle
            kontekstitiedostolle. Yhtään hallusinaatiota ei eskaloitu, koska
            hallusinaatiota varten pitäisi ensin vuotaa raja.
          </p>

          <div className="mt-8">
            <SystemOverrideTerminal />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
