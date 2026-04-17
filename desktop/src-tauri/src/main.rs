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

use fs_handler::{list_workspace_files, read_file_text, write_file_text};
use gatekeeper::{run_workflow, RunWorkflowRequest, RunWorkflowResult};
use scaffolding::{create_agent_dir_structure, ScaffoldResult};

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            cmd_create_agent_dir_structure,
            cmd_list_workspace_files,
            cmd_read_file_text,
            cmd_write_file_text,
            cmd_run_workflow,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// ── Tauri command wrappers ───────────────────────────────────────────────
//
// These wrappers pin the public surface of the app. Frontend code only
// invokes these command names; the underlying modules stay pure Rust for
// unit-testability.

#[tauri::command]
#[allow(non_snake_case)]
fn cmd_create_agent_dir_structure(targetDir: String) -> Result<ScaffoldResult, String> {
    create_agent_dir_structure(&targetDir).map_err(|e| e.to_string())
}

#[tauri::command]
#[allow(non_snake_case)]
fn cmd_list_workspace_files(rootDir: String) -> Result<Vec<fs_handler::WorkflowFile>, String> {
    list_workspace_files(&rootDir).map_err(|e| e.to_string())
}

#[tauri::command]
fn cmd_read_file_text(path: String) -> Result<String, String> {
    read_file_text(&path).map_err(|e| e.to_string())
}

#[tauri::command]
fn cmd_write_file_text(path: String, contents: String) -> Result<(), String> {
    write_file_text(&path, &contents).map_err(|e| e.to_string())
}

#[tauri::command]
async fn cmd_run_workflow(request: RunWorkflowRequest) -> Result<RunWorkflowResult, String> {
    run_workflow(request).await.map_err(|e| e.to_string())
}
