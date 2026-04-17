/**
 * Shared types for the Tauri ⇄ React bridge. Kept intentionally narrow
 * so both the Rust commands (serde) and TypeScript consumers stay in sync.
 */

export type AppState = "IDLE" | "PROCESSING" | "SUCCESS" | "ERROR";

export interface WorkflowFile {
  path: string;
  name: string;
  kind: "yaml" | "markdown";
}

export interface ScaffoldResult {
  target_dir: string;
  created_files: string[];
  skipped_files: string[];
}

export interface RunWorkflowRequest {
  workflow_path: string;
  context_path: string | null;
  mode: "openclaw" | "hermes";
}

export interface RunWorkflowResult {
  success: boolean;
  summary: string;
  model: string;
  mode: string;
  print_id: string;
  error?: string;
}

export interface AchiiEvent {
  event: "WAVE" | "THINK" | "ALERT" | "DONE";
  payload: string;
}
