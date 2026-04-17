"use client";

import { motion } from "framer-motion";
import { BookOpen, Search } from "lucide-react";
import { useMemo, useState } from "react";

interface Topic {
  tag: string;
  title: string;
  body: string;
  read: string;
}

const TOPICS: Topic[] = [
  {
    tag: "Security Whitepaper",
    title: "Miksi local-first on ainoa tapa suvereeneille tietoaineistoille",
    body:
      "Pilvi-LLM:t lokittavat syötteet oletuksena ja voivat käyttää niitä harjoitukseen. Kun rakennat tuotetta sairaalan, lakitoimiston tai puolustusteollisuuden asiakkaalle, tämä tekee pilvi-inferenssistä juridisesti mahdottoman. Sovereign Engine pitää painot, prompt-lokit ja audit-ketjun omalla koneellasi — pilvieskalaatio on opt-in ja kulkee aina Gatekeeperin sanitizerin läpi.",
    read: "26 min",
  },
  {
    tag: "Edge Compute",
    title: "NPU vs. GPU — miksi optimoimme reunalaskennalle",
    body:
      "NPU-piirit (Snapdragon X Elite, Intel Core Ultra, Apple Neural Engine) ajavat q4-kvantisoidun 4B-mallin 2,5 s latenssilla ja alle 8 W kuormituksella. Sama kuorma GPU:lla maksaa kertaluokkaa enemmän sähköä ilman latenssi-etua. Tämä luku käy läpi muistikaistan, KV-cache-säännöstelyn ja speculative decoding -reitit kolmelle laitealustalle.",
    read: "22 min",
  },
  {
    tag: "Logic Scaffolding",
    title: ".yaml-valjaat — miten rajaamme agenttikäyttäytymisen",
    body:
      "Valjas on sopimus, jonka malli ei voi rikkoa. Tässä dokumentissa näytetään miten `meta.determinism: strict`, JSON Schema -ulostulojen validointi, `egress.allow: []` -oletus ja `escalate_on`-säännöt yhdistyvät yksinkertaiseen tilakoneeseen. Mukana esimerkkivaljaat refaktorille, dokumentaatiosyntyyseille ja tietoturvatarkastukselle.",
    read: "18 min",
  },
  {
    tag: "Method",
    title: "Promptauksesta valjastamiseen — siirtymäopas tiimeille",
    body:
      "Lyhyt playbook joille tekstipromptit ovat kasvaneet hallitsemattomiksi. Miten murrat 400 rivin megapromptin neljäksi `.md`-kontekstiksi + `.yaml`-vuoksi, miten peer-review toimii ajon diffille, ja miten sovitat vanhat prompt-kokoelmat valjaisiin ilman että rikkoutuu yhtään olemassa olevaa tuotantoaajoa.",
    read: "14 min",
  },
  {
    tag: "Context Windows",
    title: "Kontekstin hallinta — mitä jätät pois 128 k -ikkunasta",
    body:
      "Jokaisesta token-tuhannesta laskutetaan ja jokainen turha token hajottaa mallin huomion. AgentDir täyttää ikkunan dependency-järjestyksessä: skeema, sitovat rajoitteet, aktiivinen `.md`, diff — ei mitään muuta. Tässä dokumentissa mitataan mitä näille neljälle tapahtuu kun skaalat 4 k:sta 128 k:hon eri mallisukupolvilla.",
    read: "16 min",
  },
  {
    tag: "Mobile Edge",
    title: "4B-malli puhelimen NPU:lla — kulutus, lämpö ja purku",
    body:
      "MLC LLM + Gemma 4B (q4) Tensor G3:lla ja Snapdragon 8 Gen 3:lla: 2,8 s latenssi, 3 W keskikulutus, 41 °C ihotila kahden minuutin ajon jälkeen. Achiin sääntö: kun akku < 50 %, haptinen palaute kertoo käyttäjälle ennen ajoa ja tarjoaa eskalaation työpöydälle. Turvallinen purku jos SoC ylikuumenee yli 46 °C.",
    read: "14 min",
  },
];

export function KnowledgeHub() {
  const [q, setQ] = useState("");

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return TOPICS;
    return TOPICS.filter(
      (t) =>
        t.title.toLowerCase().includes(needle) ||
        t.body.toLowerCase().includes(needle) ||
        t.tag.toLowerCase().includes(needle),
    );
  }, [q]);

  return (
    <section
      id="tieto"
      className="section-pad relative isolate border-t border-panel_line py-28 md:py-36"
    >
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="eyebrow mb-4">{"//"} 05 · Knowledge Hub</div>
            <h2 className="font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
              Kaiva syvemmälle.<br />
              <span className="text-accent_amber">Ei kiiltokuvia.</span>
            </h2>
          </div>
          <label className="panel flex w-full max-w-md items-center gap-3 px-4 py-3">
            <Search size={16} className="text-ink_muted" aria-hidden />
            <input
              type="search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Etsi arkkitehtuuria, promptingia, NPU-sääntöjä…"
              className="w-full bg-transparent font-mono text-[13px] text-ink_soft placeholder:text-ink_muted/60 focus:outline-none"
              aria-label="Etsi dokumentaatiosta"
            />
            <span className="hidden rounded border border-panel_line px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.22em] text-ink_muted md:inline">
              ⌘K
            </span>
          </label>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((t, i) => (
            <motion.a
              key={t.title}
              href="#lataa"
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.45, delay: i * 0.05 }}
              className="panel group flex h-full flex-col gap-4 p-6 transition hover:border-accent_amber/50 hover:shadow-amber"
            >
              <div className="flex items-center justify-between">
                <span className="eyebrow">{t.tag}</span>
                <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink_muted">
                  {t.read}
                </span>
              </div>
              <h3 className="font-display text-lg font-semibold text-ink_soft transition group-hover:text-accent_amber">
                {t.title}
              </h3>
              <p className="font-body text-[14.5px] leading-relaxed text-ink_soft/70">
                {t.body}
              </p>
              <div className="mt-auto flex items-center gap-2 border-t border-panel_line pt-4 font-mono text-[11px] uppercase tracking-[0.22em] text-accent_copper group-hover:text-accent_amber">
                <BookOpen size={13} />
                avaa luku
              </div>
            </motion.a>
          ))}
          {filtered.length === 0 && (
            <div className="panel col-span-full flex items-center justify-center px-6 py-16 text-center font-mono text-sm text-ink_muted">
              Ei osumaa. Achii ehdottaa: tarkista välilyönnit tai kokeile
              &ldquo;arkkitehtuuri&rdquo;, &ldquo;gatekeeper&rdquo;, &ldquo;gemma&rdquo;.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
