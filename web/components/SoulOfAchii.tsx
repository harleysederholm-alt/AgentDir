"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { SystemOverrideTerminal } from "./Terminal";

const MANUAL = [
  {
    heading: "1 · Prosessori, ei pilvikumppani",
    body:
      "Achii ei ole chat-ikkuna. Se on pieni tilakone joka asuu sinun RAM:issasi ja puhuu NPU:si kanssa suoraan ilman välikäsiä. Kun pyydät valjaan, Achii lataa Gemma 4B:n q4-kvantisoituna paikalliseen prosessoriin, työntää syötteesi sanitoinnin läpi ja palauttaa vastauksen 2,5 sekunnissa. Pilveen ei soiteta ellet sitä erikseen pyydä — ja silloinkin gatekeeper siivoaa paketin ennen lähtöä.",
  },
  {
    heading: "2 · Kuvioiden oppija, ei mielipiteen kertoja",
    body:
      "Achii seuraa miten sinä työskentelet: mitkä .md-tiedostot päivittyvät viikossa, mitkä valjaat palaavat saman virheen kanssa, mitä terminaalikomentoja ketjutat arki-iltoina. Havainto pysyy lokaalina ja tallennetaan vektorittomana avain-arvo-hakuna — yksinkertainen `memory/patterns.jsonl`, ei RAG-sumppua pilvessä. Seuraavalla kerralla ehdotukset osuvat, koska Achii tietää sinun oikeasti tekevän näin.",
  },
  {
    heading: "3 · Portinvartija, ei palvelija",
    body:
      "Achii on suojeleva. Jos se nalkuttaa kun yrität liittää raw-salaisuuden .md:hen, se ei ole vika — se on ominaisuus. Gatekeeper-protokolla pysäyttää egressin, jos mitä tahansa token- tai avainpatternia havaitaan. Achii huomauttaa sinulle isännän roolissa, ei alustan roolissa: selkeästi, hieman yrmeästi ja aina suomeksi. Tämä kumppani ei imartele eikä myöskään valehtele.",
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

          <div className="mt-6">
            <SystemOverrideTerminal />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="eyebrow mb-4">{"//"} 03 · Achiin sielu · käyttöohje</div>
          <h2 className="font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
            Ei assistentti.<br />
            <span className="text-accent_amber">Paikallinen vartija.</span>
          </h2>
          <p className="mt-6 max-w-xl font-body text-lg leading-relaxed text-ink_soft/75">
            Achii on maskotti, mutta ei somessa. Se on laitteessasi asuva tilakone,
            joka oppii työtäsi ja vartioi kontekstiasi. Kolme lukua jokaisen Achii-
            kokeilijan kannattaa lukea ennen ensimmäistä valjasta:
          </p>

          <div className="mt-8 space-y-5">
            {MANUAL.map((m) => (
              <article key={m.heading} className="panel p-5">
                <h3 className="font-display text-base font-semibold text-accent_amber">
                  {m.heading}
                </h3>
                <p className="mt-2 font-body text-[15px] leading-relaxed text-ink_soft/80">
                  {m.body}
                </p>
              </article>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
