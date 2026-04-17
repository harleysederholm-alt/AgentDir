import { motion } from "framer-motion";
import { Play, Zap } from "lucide-react";
import { clsx } from "clsx";
import type { AppState } from "../lib/types";
import { EditorPane } from "./EditorPane";
import { PreviewPane } from "./PreviewPane";

interface Props {
  headerPath: string;
  yaml: string;
  md: string;
  appState: AppState;
  onYamlChange: (value: string) => void;
  onRunWorkflow: () => void;
}

const RUN_LABEL: Record<AppState, string> = {
  IDLE: "Run Workflow",
  PROCESSING: "Prosessoidaan…",
  SUCCESS: "Valmis ✓ — Aja uudelleen",
  ERROR: "Virhe — Yritä uudelleen",
};

export function SplitWorkspace({
  headerPath,
  yaml,
  md,
  appState,
  onYamlChange,
  onRunWorkflow,
}: Props) {
  const isBusy = appState === "PROCESSING";

  return (
    <section className="relative z-10 flex h-full flex-1 flex-col">
      {/* Header bar */}
      <header className="flex items-center justify-between border-b border-panel_oxidized/60 bg-panel_oxidized/20 px-6 py-3 backdrop-blur-md">
        <div className="flex items-center gap-3 font-heading text-sm tracking-wide text-ink_soft/90">
          <Zap size={14} className="text-accent_amber" />
          <span className="text-ink_muted">{headerPath || "docs / — / —"}</span>
        </div>
        <motion.button
          type="button"
          onClick={onRunWorkflow}
          disabled={isBusy}
          whileTap={{ scale: 0.97 }}
          className={clsx(
            "flex items-center gap-2 rounded border px-4 py-2 font-heading text-sm font-semibold tracking-wide text-white transition copper-glow",
            appState === "ERROR"
              ? "border-red-500/70 bg-red-600/80 hover:bg-red-500"
              : "border-copper_reveal/80 bg-copper_reveal shadow-copper hover:bg-accent_amber",
            isBusy && "cursor-not-allowed opacity-80",
          )}
        >
          <Play size={14} />
          {RUN_LABEL[appState]}
        </motion.button>
      </header>

      {/* Split panes */}
      <div className="grid flex-1 grid-cols-2 gap-4 px-4 py-4">
        <EditorPane
          title="valjaat · yaml"
          language="yaml"
          value={yaml}
          onChange={onYamlChange}
        />
        <PreviewPane title="konteksti · md" markdown={md} />
      </div>
    </section>
  );
}
