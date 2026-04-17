"use client";

import { motion } from "framer-motion";
import { ArrowRight, PlayCircle } from "lucide-react";
import Image from "next/image";

export function Hero() {
  return (
    <section
      id="filosofia"
      className="section-pad relative isolate overflow-hidden pt-40 pb-28 md:pt-48 md:pb-40"
    >
      {/* Theater light cone */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-radial-fade"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-grid-amber bg-[size:80px_80px] opacity-40"
      />

      <div className="mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="eyebrow mb-6 inline-flex items-center gap-2 rounded-full border border-accent_amber/30 bg-accent_amber/5 px-3 py-1"
          >
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent_amber" />
            <span>HARNESS_ENGINE v1.0.4-beta · The Rusty Awakening</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.05 }}
            className="font-display text-5xl font-bold leading-[1.04] tracking-tight text-ink_soft md:text-6xl lg:text-7xl"
          >
            Lopeta yappaus.<br />
            <span className="text-accent_amber text-glow-amber">Rakenna valjaat.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.12 }}
            className="mt-6 max-w-xl font-body text-lg leading-relaxed text-ink_soft/75"
          >
            Tekoäly hallusinoi, koska se on jätetty ilman arkkitehtuuria. Me
            tuomme determinismin kognitiiviseen prosessointiin. AgentDir × Achii
            on Sovereign Engine, joka asuu lokaalisti ja pakottaa suuret
            kielimallit tiukkoihin valjaisiin — .yaml on logiikka, .md on
            konteksti, ja kaikki jää sinun koneellesi.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.2 }}
            className="mt-10 flex flex-wrap items-center gap-4"
          >
            <a href="#lataa" className="copper-cta group">
              Lataa työpöytäbeta
              <ArrowRight size={18} className="transition group-hover:translate-x-0.5" />
            </a>
            <a href="#demo" className="ghost-cta group">
              <PlayCircle size={18} />
              Katso demo
            </a>
          </motion.div>

          <motion.dl
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-12 grid grid-cols-3 gap-6 border-t border-panel_line pt-8 text-left"
          >
            <div>
              <dt className="eyebrow mb-1">NPU-latenssi</dt>
              <dd className="font-display text-2xl font-semibold text-ink_soft">
                2.5<span className="text-ink_muted"> s</span>
              </dd>
            </div>
            <div>
              <dt className="eyebrow mb-1">Pilvi-egress</dt>
              <dd className="font-display text-2xl font-semibold text-ink_soft">
                0<span className="text-ink_muted"> B</span>
              </dd>
            </div>
            <div>
              <dt className="eyebrow mb-1">Hallusinaatiot</dt>
              <dd className="font-display text-2xl font-semibold text-ink_soft">
                —
              </dd>
            </div>
          </motion.dl>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="relative aspect-[4/3] w-full"
        >
          <div className="absolute inset-0 mask-radial">
            <Image
              src="/images/achii-hero.png"
              alt="Achii — kupariksi hapettunut lokaali tekoälymaskotti seisoo teatterin valokeilassa."
              fill
              priority
              className="object-cover"
              sizes="(max-width: 1024px) 100vw, 50vw"
            />
          </div>
          {/* Bezel chrome */}
          <div className="pointer-events-none absolute inset-0 rounded-2xl border border-panel_line shadow-panel" />
          {/* Status ticker */}
          <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between rounded-md border border-panel_line bg-base_bg/70 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.2em] text-ink_muted backdrop-blur-md">
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent_amber" />
              cite: status.awakening
            </span>
            <span>gemma-4b · npu</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
