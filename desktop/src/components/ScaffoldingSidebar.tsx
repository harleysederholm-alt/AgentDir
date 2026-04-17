import { clsx } from "clsx";
import { Box, FileCode2, FileText, Folder, Plus } from "lucide-react";
import { useCallback, useState } from "react";
import type { AppState, WorkflowFile } from "../lib/types";
import { createAgentDirStructure } from "../lib/tauri";

interface Props {
  files: WorkflowFile[];
  appState: AppState;
  statusLine: string;
  activeYamlPath: string;
  activeMdPath: string;
  onSelectYaml: (path: string) => void;
  onSelectMd: (path: string) => void;
}

const STATE_DOT: Record<AppState, string> = {
  IDLE: "bg-accent_amber/30",
  PROCESSING: "bg-accent_amber animate-pulse shadow-amber",
  SUCCESS: "bg-emerald-400",
  ERROR: "bg-red-500",
};

export function ScaffoldingSidebar({
  files,
  appState,
  statusLine,
  activeYamlPath,
  activeMdPath,
  onSelectYaml,
  onSelectMd,
}: Props) {
  const [scaffolding, setScaffolding] = useState(false);

  const handleScaffold = useCallback(async () => {
    setScaffolding(true);
    try {
      // Tauri dialog plugin may not be available in browser preview; guard it.
      let targetDir = "./workspace";
      try {
        const mod = await import("@tauri-apps/plugin-dialog");
        const chosen = await mod.open({
          directory: true,
          multiple: false,
          title: "Valitse AgentDir-juuri",
        });
        if (typeof chosen === "string") targetDir = chosen;
      } catch {
        // Preview fallback
      }
      await createAgentDirStructure(targetDir);
    } finally {
      setScaffolding(false);
    }
  }, []);

  const yamlFiles = files.filter((f) => f.kind === "yaml");
  const mdFiles = files.filter((f) => f.kind === "markdown");

  return (
    <aside className="relative z-10 flex h-full w-64 flex-col border-r border-panel_oxidized/60 bg-panel_oxidized/30 backdrop-blur-md">
      {/* Header — oxidized plate */}
      <div className="flex items-center gap-2 border-b border-panel_oxidized/60 px-4 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-md border border-accent_amber/40 bg-base_bg shadow-amber">
          <Box size={16} className="text-accent_amber" />
        </div>
        <div className="leading-tight">
          <div className="font-heading text-sm font-semibold tracking-widest text-ink_soft">
            AGENTDIR
          </div>
          <div className="font-code text-[10px] uppercase tracking-[0.2em] text-ink_muted">
            × Achii v4.1
          </div>
        </div>
      </div>

      {/* Scaffold button */}
      <button
        type="button"
        onClick={handleScaffold}
        disabled={scaffolding}
        className={clsx(
          "mx-3 mt-4 flex items-center justify-center gap-2 rounded border border-panel_oxidized/60 bg-base_bg/70 px-3 py-2 text-xs font-medium tracking-wide transition copper-glow",
          scaffolding ? "opacity-60" : "hover:border-accent_amber/70 hover:text-accent_amber",
        )}
      >
        <Plus size={14} />
        {scaffolding ? "Skafoldataan…" : "Luo AgentDir-rakenne"}
      </button>

      {/* File tree */}
      <div className="mt-5 flex-1 overflow-y-auto px-3 no-scrollbar">
        <SidebarSection label=".achii / templates">
          {yamlFiles.length === 0 && <EmptyHint label="Ei YAML-valjaita" />}
          {yamlFiles.map((f) => (
            <FileRow
              key={f.path}
              icon={<FileCode2 size={14} />}
              label={f.name}
              active={f.path === activeYamlPath}
              onClick={() => onSelectYaml(f.path)}
            />
          ))}
        </SidebarSection>

        <SidebarSection label="docs">
          {mdFiles.length === 0 && <EmptyHint label="Ei markdown-kontekstia" />}
          {mdFiles.map((f) => (
            <FileRow
              key={f.path}
              icon={<FileText size={14} />}
              label={f.name}
              active={f.path === activeMdPath}
              onClick={() => onSelectMd(f.path)}
            />
          ))}
        </SidebarSection>

        <SidebarSection label="workspace">
          <FileRow icon={<Folder size={14} />} label="Inbox/" muted />
          <FileRow icon={<Folder size={14} />} label="Outbox/" muted />
        </SidebarSection>
      </div>

      {/* Status footer */}
      <div className="border-t border-panel_oxidized/60 px-3 py-3">
        <div className="flex items-center gap-2">
          <span className={clsx("h-2 w-2 rounded-full", STATE_DOT[appState])} />
          <span className="font-code text-[10px] uppercase tracking-[0.18em] text-ink_muted">
            {appState}
          </span>
        </div>
        <div className="mt-1 truncate font-code text-[11px] text-ink_soft/80" title={statusLine}>
          {statusLine}
        </div>
      </div>
    </aside>
  );
}

function SidebarSection({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-4">
      <div className="mb-2 font-code text-[10px] uppercase tracking-[0.22em] text-ink_muted">
        {label}
      </div>
      <div className="flex flex-col gap-1">{children}</div>
    </div>
  );
}

function FileRow({
  icon,
  label,
  active,
  muted,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  muted?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "flex items-center gap-2 rounded px-2 py-1.5 text-left text-xs font-code transition",
        active && "bg-accent_amber/10 text-accent_amber shadow-[inset_0_0_0_1px_rgba(243,156,18,0.35)]",
        !active && !muted && "text-ink_soft/80 hover:bg-panel_oxidized/40",
        muted && "cursor-default text-ink_muted",
      )}
    >
      <span className={clsx(active ? "text-accent_amber" : "text-ink_muted")}>{icon}</span>
      <span className="truncate">{label}</span>
    </button>
  );
}

function EmptyHint({ label }: { label: string }) {
  return (
    <div className="px-2 py-1 font-code text-[10px] text-ink_muted/70">{label}</div>
  );
}
