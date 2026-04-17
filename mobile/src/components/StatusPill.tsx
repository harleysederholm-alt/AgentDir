import type { ReactNode } from "react";

type Tone = "amber" | "copper" | "success" | "muted";

const TONE_MAP: Record<Tone, string> = {
  amber: "border-accent_amber/40 bg-accent_amber/10 text-accent_amber",
  copper: "border-accent_copper/40 bg-accent_copper/10 text-accent_copper_warm",
  success: "border-accent_success/40 bg-accent_success/10 text-accent_success",
  muted: "border-panel_line bg-white/5 text-ink_muted"
};

export function StatusPill({
  tone = "amber",
  children,
  dot = true
}: {
  tone?: Tone;
  children: ReactNode;
  dot?: boolean;
}) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 font-mono text-[10.5px] uppercase tracking-[0.2em] backdrop-blur-md ${TONE_MAP[tone]}`}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" />}
      {children}
    </span>
  );
}
