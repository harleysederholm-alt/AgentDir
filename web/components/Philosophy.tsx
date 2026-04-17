"use client";

import { motion } from "framer-motion";
import { Dices, Scale, ShieldAlert } from "lucide-react";

const CONTRAST = [
  {
    mode: "Prompting",
    subtitle: "Arvaamista luonnollisella kielellä",
    bullet: [
      "Sanamuoto ratkaisee, ei rakenne.",
      "Malli näkee koko kontekstin sellaisenaan — mukaan lukien salaisuudet.",
      "Tulos vaihtelee ajojen välillä. Ei jäljitettävissä.",
      "Virhetilanne = rivin uudelleenkirjoitus."
    ],
    tone: "copper" as const,
    Icon: Dices
  },
  {
    mode: "Harnessing",
    subtitle: "Insinöörien kognitiivinen scaffolding",
    bullet: [
      "Skeema (.yaml) määrittelee askeleet, rajoitteet ja tyyppisopimukset.",
      "Konteksti (.md) tulee vain hallitusti, sanitoituna.",
      "Ajo on deterministinen: sama sisältö → sama ulostulo.",
      "Virhetilanne = validoitu pysähdys ennen egressä."
    ],
    tone: "amber" as const,
    Icon: Scale
  }
];

export function Philosophy() {
  return (
    <section
      id="filosofia"
      className="section-pad relative isolate overflow-hidden border-t border-panel_line py-24 md:py-32"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_40%_at_50%_0%,rgba(243,156,18,0.06),transparent_70%)]"
      />
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
          <div>
            <div className="eyebrow mb-4">{"//"} 01 · Filosofia</div>
            <h2 className="font-display text-4xl font-bold leading-[1.06] tracking-tight text-ink_soft md:text-5xl">
              Pilvi-AI arvaa.<br />
              <span className="text-accent_amber">Valjaat pakottavat.</span>
            </h2>
          </div>
          <p className="max-w-xl font-body text-[16.5px] leading-relaxed text-ink_soft/75">
            Suuret kielimallit eivät epäonnistu siksi, että ne olisivat tyhmiä. Ne epäonnistuvat,
            koska niiltä on unohdettu arkkitehtuuri. Pilvi-SaaS nojaa yhteen tekstipromptiin, joka
            upotetaan 128 kilotavun kontekstiin, ja odottaa luovaa tulosta kuin runoilulta. Luotettavaa
            ohjelmistoa ei rakenneta runoilemalla. Se rakennetaan sopimuksilla, tyypeillä ja
            rajapinnoilla — Harness Engineeringillä.
          </p>
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-2">
          {CONTRAST.map((col, i) => (
            <motion.article
              key={col.mode}
              initial={{ opacity: 0, y: 22 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.55, delay: i * 0.08 }}
              className="panel relative flex h-full flex-col gap-5 p-7"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`grid h-11 w-11 place-items-center rounded-lg border border-panel_line bg-panel_deep/70 ${
                    col.tone === "amber" ? "text-accent_amber" : "text-accent_copper"
                  }`}
                >
                  <col.Icon size={20} />
                </div>
                <div>
                  <h3 className="font-display text-xl font-semibold text-ink_soft">{col.mode}</h3>
                  <div className="font-mono text-[12px] text-ink_muted">{col.subtitle}</div>
                </div>
              </div>
              <ul className="space-y-3 font-body text-[14.5px] leading-relaxed text-ink_soft/80">
                {col.bullet.map((b) => (
                  <li key={b} className="flex items-start gap-3">
                    <span
                      className={`mt-2 h-1.5 w-1.5 rounded-full ${
                        col.tone === "amber" ? "bg-accent_amber" : "bg-accent_copper"
                      }`}
                    />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </motion.article>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.55, delay: 0.1 }}
          className="panel mt-10 grid gap-6 p-7 md:grid-cols-[auto_1fr] md:items-start"
        >
          <div className="grid h-11 w-11 place-items-center rounded-lg border border-accent_amber/40 bg-accent_amber/10 text-accent_amber">
            <ShieldAlert size={20} />
          </div>
          <div>
            <h3 className="font-display text-lg font-semibold text-ink_soft">
              Miksi pilvi-AI on epäluotettava tuotannossa
            </h3>
            <p className="mt-2 font-body text-[15px] leading-relaxed text-ink_soft/75">
              Pilvimalli ei ole deterministinen. Sama prompt palauttaa eri vastauksen eri ajoilla,
              koska sampling, tokenisaatio ja versiopäivitykset muuttuvat ilmoituksetta. Samaan aikaan
              kaikki syötteesi — mukaan lukien API-avaimet, asiakasnimet, terveystiedot — kulkevat
              kolmannen osapuolen GPU-klustereille, joissa niitä saa lokittaa ja käyttää malliharjoitukseen.
              Jos tuotteesi tekee päätöksiä käyttäjän puolesta, tämä yhdistelmä on vakuutusmatemaattinen
              aikapommi. Valjaat tekevät ajosta toistettavan, kontekstista sanitoidun ja eskalaation pakolliseksi.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
