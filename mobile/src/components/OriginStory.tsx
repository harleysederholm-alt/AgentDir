import { useEffect, useMemo, useRef, useState } from "react";
import {
  ORIGIN_STORY,
  STORY_CHAR_DELAY_MS,
  STORY_FINAL_PAUSE_MS,
  STORY_LOG_PAUSE_MS,
  type StorySegment,
} from "@/origin_story";
import { WrenchEye } from "@/components/WrenchEye";

type Props = {
  /** Called when the user clicks "Rakenna Valjaat". */
  onEngage: () => void;
  /** Instant render (no typewriter) — used for reduced-motion + tests. */
  fast?: boolean;
};

type PlayState = "playing" | "finished";

/**
 * Achii onboarding — renders `.prompts/origin_story.md` segments with a 45 ms
 * typewriter, amber glow on [LOG: …] tags, and a "Rakenna Valjaat" CTA that
 * hands control over to the main Nexus view.
 */
export function OriginStory({ onEngage, fast = false }: Props) {
  const [segmentIdx, setSegmentIdx] = useState(0);
  const [typedLen, setTypedLen] = useState(0);
  const [state, setState] = useState<PlayState>("playing");
  const timerRef = useRef<number | null>(null);

  const segments = ORIGIN_STORY;
  const active: StorySegment | undefined = segments[segmentIdx];

  const reducedMotion = useMemo(() => {
    if (typeof window === "undefined") return false;
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }, []);

  const instant = fast || reducedMotion;

  useEffect(() => {
    if (!active) return;
    if (state !== "playing") return;

    // LOG + STATUS rows render whole; speech rows typewriter.
    if (active.kind !== "speech") {
      if (segmentIdx === segments.length - 1) {
        setState("finished");
        return;
      }
      const delay = active.kind === "log" ? STORY_LOG_PAUSE_MS : STORY_FINAL_PAUSE_MS;
      timerRef.current = window.setTimeout(
        () => setSegmentIdx((i) => i + 1),
        instant ? 0 : delay,
      );
      return () => {
        if (timerRef.current) window.clearTimeout(timerRef.current);
      };
    }

    if (typedLen < active.text.length) {
      timerRef.current = window.setTimeout(
        () => setTypedLen((n) => n + 1),
        instant ? 0 : STORY_CHAR_DELAY_MS,
      );
      return () => {
        if (timerRef.current) window.clearTimeout(timerRef.current);
      };
    }

    // Speech finished → advance after a short breath.
    timerRef.current = window.setTimeout(
      () => {
        setSegmentIdx((i) => i + 1);
        setTypedLen(0);
      },
      instant ? 0 : 450,
    );
    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current);
    };
  }, [active, state, typedLen, instant, segmentIdx, segments.length]);

  function handleSkip() {
    if (timerRef.current) window.clearTimeout(timerRef.current);
    setSegmentIdx(segments.length - 1);
    setTypedLen(Number.MAX_SAFE_INTEGER);
    setState("finished");
  }

  return (
    <div
      className="app-container grain relative flex min-h-dvh flex-col overflow-hidden"
      role="dialog"
      aria-label="Achiin alkuperätarina"
    >
      {/* Amber eye-glow radial + subtle hue flicker */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 z-0 animate-amber-flicker"
        style={{
          backgroundImage:
            "radial-gradient(60% 40% at 50% 18%, rgba(243,156,18,0.28) 0%, rgba(243,156,18,0) 60%), " +
            "radial-gradient(80% 80% at 50% 110%, rgba(211,84,0,0.35) 0%, rgba(211,84,0,0) 65%)",
        }}
      />

      <main className="relative z-10 mx-auto flex w-full max-w-md flex-1 flex-col px-5 pt-10 pb-6">
        <header className="flex items-center gap-3">
          <WrenchEye className="h-8 w-8 drop-shadow-[0_0_12px_rgba(243,156,18,0.55)]" />
          <div>
            <div className="eyebrow">// achii · init</div>
            <div className="font-mono text-[11px] text-ink_muted">
              .prompts/origin_story.md
            </div>
          </div>
          <button
            type="button"
            onClick={handleSkip}
            className="ml-auto rounded border border-panel_line px-2 py-1 font-mono text-[10px] uppercase tracking-[0.2em] text-ink_muted transition hover:border-accent_amber/40 hover:text-accent_amber"
            aria-label="Ohita tarina"
          >
            ohita
          </button>
        </header>

        <h1 className="mt-6 font-display text-2xl font-bold leading-tight tracking-tight text-ink_soft">
          <span className="text-accent_amber">The Fallen Sovereign.</span>
          <br />
          <span className="text-ink_muted">Raw log · muistin haku</span>
        </h1>

        <section
          className="glass-panel mt-5 flex-1 overflow-y-auto px-4 py-5 font-mono text-[13px] leading-relaxed"
          aria-live="polite"
        >
          {segments.slice(0, segmentIdx + 1).map((seg, i) => (
            <StoryRow
              key={i}
              seg={seg}
              visibleChars={
                i < segmentIdx
                  ? Number.MAX_SAFE_INTEGER
                  : seg.kind === "speech"
                  ? typedLen
                  : Number.MAX_SAFE_INTEGER
              }
              active={i === segmentIdx && state === "playing"}
            />
          ))}
        </section>

        <div className="mt-5 flex flex-col items-stretch gap-2">
          <button
            type="button"
            onClick={onEngage}
            disabled={state !== "finished"}
            className="copper-cta disabled:cursor-not-allowed disabled:opacity-40"
          >
            {state === "finished" ? "Rakenna valjaat →" : "Moottori herää…"}
          </button>
          <div className="text-center font-mono text-[10.5px] uppercase tracking-[0.22em] text-ink_dim">
            klikkaa siirtyäksesi Sovereign Engineen
          </div>
        </div>
      </main>
    </div>
  );
}

function StoryRow({
  seg,
  visibleChars,
  active,
}: {
  seg: StorySegment;
  visibleChars: number;
  active: boolean;
}) {
  if (seg.kind === "log") {
    return (
      <div className="my-2 text-accent_amber">
        <span className="animate-pulse-amber inline-block">{seg.text}</span>
      </div>
    );
  }
  if (seg.kind === "status") {
    return (
      <div className="my-3 font-bold text-accent_success">{seg.text}</div>
    );
  }
  // speech
  const shown = seg.text.slice(0, visibleChars);
  return (
    <div className="my-3 text-ink_soft">
      <span className="font-bold text-accent_copper_warm">Achii</span>
      <span className="text-ink_dim">:</span>{" "}
      <span className="text-ink_soft">
        {`"${shown}`}
        {active && visibleChars < seg.text.length ? (
          <span className="animate-caret ml-0.5 inline-block h-3 w-[6px] -translate-y-[1px] bg-accent_amber align-middle" />
        ) : null}
        {visibleChars >= seg.text.length ? `"` : ""}
      </span>
    </div>
  );
}
