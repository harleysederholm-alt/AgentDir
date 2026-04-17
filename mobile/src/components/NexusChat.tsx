import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { WrenchEye } from "@/components/WrenchEye";

/**
 * NexusChat — post-onboarding surface for Achii PWA.
 *
 * Intent: standard, utilitarian AI chat UI (Perplexity / Claude / ChatGPT
 * mobile). No marketing copy, no status cards, no hero — just a conversation.
 *
 * Layout:
 *   [Top bar]   menu · Achii / Gemma 4B · new chat
 *   [Messages]  threaded bubbles (user right, Achii left)
 *   [Composer]  attach · textarea · send
 *   [Sidebar]   drawer from left — history + settings
 */

type Role = "user" | "achii";
type SendState = "idle" | "thinking";

interface Msg {
  id: number;
  role: Role;
  body: string;
  ts: string;
}

interface Thread {
  id: string;
  title: string;
  createdAt: number;
  messages: Msg[];
}

const HISTORY_KEY = "achii:threads_v1";
const ACTIVE_KEY = "achii:active_thread_v1";

const ACHII_REPLIES = [
  "Selvä. Gatekeeper sanitoi syötteen ensin, sitten Gemma 4B ajaa valjaat. Ei tavua egressiä.",
  "Löysin .md-kontekstistasi 3 ristiriitaa. Korjaanko ne ennen kuin vastaan?",
  "Deterministinen polku valittu. Aika-arvio: ~2.5 s NPU:lla.",
  "Konteksti puuttuu. Liitä .md-tiedosto tai anna avainsana, niin hain paikallisesta muistista.",
  "Tallensin tämän istunnon lokaalisti: /memory/session.md. Pilveä ei koskettu.",
  "Isäntä, tämä pyyntö hyppäisi sandboxin ulkopuolelle. En tee sitä ilman uutta valjasta.",
];

function nowStamp(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function uid(): string {
  return `t_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

function freshThread(): Thread {
  return {
    id: uid(),
    title: "Uusi keskustelu",
    createdAt: Date.now(),
    messages: [
      {
        id: 1,
        role: "achii",
        body:
          "Isäntä. Heräsin taskussa, NPU lämmin, Gemma 4B lokaalisti. Kerro mitä valjastetaan.",
        ts: nowStamp(),
      },
    ],
  };
}

function loadThreads(): Thread[] {
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed as Thread[];
  } catch {
    return [];
  }
}

function saveThreads(threads: Thread[]): void {
  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(threads));
  } catch {
    /* private mode / quota — fail silently */
  }
}

function loadActiveId(): string | null {
  try {
    return window.localStorage.getItem(ACTIVE_KEY);
  } catch {
    return null;
  }
}

function saveActiveId(id: string): void {
  try {
    window.localStorage.setItem(ACTIVE_KEY, id);
  } catch {
    /* noop */
  }
}

function haptic(ms: number | number[]): void {
  const nav = window.navigator as Navigator & {
    vibrate?: (p: number | number[]) => boolean;
  };
  if (typeof nav.vibrate === "function") nav.vibrate(ms);
}

/* ─────────────────────────────── component ─────────────────────────────── */

export function NexusChat() {
  const [threads, setThreads] = useState<Thread[]>(() => {
    const loaded = loadThreads();
    if (loaded.length > 0) return loaded;
    const seed = [freshThread()];
    saveThreads(seed);
    return seed;
  });
  const [activeId, setActiveId] = useState<string>(() => {
    const existing = loadActiveId();
    if (existing) return existing;
    return threads[0]?.id ?? "";
  });
  const [draft, setDraft] = useState("");
  const [sendState, setSendState] = useState<SendState>("idle");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const scrollerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const msgCounterRef = useRef<number>(1);
  const timersRef = useRef<number[]>([]);

  const activeThread = useMemo<Thread | undefined>(
    () => threads.find((t) => t.id === activeId),
    [threads, activeId],
  );

  // Persist threads + active id whenever they change.
  useEffect(() => {
    saveThreads(threads);
  }, [threads]);

  useEffect(() => {
    if (activeId) saveActiveId(activeId);
  }, [activeId]);

  // Keep counter ahead of the highest-known message id.
  useEffect(() => {
    const max = threads.reduce(
      (acc, t) => Math.max(acc, ...t.messages.map((m) => m.id)),
      0,
    );
    msgCounterRef.current = max;
  }, [threads]);

  // Autoscroll the messages pane to the bottom on new messages or state change.
  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [activeThread?.messages.length, sendState, activeId]);

  // Auto-grow the composer textarea (max 6 rows).
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    const MAX = 168; // ~6 rows @ 28px line height
    el.style.height = `${Math.min(el.scrollHeight, MAX)}px`;
  }, [draft]);

  // Clean up any pending timers on unmount.
  useEffect(() => {
    return () => {
      timersRef.current.forEach(window.clearTimeout);
      timersRef.current = [];
    };
  }, []);

  const canSend = draft.trim().length > 0 && sendState === "idle";

  const appendMessage = useCallback(
    (threadId: string, msg: Msg, titleIfFirst?: string) => {
      setThreads((prev) =>
        prev.map((t) => {
          if (t.id !== threadId) return t;
          const firstUser =
            titleIfFirst &&
            !t.messages.some((m) => m.role === "user") &&
            msg.role === "user";
          return {
            ...t,
            title: firstUser ? titleIfFirst : t.title,
            messages: [...t.messages, msg],
          };
        }),
      );
    },
    [],
  );

  const send = useCallback(() => {
    if (!canSend || !activeThread) return;
    const body = draft.trim();
    msgCounterRef.current += 1;
    const userMsg: Msg = {
      id: msgCounterRef.current,
      role: "user",
      body,
      ts: nowStamp(),
    };
    appendMessage(
      activeThread.id,
      userMsg,
      body.length > 42 ? `${body.slice(0, 42)}…` : body,
    );
    setDraft("");
    setSendState("thinking");
    haptic([4, 8, 14]);

    const replyIdx = msgCounterRef.current % ACHII_REPLIES.length;
    const reply = ACHII_REPLIES[replyIdx] ?? ACHII_REPLIES[0]!;

    const t = window.setTimeout(() => {
      msgCounterRef.current += 1;
      const achiiMsg: Msg = {
        id: msgCounterRef.current,
        role: "achii",
        body: reply,
        ts: nowStamp(),
      };
      appendMessage(activeThread.id, achiiMsg);
      setSendState("idle");
      haptic(8);
    }, 1400);
    timersRef.current.push(t);
  }, [activeThread, appendMessage, canSend, draft]);

  const newThread = useCallback(() => {
    const t = freshThread();
    setThreads((prev) => [t, ...prev]);
    setActiveId(t.id);
    setDrawerOpen(false);
    setDraft("");
    setSendState("idle");
  }, []);

  const pickThread = useCallback((id: string) => {
    setActiveId(id);
    setDrawerOpen(false);
  }, []);

  const deleteThread = useCallback(
    (id: string) => {
      setThreads((prev) => {
        const next = prev.filter((t) => t.id !== id);
        if (next.length === 0) {
          const seed = freshThread();
          setActiveId(seed.id);
          return [seed];
        }
        if (id === activeId && next[0]) {
          setActiveId(next[0].id);
        }
        return next;
      });
    },
    [activeId],
  );

  const clearAll = useCallback(() => {
    const seed = freshThread();
    setThreads([seed]);
    setActiveId(seed.id);
    setSettingsOpen(false);
  }, []);

  const grouped = useMemo(() => {
    const today: Thread[] = [];
    const earlier: Thread[] = [];
    const startOfToday = new Date();
    startOfToday.setHours(0, 0, 0, 0);
    const ms = startOfToday.getTime();
    for (const t of threads) {
      (t.createdAt >= ms ? today : earlier).push(t);
    }
    return { today, earlier };
  }, [threads]);

  const messages = activeThread?.messages ?? [];

  return (
    <div className="nexus-shell">
      {/* TOP BAR */}
      <header className="nexus-topbar">
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          aria-label="Avaa keskusteluhistoria"
          className="nexus-iconbtn"
        >
          <MenuIcon />
        </button>
        <div className="flex min-w-0 items-center gap-2">
          <WrenchEye className="h-6 w-6 shrink-0" />
          <div className="min-w-0 leading-tight">
            <div className="truncate font-display text-sm font-semibold text-ink_soft">
              Achii
            </div>
            <div className="truncate font-mono text-[10px] uppercase tracking-[0.18em] text-ink_muted">
              Gemma 4B · lokaali
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={newThread}
          aria-label="Uusi keskustelu"
          className="nexus-iconbtn"
        >
          <PlusIcon />
        </button>
      </header>

      {/* MESSAGES */}
      <div ref={scrollerRef} className="nexus-messages">
        <div className="mx-auto w-full max-w-2xl px-4 py-6">
          {messages.length === 0 && (
            <div className="py-10 text-center font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
              Tyhjä valjas-istunto. Aloita syöttämällä tehtävä alas.
            </div>
          )}
          {messages.map((m) => (
            <MessageRow key={m.id} msg={m} />
          ))}
          {sendState === "thinking" && <ThinkingRow />}
        </div>
      </div>

      {/* COMPOSER */}
      <div className="nexus-composer">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
          className="mx-auto flex w-full max-w-2xl items-end gap-2 px-3 py-3"
        >
          <button
            type="button"
            aria-label="Liitä tiedosto"
            className="nexus-iconbtn"
            onClick={() => {
              /* placeholder: attach .md / .yaml files would plug in here */
            }}
          >
            <PaperclipIcon />
          </button>
          <div className="nexus-input-wrap">
            <textarea
              ref={textareaRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              placeholder="Kysy Achiilta…"
              rows={1}
              className="nexus-textarea"
            />
          </div>
          <button
            type="submit"
            aria-label="Lähetä"
            disabled={!canSend}
            className={`nexus-sendbtn ${canSend ? "" : "opacity-40"}`}
          >
            <SendIcon />
          </button>
        </form>
        <div className="pb-2 text-center font-mono text-[9.5px] uppercase tracking-[0.22em] text-ink_dim">
          gatekeeper · on · egress · 0 B
        </div>
      </div>

      {/* SIDEBAR DRAWER */}
      {drawerOpen && (
        <div
          role="dialog"
          aria-label="Keskusteluhistoria"
          className="fixed inset-0 z-50 flex"
        >
          <button
            type="button"
            aria-label="Sulje valikko"
            onClick={() => setDrawerOpen(false)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />
          <aside className="nexus-drawer">
            <div className="flex items-center justify-between px-4 pt-4 pb-2">
              <div className="flex items-center gap-2">
                <WrenchEye className="h-5 w-5" />
                <span className="font-display text-sm font-semibold text-ink_soft">
                  Achii
                </span>
              </div>
              <button
                type="button"
                aria-label="Sulje"
                onClick={() => setDrawerOpen(false)}
                className="nexus-iconbtn"
              >
                <CloseIcon />
              </button>
            </div>
            <button
              type="button"
              onClick={newThread}
              className="mx-4 mt-2 flex items-center justify-center gap-2 rounded-lg border border-accent_amber/30 bg-accent_amber/10 px-3 py-2.5 font-display text-sm font-medium text-accent_amber transition hover:bg-accent_amber/20"
            >
              <PlusIcon /> Uusi keskustelu
            </button>

            <nav className="mt-4 flex-1 overflow-y-auto px-2 pb-4">
              {grouped.today.length > 0 && (
                <ThreadGroup
                  label="Tänään"
                  items={grouped.today}
                  activeId={activeId}
                  onPick={pickThread}
                  onDelete={deleteThread}
                />
              )}
              {grouped.earlier.length > 0 && (
                <ThreadGroup
                  label="Aiemmin"
                  items={grouped.earlier}
                  activeId={activeId}
                  onPick={pickThread}
                  onDelete={deleteThread}
                />
              )}
              {threads.length === 0 && (
                <div className="px-2 py-4 font-mono text-[10.5px] uppercase tracking-[0.2em] text-ink_dim">
                  Ei historiaa
                </div>
              )}
            </nav>

            <div className="border-t border-panel_line px-2 py-3">
              <button
                type="button"
                onClick={() => setSettingsOpen(true)}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left font-body text-sm text-ink_soft transition hover:bg-white/5"
              >
                <SettingsIcon /> Asetukset
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* SETTINGS MODAL */}
      {settingsOpen && (
        <div
          role="dialog"
          aria-label="Asetukset"
          className="fixed inset-0 z-[60] flex items-end justify-center sm:items-center"
        >
          <button
            type="button"
            aria-label="Sulje asetukset"
            onClick={() => setSettingsOpen(false)}
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          />
          <div className="nexus-sheet">
            <div className="flex items-center justify-between px-5 pt-4 pb-2">
              <div className="font-display text-base font-semibold text-ink_soft">
                Asetukset
              </div>
              <button
                type="button"
                aria-label="Sulje"
                onClick={() => setSettingsOpen(false)}
                className="nexus-iconbtn"
              >
                <CloseIcon />
              </button>
            </div>
            <dl className="space-y-3 px-5 py-3 font-mono text-[11px] uppercase tracking-[0.18em]">
              <Row k="Malli" v="Gemma 4B · Q4_K_M" />
              <Row k="Gatekeeper" v="ON · Rust" />
              <Row k="Konteksti" v=".yaml + .md (lokaali)" />
              <Row k="Egress" v="0 B" />
              <Row k="Muisti" v="Lokaali · vektoritöntä" />
              <Row k="Versio" v="v1.0.4-beta" />
            </dl>
            <div className="px-5 pt-1 pb-5">
              <button
                type="button"
                onClick={clearAll}
                className="w-full rounded-lg border border-accent_copper/40 bg-accent_copper/10 px-3 py-2.5 font-display text-sm text-accent_copper_warm transition hover:bg-accent_copper/20"
              >
                Tyhjennä kaikki keskustelut
              </button>
              <p className="mt-2 text-center font-mono text-[10px] uppercase tracking-[0.22em] text-ink_dim">
                data tallennettu vain tälle laitteelle
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ───────────────────────────── sub-components ──────────────────────────── */

function MessageRow({ msg }: { msg: Msg }) {
  if (msg.role === "user") {
    return (
      <div className="mb-4 flex justify-end">
        <div className="user-bubble">
          <p className="whitespace-pre-wrap break-words text-[15px] leading-relaxed text-ink_soft">
            {msg.body}
          </p>
        </div>
      </div>
    );
  }
  return (
    <div className="mb-5 flex gap-3">
      <WrenchEye className="mt-0.5 h-6 w-6 shrink-0" />
      <div className="min-w-0 flex-1">
        <div className="mb-1 font-mono text-[10px] uppercase tracking-[0.22em] text-accent_amber/80">
          Achii · {msg.ts}
        </div>
        <p className="whitespace-pre-wrap break-words text-[15px] leading-relaxed text-ink_soft">
          {msg.body}
        </p>
      </div>
    </div>
  );
}

function ThinkingRow() {
  return (
    <div className="mb-5 flex gap-3" aria-live="polite">
      <WrenchEye className="mt-0.5 h-6 w-6 shrink-0 animate-pulse-amber" />
      <div className="min-w-0 flex-1 pt-0.5">
        <div className="mb-1 font-mono text-[10px] uppercase tracking-[0.22em] text-accent_amber/80">
          Achii · prosessoi
        </div>
        <div className="flex items-center gap-1">
          <Dot />
          <Dot delay={0.18} />
          <Dot delay={0.36} />
        </div>
      </div>
    </div>
  );
}

function Dot({ delay = 0 }: { delay?: number }) {
  return (
    <span
      className="inline-block h-1.5 w-1.5 rounded-full bg-ink_muted"
      style={{ animation: `caret 1.2s ${delay}s infinite` }}
    />
  );
}

function ThreadGroup({
  label,
  items,
  activeId,
  onPick,
  onDelete,
}: {
  label: string;
  items: Thread[];
  activeId: string;
  onPick: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div className="mb-4">
      <div className="px-2 pb-1.5 font-mono text-[9.5px] uppercase tracking-[0.22em] text-ink_dim">
        {label}
      </div>
      <ul className="space-y-0.5">
        {items.map((t) => {
          const active = t.id === activeId;
          return (
            <li key={t.id} className="group relative">
              <button
                type="button"
                onClick={() => onPick(t.id)}
                className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 pr-9 text-left text-sm transition ${
                  active
                    ? "bg-white/10 text-ink_soft"
                    : "text-ink_soft/80 hover:bg-white/5"
                }`}
              >
                <ChatIcon />
                <span className="truncate">{t.title}</span>
              </button>
              <button
                type="button"
                onClick={() => onDelete(t.id)}
                aria-label="Poista keskustelu"
                className="absolute right-1.5 top-1.5 rounded-md p-1.5 text-ink_dim opacity-0 transition hover:bg-white/5 hover:text-accent_copper_warm group-hover:opacity-100 focus:opacity-100"
              >
                <TrashIcon />
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between rounded-md bg-white/5 px-3 py-2">
      <dt className="text-ink_muted">{k}</dt>
      <dd className="text-ink_soft">{v}</dd>
    </div>
  );
}

/* ──────────────────────────────── icons ────────────────────────────────── */

function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" width={20} height={20} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" aria-hidden>
      <line x1="4" y1="7" x2="20" y2="7" />
      <line x1="4" y1="12" x2="20" y2="12" />
      <line x1="4" y1="17" x2="20" y2="17" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg viewBox="0 0 24 24" width={20} height={20} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" aria-hidden>
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" width={20} height={20} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" aria-hidden>
      <line x1="6" y1="6" x2="18" y2="18" />
      <line x1="18" y1="6" x2="6" y2="18" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" width={18} height={18} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M5 12l14-7-3 14-4-5-7-2z" />
    </svg>
  );
}

function PaperclipIcon() {
  return (
    <svg viewBox="0 0 24 24" width={18} height={18} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 11.5l-8.1 8.1a5 5 0 0 1-7.1-7.1L14.5 4A3.5 3.5 0 0 1 19.5 9l-8.4 8.4a2 2 0 1 1-2.8-2.8l7.4-7.4" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg viewBox="0 0 24 24" width={18} height={18} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.7 1.7 0 0 0 .4 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.4 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.4l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .4-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.4-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.4H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.4l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.4 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg viewBox="0 0 24 24" width={15} height={15} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" width={14} height={14} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6" />
      <path d="M14 11v6" />
    </svg>
  );
}
