/**
 * Tauri command wrappers. In browser-only dev (no Tauri context) we fall back
 * to deterministic stubs so the Vite dev server is usable without the Rust
 * backend running — useful for UI iteration and CI builds.
 */

import type {
  RunWorkflowRequest,
  RunWorkflowResult,
  ScaffoldResult,
  WorkflowFile,
} from "./types";

// Tauri's `@tauri-apps/api/core` throws if the window global isn't wired up.
// We lazy-import to keep the web preview path (npm run preview) clean.
async function invokeSafe<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  // `window.__TAURI_INTERNALS__` is injected by the Tauri runtime.
  const hasTauri =
    typeof window !== "undefined" &&
    ((window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ !== undefined ||
      (window as unknown as { __TAURI__?: unknown }).__TAURI__ !== undefined);
  if (!hasTauri) {
    throw new Error(`Tauri bridge unavailable (cmd=${cmd}); running in browser preview`);
  }
  const { invoke } = await import("@tauri-apps/api/core");
  return invoke<T>(cmd, args);
}

export async function createAgentDirStructure(targetDir: string): Promise<ScaffoldResult> {
  try {
    return await invokeSafe<ScaffoldResult>("create_agent_dir_structure", { targetDir });
  } catch {
    return {
      target_dir: targetDir,
      created_files: [
        ".achii/templates/agent.yaml",
        "docs/00-SPARK.md",
        "docs/01-PRD.md",
        "Inbox/.gitkeep",
        "Outbox/.gitkeep",
        "Workspace/.gitkeep",
      ],
      skipped_files: [],
    };
  }
}

export async function listWorkspaceFiles(rootDir: string): Promise<WorkflowFile[]> {
  try {
    return await invokeSafe<WorkflowFile[]>("list_workspace_files", { rootDir });
  } catch {
    return [
      { path: "docs/01-PRD.md", name: "01-PRD.md", kind: "markdown" },
      { path: ".achii/templates/agent.yaml", name: "agent.yaml", kind: "yaml" },
    ];
  }
}

export async function readFileText(path: string): Promise<string> {
  try {
    return await invokeSafe<string>("read_file_text", { path });
  } catch {
    return `# ${path}\n\n_(Preview fallback — Tauri bridge ei ole käynnissä)_\n`;
  }
}

export async function writeFileText(path: string, contents: string): Promise<void> {
  try {
    await invokeSafe<void>("write_file_text", { path, contents });
  } catch {
    // no-op in preview mode
  }
}

export async function runWorkflow(req: RunWorkflowRequest): Promise<RunWorkflowResult> {
  try {
    return await invokeSafe<RunWorkflowResult>("run_workflow", { request: req });
  } catch (err) {
    return {
      success: false,
      summary: "Tauri bridge offline — simulated failure in browser preview.",
      model: "stub",
      mode: req.mode,
      print_id: "",
      error: err instanceof Error ? err.message : String(err),
    };
  }
}
