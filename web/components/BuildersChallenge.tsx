"use client";

import { motion } from "framer-motion";
import { Calendar, MapPin, Mail, Github, Send } from "lucide-react";

const AGENDA = [
  {
    time: "10:00",
    title: "Doors · kahvit · rekisteröinti",
    body: "Turku Arena, eteisaula. Osallistujapassit jaetaan paikan päällä."
  },
  {
    time: "11:30",
    title: "Keynote — Lopeta yappaus. Rakenna valjaat.",
    body: "15 min demo: sama valjas ajetaan pilvessä ja lokaalisti, vertailu live."
  },
  {
    time: "13:00",
    title: "Workshop — oma ensimmäinen .yaml-valjas",
    body: "90 min, max 40 hlö, oma kone. Achii asennetaan paikalla, ajot Gemma 4B:llä."
  },
  {
    time: "16:00",
    title: "Builder's Showcase & tuomariston arvio",
    body: "7 min per tiimi. Ensimmäinen palkinto: lifetime-lisenssi Sovereign Engineen."
  }
];

export function BuildersChallenge() {
  return (
    <section
      id="areena"
      className="section-pad relative isolate overflow-hidden border-t border-panel_line py-28 md:py-36"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(70%_50%_at_20%_10%,rgba(243,156,18,0.08),transparent_70%)]"
      />

      <div className="mx-auto grid max-w-7xl gap-14 lg:grid-cols-[1.05fr_0.95fr]">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.55 }}
        >
          <div className="eyebrow mb-4">{"//"} 06 · Builder&apos;s Challenge</div>
          <h2 className="font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
            Turku Arena.<br />
            <span className="text-accent_amber">13. toukokuuta 2026.</span>
          </h2>
          <p className="mt-6 max-w-xl font-body text-lg leading-relaxed text-ink_soft/75">
            Yhden päivän kenttä sovereign-engineerien harjoitusotteluun. Ei
            PowerPointeja, ei sponsoripaneeleja, ei LinkedIn-lanseerauksia. Vain
            koodeja, valjaita ja Achii seisomassa metallipaneelissaan näyttämön
            laidalla. Osallistuminen on maksuton kutsuvieraille — pyydä kutsu
            alla olevalla lomakkeella tai skannaamalla QR Micin Drop -osiosta.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-4 font-mono text-[12px] uppercase tracking-[0.22em] text-ink_muted">
            <span className="inline-flex items-center gap-2">
              <Calendar size={13} className="text-accent_amber" />
              13.5.2026 · 10:00 — 18:00
            </span>
            <span className="hidden h-3 w-px bg-panel_line md:inline" />
            <span className="inline-flex items-center gap-2">
              <MapPin size={13} className="text-accent_amber" />
              Turku Arena · Artukaistentie 20
            </span>
          </div>

          <ol className="mt-10 space-y-4">
            {AGENDA.map((item, i) => (
              <motion.li
                key={item.time}
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, amount: 0.4 }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                className="panel flex gap-5 p-5"
              >
                <div className="font-mono text-[13px] font-semibold text-accent_amber">
                  {item.time}
                </div>
                <div>
                  <div className="font-display text-[15px] font-semibold text-ink_soft">
                    {item.title}
                  </div>
                  <p className="mt-1 font-body text-[14px] leading-relaxed text-ink_soft/70">
                    {item.body}
                  </p>
                </div>
              </motion.li>
            ))}
          </ol>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.55, delay: 0.1 }}
          className="panel flex h-fit flex-col gap-6 p-8"
        >
          <div>
            <div className="eyebrow mb-2">Ota yhteyttä</div>
            <h3 className="font-display text-2xl font-semibold text-ink_soft">
              Pyydä kutsu tai arvioijan passi
            </h3>
            <p className="mt-3 font-body text-[14.5px] leading-relaxed text-ink_soft/70">
              Lomake menee suoraan sähköpostiin. Emme tallenna tietoja kolmannen
              osapuolen CRM:ään emmekä siirrä niitä pilveen — käsittely on
              lokaalia ja vastaus tulee 48 tunnin sisällä.
            </p>
          </div>

          <form
            className="grid gap-4"
            action="mailto:achii@agentdir.dev"
            method="post"
            encType="text/plain"
          >
            <label className="grid gap-2">
              <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
                Nimi
              </span>
              <input
                type="text"
                name="nimi"
                required
                placeholder="Matti Meikäläinen"
                className="rounded-md border border-panel_line bg-panel_deep/40 px-3 py-2 font-body text-[14px] text-ink_soft placeholder:text-ink_muted/60 focus:border-accent_amber/60 focus:outline-none"
              />
            </label>
            <label className="grid gap-2">
              <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
                Sähköposti
              </span>
              <input
                type="email"
                name="sahkoposti"
                required
                placeholder="matti@firma.fi"
                className="rounded-md border border-panel_line bg-panel_deep/40 px-3 py-2 font-body text-[14px] text-ink_soft placeholder:text-ink_muted/60 focus:border-accent_amber/60 focus:outline-none"
              />
            </label>
            <label className="grid gap-2">
              <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
                Rooli
              </span>
              <select
                name="rooli"
                defaultValue="rakentaja"
                className="rounded-md border border-panel_line bg-panel_deep/40 px-3 py-2 font-body text-[14px] text-ink_soft focus:border-accent_amber/60 focus:outline-none"
              >
                <option value="rakentaja">Rakentaja · hacker</option>
                <option value="arvioija">Tuomari · arvioija</option>
                <option value="media">Media · kirjoittaja</option>
                <option value="sijoittaja">Sijoittaja · rahoittaja</option>
              </select>
            </label>
            <label className="grid gap-2">
              <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
                Viesti Achiille
              </span>
              <textarea
                name="viesti"
                rows={4}
                placeholder="Mitä rakennat ja miksi haluat valjaat?"
                className="resize-none rounded-md border border-panel_line bg-panel_deep/40 px-3 py-2 font-body text-[14px] text-ink_soft placeholder:text-ink_muted/60 focus:border-accent_amber/60 focus:outline-none"
              />
            </label>
            <button type="submit" className="copper-cta mt-2">
              Lähetä kutsupyyntö
              <Send size={15} />
            </button>
          </form>

          <div className="border-t border-panel_line pt-5">
            <div className="eyebrow mb-3">Suora linja</div>
            <ul className="space-y-2 font-body text-[14px] text-ink_soft/80">
              <li className="flex items-center gap-2">
                <Mail size={14} className="text-accent_amber" />
                <a
                  href="mailto:achii@agentdir.dev"
                  className="transition hover:text-accent_amber"
                >
                  achii@agentdir.dev
                </a>
              </li>
              <li className="flex items-center gap-2">
                <Github size={14} className="text-accent_amber" />
                <a
                  href="https://github.com/harleysederholm-alt/AgentDir"
                  className="transition hover:text-accent_amber"
                >
                  github.com/harleysederholm-alt/AgentDir
                </a>
              </li>
            </ul>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
