"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { PlayCircle } from "lucide-react";

/**
 * Veo 3.1 intro-video placeholder. When the final render is ready, swap the
 * <Image> for a <video autoPlay muted playsInline loop> with the same class
 * names — the radial mask frames both identically.
 */
export function VideoShowcase() {
  return (
    <section
      id="demo"
      className="section-pad relative isolate border-t border-panel_line py-24 md:py-32"
    >
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
          <div>
            <div className="eyebrow mb-3">{"//"} demo · Veo 3.1 intro reel</div>
            <h2 className="font-display text-3xl font-bold leading-tight text-ink_soft md:text-4xl">
              45 sekunnissa valjaisiin.
            </h2>
          </div>
          <p className="max-w-md font-body text-sm leading-relaxed text-ink_soft/65">
            Työpöytäkuva, puhelinkuva, Achii herätetään. Ei chat-kuplaa, ei
            loading-spinneriä, vain yksi deterministinen ajo.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, amount: 0.35 }}
          transition={{ duration: 0.6 }}
          className="relative mt-10 aspect-video overflow-hidden rounded-2xl border border-panel_line shadow-panel"
        >
          <div className="absolute inset-0 mask-radial">
            <Image
              src="/images/achii-workbench.jpg"
              alt="Työpöytä, jossa Achiin työkalut, Arduino, ruostunut muki ja muistilehtiö lukee: AgentDir korjauslista."
              fill
              className="object-cover"
              sizes="100vw"
            />
          </div>
          <button
            type="button"
            className="absolute inset-0 m-auto grid h-20 w-20 place-items-center rounded-full border border-accent_amber/50 bg-base_bg/60 backdrop-blur-md transition hover:scale-105 hover:border-accent_amber"
            aria-label="Toista intro-video"
          >
            <PlayCircle size={36} className="text-accent_amber" />
          </button>
          <div className="pointer-events-none absolute bottom-4 left-4 right-4 flex items-center justify-between rounded-md border border-panel_line bg-base_bg/70 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted backdrop-blur-md">
            <span>intro · 00:45</span>
            <span>veo 3.1 · 4k · hdr</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
