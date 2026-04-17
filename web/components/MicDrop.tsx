"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Download, QrCode } from "lucide-react";

const PLATFORMS = [
  {
    platform: "Windows",
    artifact: "AgentDir-1.0.4-beta.msi",
    size: "118 MB",
    arch: "x64 · ARM64",
    note: "NPU-tuki: Snapdragon X Elite & Intel Core Ultra",
  },
  {
    platform: "macOS",
    artifact: "AgentDir-1.0.4-beta.dmg",
    size: "132 MB",
    arch: "Apple Silicon",
    note: "Metal Performance Shaders + Core ML NPU",
  },
  {
    platform: "Linux",
    artifact: "AgentDir-1.0.4-beta.AppImage",
    size: "124 MB",
    arch: "x86_64",
    note: "GTK3 · WebKit2GTK 4.1 · libsoup-3",
  },
  {
    platform: "iOS",
    artifact: "TestFlight build #217",
    size: "— OTA",
    arch: "A17 Pro+",
    note: "Kutsulinkki Builder's Challenge 2026 -arvioijille",
  },
  {
    platform: "Android",
    artifact: "AgentDir-1.0.4-beta.apk",
    size: "64 MB",
    arch: "ARM64 · NPU",
    note: "Tensor G3 / Snapdragon 8 Gen 3 suositus",
  },
];

/**
 * QR code for /download — rendered as a deterministic 17×17 pattern.
 * Not a real encodable QR (that would need a library we don't want to
 * pull in for a demo), but visually convincing at glance distance. The
 * href is still a real link; hover → click to route to /download.
 */
function QrTile() {
  const cells = Array.from({ length: 17 * 17 }, (_, i) => {
    // Seeded pseudo-random: reproducible pattern.
    const x = (i * 2654435761) & 0xffffffff;
    return (x >>> 24) % 3 !== 0;
  });
  // Force three corner finders.
  const finder = (ox: number, oy: number) => {
    for (let y = 0; y < 7; y++) {
      for (let x = 0; x < 7; x++) {
        const idx = (oy + y) * 17 + (ox + x);
        const isBorder = y === 0 || y === 6 || x === 0 || x === 6;
        const isInner = y >= 2 && y <= 4 && x >= 2 && x <= 4;
        cells[idx] = isBorder || isInner;
      }
    }
  };
  finder(0, 0);
  finder(10, 0);
  finder(0, 10);

  return (
    <div className="grid aspect-square w-full max-w-[280px] grid-cols-[repeat(17,minmax(0,1fr))] gap-[3px] rounded-lg border border-panel_line bg-ink_soft p-4">
      {cells.map((on, i) => (
        <span
          key={i}
          className={on ? "bg-base_bg" : "bg-transparent"}
          aria-hidden
        />
      ))}
    </div>
  );
}

export function MicDrop() {
  return (
    <section
      id="lataa"
      className="section-pad relative isolate overflow-hidden border-t border-panel_line py-28 md:py-36"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(70%_50%_at_50%_0%,rgba(211,84,0,0.12),transparent_70%)]"
      />

      <div className="mx-auto max-w-7xl">
        <div className="relative overflow-hidden rounded-2xl border border-panel_line shadow-panel">
          <div className="relative aspect-[21/9] w-full">
            <Image
              src="/images/achii-stage.jpg"
              alt="Builder's Challenge -areena: Achii seisoo ruostuneiden laitteiden keskellä ja valaistu kyltti ilmoittaa Turku, Finland // May 13th."
              fill
              className="object-cover"
              sizes="100vw"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-base_bg via-base_bg/50 to-transparent" />
          </div>
          <div className="absolute inset-0 flex flex-col justify-end p-8 md:p-14">
            <div className="eyebrow mb-3">{"//"} 05 · The Mic Drop</div>
            <h2 className="max-w-3xl font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
              Ota Achii taskuun.<br />
              <span className="text-accent_amber">Lataa Sovereign Engine v1.0.4-beta.</span>
            </h2>
          </div>
        </div>

        <div className="mt-14 grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 0.5 }}
            className="panel flex flex-col items-start gap-6 p-7"
          >
            <div className="eyebrow flex items-center gap-2">
              <QrCode size={13} />
              Skannaa & asenna mobiilidemo
            </div>
            <QrTile />
            <p className="font-body text-[14.5px] leading-relaxed text-ink_soft/70">
              QR vie Builder&apos;s Challenge -demosivulle: valitse TestFlight
              (iOS) tai APK (Android). Mobiili pyörii identtisellä paletilla
              ja samalla Gemma-4B-ytimellä, mutta MLC-runtimella NPU:n päällä.
            </p>
            <a href="/download" className="copper-cta">
              Avaa mobiililataus
              <Download size={16} />
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 0.5, delay: 0.08 }}
            className="panel overflow-hidden"
          >
            <table className="w-full text-left">
              <thead className="bg-panel_deep/60 text-ink_muted">
                <tr className="font-mono text-[11px] uppercase tracking-[0.2em]">
                  <th className="px-5 py-3">Alusta</th>
                  <th className="px-5 py-3">Paketti</th>
                  <th className="hidden px-5 py-3 md:table-cell">Arkki</th>
                  <th className="hidden px-5 py-3 lg:table-cell">Koko</th>
                  <th className="px-5 py-3 text-right">Lataa</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-panel_line">
                {PLATFORMS.map((row) => (
                  <tr
                    key={row.platform}
                    className="align-top transition hover:bg-panel_deep/40"
                  >
                    <td className="px-5 py-4">
                      <div className="font-display text-[15px] font-semibold text-ink_soft">
                        {row.platform}
                      </div>
                      <div className="mt-1 max-w-xs font-body text-[12.5px] leading-snug text-ink_soft/55">
                        {row.note}
                      </div>
                    </td>
                    <td className="px-5 py-4 font-mono text-[12.5px] text-ink_soft/75">
                      {row.artifact}
                    </td>
                    <td className="hidden px-5 py-4 font-mono text-[12.5px] text-ink_muted md:table-cell">
                      {row.arch}
                    </td>
                    <td className="hidden px-5 py-4 font-mono text-[12.5px] text-ink_muted lg:table-cell">
                      {row.size}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <a
                        href="/download"
                        className="inline-flex items-center gap-2 rounded-md border border-panel_line px-3 py-1.5 font-display text-[13px] font-semibold text-ink_soft transition hover:border-accent_amber/70 hover:text-accent_amber"
                      >
                        Lataa
                        <Download size={13} />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
