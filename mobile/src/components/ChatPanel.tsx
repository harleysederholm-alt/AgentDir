import { useEffect, useMemo, useRef, useState } from "react";
import { StatusPill } from "@/components/StatusPill";

type Role = "isäntä" | "achii";
type State = "IDLE" | "PROCESSING" | "DONE" | "ERROR";

interface Msg {
  id: number;
  role: Role;
  body: string;
  ts: string;
}

const INITIAL: Msg[] = [
  {
    id: 1,
    role: "achii",
    body:
      "Isäntä, heräsin taskussa. NPU lämpenee, Gemma 4B ladattu lokaalisti. Kerro mitä valjastetaan — pidän sinut ruodussa.",
    ts: "07:02"
  }
];

const ACHII_REPLIES: string[] = [
  "Valjas vastaanotettu. Gatekeeper sanitoi syötteen ennen inferenssiä. Ei tavua egressiä.",
  "Kontekstisi ei ole järjestyksessä — löysin 14 järjestelemätöntä .md-tiedostoa. Korjaanko ennen ajoa?",
  "Deterministinen polku valittu. Gemma 4B (Q4_K_M) · 2.5 s kohdelatenssi · NPU ON.",
  "Muistutus: akku 42 %. Ajo onnistuu, mutta latauksen jälkeen järjestelen postilaatikkosi uudelleen.",
  "Yhteenveto tallennettu lokaalisti: /memory/session_042.md. Pilveä ei koskettu kertaakaan."
];

function haptic(ms: number | number[]) {
  if (typeof window === "undefined") return;
  const nav = window.navigator as Navigator & { vibrate?: (p: number | number[]) => boolean };
  if (typeof nav.vibrate === "function") nav.vibrate(ms);
}

export function ChatPanel() {
  const [msgs, setMsgs] = useState<Msg[]>(INITIAL);
  const [draft, setDraft] = useState("");
  const [state, setState] = useState<State>("IDLE");
  const timers = useRef<number[]>([]);
  const scrollerRef = useRef<HTMLDivElement>(null);
  const counterRef = useRef<number>(INITIAL.length);

  useEffect(() => {
    return () => {
      timers.current.forEach(window.clearTimeout);
      timers.current = [];
    };
  }, []);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
  }, [msgs, state]);

  const canSend = useMemo(() => draft.trim().length > 0 && state !== "PROCESSING", [draft, state]);

  function nextId() {
    counterRef.current += 1;
    return counterRef.current;
  }

  function pickReply(n: number): string {
    const reply = ACHII_REPLIES[n % ACHII_REPLIES.length];
    return reply ?? ACHII_REPLIES[0]!;
  }

  function nowStamp(): string {
    const d = new Date();
    return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  }

  function send() {
    if (!canSend) return;
    const isannat: Msg = { id: nextId(), role: "isäntä", body: draft.trim(), ts: nowStamp() };
    setMsgs((m) => [...m, isannat]);
    setDraft("");
    setState("PROCESSING");
    haptic([6, 10, 18]);

    const t1 = window.setTimeout(() => {
      const reply: Msg = {
        id: nextId(),
        role: "achii",
        body: pickReply(isannat.id),
        ts: nowStamp()
      };
      setMsgs((m) => [...m, reply]);
      setState("DONE");
      haptic(10);
    }, 2500);

    const t2 = window.setTimeout(() => setState("IDLE"), 6800);
    timers.current.push(t1, t2);
  }

  return (
    <section className="glass-panel grain relative mt-4 flex flex-col gap-3 p-4">
      <header className="flex items-center justify-between">
        <div>
          <div className="eyebrow">// chat · lokaali inferenssi</div>
          <h2 className="mt-1 font-display text-base font-semibold text-ink_soft">
            Valjas-istunto
          </h2>
        </div>
        <StatusPill
          tone={state === "PROCESSING" ? "amber" : state === "ERROR" ? "copper" : state === "DONE" ? "success" : "muted"}
        >
          {state.toLowerCase()}
        </StatusPill>
      </header>

      <div
        ref={scrollerRef}
        className="max-h-[42vh] min-h-[220px] space-y-3 overflow-y-auto pr-1"
      >
        {msgs.map((m) => (
          <div
            key={m.id}
            className={
              m.role === "achii"
                ? "chat-bubble chat-bubble-achii"
                : "chat-bubble ml-8 border-accent_copper/25 bg-accent_copper/10"
            }
          >
            <div className="mb-1 flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.2em] text-ink_muted">
              <span>{m.role}</span>
              <span>{m.ts}</span>
            </div>
            <p className="text-sm leading-relaxed text-ink_soft">{m.body}</p>
          </div>
        ))}
        {state === "PROCESSING" && (
          <div className="chat-bubble chat-bubble-achii">
            <div className="mb-1 font-mono text-[10px] uppercase tracking-[0.2em] text-accent_amber/80">
              achii · prosessoi
            </div>
            <p className="text-sm text-ink_soft">
              Syöte gatekeeper-putkessa
              <span className="ml-1 inline-block animate-caret">_</span>
            </p>
          </div>
        )}
      </div>

      <div className="flex items-end gap-2 pt-1">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          placeholder="Syötä tehtäväsi Achiille — enter ajaa, shift+enter rivittää…"
          className="min-h-[60px] flex-1 resize-none rounded-lg border border-panel_line bg-base_bg/70 px-3 py-2 font-body text-sm leading-relaxed text-ink_soft placeholder:text-ink_dim focus:border-accent_amber/60 focus:outline-none"
          rows={2}
        />
        <button
          type="button"
          onClick={send}
          disabled={!canSend}
          className="copper-cta h-[60px] min-w-[112px] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {state === "PROCESSING" ? "ajossa…" : "aja valjas"}
        </button>
      </div>

      <div className="flex items-center justify-between font-mono text-[10.5px] uppercase tracking-[0.22em] text-ink_muted">
        <span>gemma 4b · q4_k_m</span>
        <span>gatekeeper · ON</span>
        <span>egress · 0 B</span>
      </div>
    </section>
  );
}
