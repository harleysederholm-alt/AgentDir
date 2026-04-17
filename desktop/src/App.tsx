import { useCallback, useEffect, useMemo, useState } from "react";
import { ScaffoldingSidebar } from "./components/ScaffoldingSidebar";
import { SplitWorkspace } from "./components/SplitWorkspace";
import { AchiiCanvas } from "./components/AchiiCanvas";
import type { AppState, WorkflowFile } from "./lib/types";
import { listWorkspaceFiles, readFileText, runWorkflow } from "./lib/tauri";

const SEED_YAML = `# FILE: tauri_ui_config.yaml
workflow_metadata:
  name: "AgentDir_Achii_Tauri_Frontend"
  version: "1.0.0"
  role: "Elite Frontend Architect (React, TypeScript, Tailwind, R3F)"

tech_stack_constraints:
  framework: "Tauri + React + Vite"
  language: "TypeScript (Strict Mode)"
  styling: "Tailwind CSS + Framer Motion"
  3d_engine: "@react-three/fiber + @react-three/drei"

strict_rules:
  - NO_INFINITE_LOOPS
  - NO_FLAT_DESIGN
  - COMPONENT_STRUCTURE: modulaarinen
`;

const SEED_MD = `# docs / 03-PRDs / refactor.md

> **Sovereign Engine v4.1** — yhdistetty Tauri-desktop-kerros Achiin elävälle
> käyttöliittymälle. Pudota \`Inbox/\`-kansioon tehtävä, seuraa Achiita oikeassa
> alakulmassa ja katso valjaiden ohjaavan tuloksen putkeen.

## Design Tokens
- **Teatterimusta** \`#0F0F0F\`
- **Amber-hehku** \`#F39C12\`
- **Nuhruinen metalli** \`#2C3E50\`
- **Kuparinen paljastus** \`#D35400\`

## Flow
1. Valitse työnkulku (\`.achii/templates/*.yaml\`).
2. Syötä konteksti (\`docs/*.md\`).
3. Paina **Run Workflow** → Rust-gatekeeper validoi → Python-ydin suorittaa.
4. Achii signaloi tilan (IDLE → PROCESSING → SUCCESS/ERROR).
`;

export default function App() {
  const [appState, setAppState] = useState<AppState>("IDLE");
  const [files, setFiles] = useState<WorkflowFile[]>([]);
  const [activeYamlPath, setActiveYamlPath] = useState<string>(".achii/templates/agent.yaml");
  const [activeMdPath, setActiveMdPath] = useState<string>("docs/03-PRDs/refactor.md");
  const [yaml, setYaml] = useState<string>(SEED_YAML);
  const [md, setMd] = useState<string>(SEED_MD);
  const [statusLine, setStatusLine] = useState<string>("Valjaat valmiina. Achii lepää.");

  useEffect(() => {
    // Poll the gatekeeper for an initial workspace snapshot.
    listWorkspaceFiles(".")
      .then((f) => setFiles(f))
      .catch(() => {
        // Offline/preview — fall through with seed data.
      });
  }, []);

  const onSelectYaml = useCallback(async (path: string) => {
    setActiveYamlPath(path);
    try {
      const text = await readFileText(path);
      setYaml(text);
    } catch {
      setYaml(`# ${path}\n# (ei luettavissa)\n`);
    }
  }, []);

  const onSelectMd = useCallback(async (path: string) => {
    setActiveMdPath(path);
    try {
      const text = await readFileText(path);
      setMd(text);
    } catch {
      setMd(`# ${path}\n\n(ei luettavissa)`);
    }
  }, []);

  const onRunWorkflow = useCallback(async () => {
    if (appState === "PROCESSING") return;
    setAppState("PROCESSING");
    setStatusLine(`Aja valjaat: ${activeYamlPath}`);
    const result = await runWorkflow({
      workflow_path: activeYamlPath,
      context_path: activeMdPath,
      mode: "openclaw",
    });
    if (result.success) {
      setAppState("SUCCESS");
      setStatusLine(`Achii valmis · ${result.model} · print ${result.print_id}`);
    } else {
      setAppState("ERROR");
      setStatusLine(result.error ?? result.summary ?? "Tuntematon virhe");
    }
    // Pudota SUCCESS/ERROR-tila hetken kuluttua takaisin IDLE-tilaan.
    // Tämä ei ole loputon looppi — se on tapahtumapohjainen debounce.
    const resetHandle = window.setTimeout(() => setAppState("IDLE"), 4200);
    return () => window.clearTimeout(resetHandle);
  }, [appState, activeYamlPath, activeMdPath]);

  const headerPath = useMemo(() => {
    const parts = activeMdPath.split(/[\\/]+/).filter(Boolean);
    return parts.join(" / ");
  }, [activeMdPath]);

  return (
    <div className="relative flex h-screen w-screen overflow-hidden bg-base_bg text-ink_soft">
      {/* Anamorfinen taustakaarto — syvyyttä teatterimustalle. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-70"
        style={{
          background:
            "radial-gradient(1200px 600px at 10% -10%, rgba(44,62,80,0.35), transparent 60%), radial-gradient(900px 500px at 110% 120%, rgba(211,84,0,0.18), transparent 55%)",
        }}
      />

      <ScaffoldingSidebar
        files={files}
        appState={appState}
        statusLine={statusLine}
        activeYamlPath={activeYamlPath}
        activeMdPath={activeMdPath}
        onSelectYaml={onSelectYaml}
        onSelectMd={onSelectMd}
      />

      <SplitWorkspace
        headerPath={headerPath}
        yaml={yaml}
        md={md}
        onYamlChange={setYaml}
        onRunWorkflow={onRunWorkflow}
        appState={appState}
      />

      {/* Achii kelluu kulmassa — `pointer-events-none` paitsi canvas itse. */}
      <div className="pointer-events-none absolute bottom-4 right-4 h-56 w-56">
        <div className="pointer-events-auto h-full w-full">
          <AchiiCanvas appState={appState} />
        </div>
      </div>
    </div>
  );
}
