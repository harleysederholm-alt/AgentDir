"use client";

import { useEffect, useRef, useState } from "react";

const LINES = [
  { prompt: "$", text: "achii scan ~/Documents/AgentDir", color: "ink" },
  { prompt: ">", text: "Käynnistetään lokaali gatekeeper…", color: "muted" },
  { prompt: ">", text: "Ladataan Gemma-4B NPU-kontekstiin (quant: q4)…", color: "muted" },
  { prompt: ">", text: "Skannataan .yaml × 7 · .md × 14 · .inbox × 3", color: "muted" },
  { prompt: "!", text: "VAROITUS: löytyi 14 järjestämätöntä .md-tiedostoa.", color: "amber" },
  { prompt: "!", text: "Isäntä, mä en ole onnellinen. Mä tarvitsen jäsentelyä.", color: "amber" },
  { prompt: ">", text: "Ehdotan: luo docs/03-PRDs ja docs/04-Notes.", color: "muted" },
  { prompt: "?", text: "Odotan lupaa: aloitetaanko refaktori? [y/N]", color: "copper" },
] as const;

const COLOR_CLASS: Record<string, string> = {
  ink: "text-ink_soft",
  muted: "text-ink_soft/60",
  amber: "text-accent_amber",
  copper: "text-accent_copper",
};

/**
 * Animated CLI that simulates Achii's internal monologue. Runs once per mount —
 * no infinite loop. When the last line finishes the caret keeps blinking but
 * nothing else advances; refreshing the page re-runs it.
 */
export function SystemOverrideTerminal() {
  const [lineIdx, setLineIdx] = useState(0);
  const [charIdx, setCharIdx] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (lineIdx >= LINES.length) return;
    const line = LINES[lineIdx];
    if (charIdx < line.text.length) {
      const t = window.setTimeout(() => setCharIdx((c) => c + 1), 22);
      return () => window.clearTimeout(t);
    }
    // Finished current line, pause, then advance.
    const pause = window.setTimeout(() => {
      setLineIdx((i) => i + 1);
      setCharIdx(0);
    }, 480);
    return () => window.clearTimeout(pause);
  }, [lineIdx, charIdx]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [lineIdx, charIdx]);

  return (
    <div className="panel overflow-hidden">
      <div className="flex items-center justify-between border-b border-panel_line bg-panel_deep/60 px-4 py-2">
        <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
          <span className="h-2 w-2 rounded-full bg-accent_error/70" />
          <span className="h-2 w-2 rounded-full bg-accent_amber/70" />
          <span className="h-2 w-2 rounded-full bg-accent_success/70" />
          <span className="ml-3">system_override :: achii@local</span>
        </div>
        <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-accent_amber">
          live
        </span>
      </div>

      <div
        ref={scrollRef}
        className="max-h-[340px] overflow-y-auto bg-panel_fill/70 px-5 py-4 font-mono text-[13px] leading-relaxed"
      >
        {LINES.slice(0, lineIdx).map((line, i) => (
          <div key={i} className="flex gap-3">
            <span className="select-none text-ink_dim">{line.prompt}</span>
            <span className={COLOR_CLASS[line.color]}>{line.text}</span>
          </div>
        ))}
        {lineIdx < LINES.length && (
          <div className="flex gap-3">
            <span className="select-none text-ink_dim">{LINES[lineIdx].prompt}</span>
            <span className={COLOR_CLASS[LINES[lineIdx].color]}>
              {LINES[lineIdx].text.slice(0, charIdx)}
              <span className="ml-0.5 inline-block h-4 w-[7px] -mb-[2px] animate-caret bg-accent_amber align-middle" />
            </span>
          </div>
        )}
        {lineIdx >= LINES.length && (
          <div className="mt-3 flex gap-3 text-ink_dim">
            <span className="select-none">$</span>
            <span className="inline-block h-4 w-[7px] animate-caret bg-accent_amber" />
          </div>
        )}
      </div>
    </div>
  );
}
