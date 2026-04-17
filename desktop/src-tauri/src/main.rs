// Tauri 2 desktop shell — AgentDir × Achii Sovereign Engine.
//
// The Rust layer is intentionally thin but authoritative: it is the
// gatekeeper between the React frontend (running in a WebView) and the
// Python AgentDir core. It never hallucinates behaviour — it validates,
// sanitises, and then delegates either to local file operations or to the
// AgentDir HTTP gateway (`server.py`).
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod fs_handler;
mod gatekeeper;
mod local_ai;
mod scaffolding;

use gatekeeper::{RunWorkflowRequest, RunWorkflowResult};
use scaffolding::ScaffoldResult;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            create_agent_dir_structure,
            list_workspace_files,
            read_file_text,
            write_file_text,
            run_workflow,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// ── Tauri command surface ────────────────────────────────────────────────
//
// The function names here are the IPC command names the TS client in
// `src/lib/tauri.ts` invokes. `rename_all = "camelCase"` makes the
// JS/TS-side argument names (e.g. `targetDir`, `rootDir`) map to the
// snake_case Rust parameters — matching what `tauri.ts` already sends.
// The underlying implementations live in the sibling modules.

#[tauri::command(rename_all = "camelCase")]
fn create_agent_dir_structure(target_dir: String) -> Result<ScaffoldResult, String> {
    scaffolding::create_agent_dir_structure(&target_dir).map_err(|e| e.to_string())
}

#[tauri::command(rename_all = "camelCase")]
fn list_workspace_files(root_dir: String) -> Result<Vec<fs_handler::WorkflowFile>, String> {
    fs_handler::list_workspace_files(&root_dir).map_err(|e| e.to_string())
}

#[tauri::command]
fn read_file_text(path: String) -> Result<String, String> {
    fs_handler::read_file_text(&path).map_err(|e| e.to_string())
}

#[tauri::command]
fn write_file_text(path: String, contents: String) -> Result<(), String> {
    fs_handler::write_file_text(&path, &contents).map_err(|e| e.to_string())
}

#[tauri::command]
async fn run_workflow(request: RunWorkflowRequest) -> Result<RunWorkflowResult, String> {
    gatekeeper::run_workflow(request).await.map_err(|e| e.to_string())
}
