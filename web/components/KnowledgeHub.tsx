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
    tag: "Arkkitehtuuri",
    title: "Arkkitehtuuri — syväsukellus",
    body:
      "Tauri-shelli, Rust-portinvartija ja Python-orchestrator muodostavat kolmikerrosrakennelman. Komennot matkustavat IPC-kanavaa pitkin; tiedostojärjestelmä on scopattu .achii/ -hakemistoon; jokainen kutsu palaa tyypitettynä. Luvussa käydään läpi jokainen kerros ja sen sopimus.",
    read: "18 min",
  },
  {
    tag: "Prompting",
    title: "Prompt engineering vs. valjastaminen",
    body:
      "Prompt engineering ylläpitää mallia. Valjastaminen rakentaa sen ympärille determinismin: skema validointi, tilakoneet, pakolliset .md-kontekstit ja regex-sanitointi. Tämä dokumentti näyttää konkreettisesti miksi promptien virittely on tie tuhoon ilman valjaita.",
    read: "12 min",
  },
  {
    tag: "Suorituskyky",
    title: "NPU-optimointi Gemma 4B:lle",
    body:
      "Kvantisoinnit (q4, q8), KV-cache säännöstely, speculative decoding ja MediaPipe LLM vs. MLC:n vertailu ARM/x86-piireille. Mukana latenssiprofiili ja muistikäyttö kolmella eri laitealustalla — M3 Pro, Snapdragon X Elite ja Ryzen AI.",
    read: "22 min",
  },
  {
    tag: "Turvallisuus",
    title: "Security whitepaper",
    body:
      "Uhkamallinnus Sovereign Enginelle: local-first TOCTOU, IPC-capability-luvat, regex-pohjaisen sanitizerin rajat, pilvieskalaation hyväksyntäpolut. Sisältää tarkistuslistan auditille ja verrokit OWASP LLM Top 10 -listaan.",
    read: "26 min",
  },
  {
    tag: "Prosessi",
    title: "AgentDir-scaffoldin anatomia",
    body:
      "Miksi .achii/, docs/, Inbox/, Outbox/ ja valjaat/ on eroteltu? Mikä menee `templates/`-kansioon ja mikä `03-PRDs/`-kansioon? Käymme läpi jokaisen kansion tarkoituksen ja kirjoitamme oikean työnkulun alusta loppuun yhdessä istunnossa.",
    read: "15 min",
  },
  {
    tag: "Mobiili",
    title: "Edge AI mobiilissa: MLC & MediaPipe",
    body:
      "Miten saamme 4B-mallin pyörimään vakaasti puhelimen NPU:lla. Kulutusbudjetti, lämpötilamaksimit, haptinen palaute käyttäjälle ajon aikana, ja turvallinen purkaminen kun akku laskee alle 50 %.",
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
            <div className="eyebrow mb-4">{"//"} 04 · Knowledge Hub</div>
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
