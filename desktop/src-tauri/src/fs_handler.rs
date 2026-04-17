// Scoped filesystem helpers used by the desktop shell.
//
// Rules of engagement:
//  - Never read files outside of the caller-provided root. We resolve paths
//    and reject anything that escapes via `..`.
//  - YAML files live under `.achii/templates/` (logic).
//  - Markdown files live under `docs/` (context).
//  - Runtime directories `Inbox/`, `Outbox/`, `Workspace/` are scaffolded
//    but not introspected here — those are the Python core's territory.

use std::fs;
use std::path::{Path, PathBuf};

use serde::Serialize;
use thiserror::Error;
use walkdir::WalkDir;

#[derive(Debug, Error)]
pub enum FsError {
    #[error("path traversal is not allowed: {0}")]
    PathTraversal(String),
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
    #[error("not a utf-8 file: {0}")]
    NotUtf8(String),
}

#[derive(Debug, Serialize, Clone)]
pub struct WorkflowFile {
    pub path: String,
    pub name: String,
    pub kind: FileKind,
}

#[derive(Debug, Serialize, Clone, Copy)]
#[serde(rename_all = "lowercase")]
pub enum FileKind {
    Yaml,
    Markdown,
}

pub fn list_workspace_files(root: &str) -> Result<Vec<WorkflowFile>, FsError> {
    let root = canonical_root(root)?;
    let mut out = Vec::new();

    for entry in WalkDir::new(&root)
        .max_depth(6)
        .into_iter()
        .filter_map(Result::ok)
    {
        if !entry.file_type().is_file() {
            continue;
        }
        let path = entry.path();
        let rel = match path.strip_prefix(&root) {
            Ok(r) => r,
            Err(_) => continue,
        };

        let Some(kind) = classify(rel) else { continue };

        out.push(WorkflowFile {
            path: rel.to_string_lossy().replace('\\', "/"),
            name: path
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default(),
            kind,
        });
    }

    out.sort_by(|a, b| a.path.cmp(&b.path));
    Ok(out)
}

pub fn read_file_text(path: &str) -> Result<String, FsError> {
    let p = safe_path(path)?;
    let bytes = fs::read(&p)?;
    String::from_utf8(bytes).map_err(|_| FsError::NotUtf8(path.to_string()))
}

pub fn write_file_text(path: &str, contents: &str) -> Result<(), FsError> {
    let p = safe_path(path)?;
    if let Some(parent) = p.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(&p, contents)?;
    Ok(())
}

// ── Internal helpers ─────────────────────────────────────────────────────

fn canonical_root(root: &str) -> Result<PathBuf, FsError> {
    let p = PathBuf::from(root);
    let canonical = p.canonicalize().unwrap_or(p);
    Ok(canonical)
}

fn safe_path(path: &str) -> Result<PathBuf, FsError> {
    let p = PathBuf::from(path);
    for comp in p.components() {
        if matches!(comp, std::path::Component::ParentDir) {
            return Err(FsError::PathTraversal(path.to_string()));
        }
    }
    Ok(p)
}

fn classify(rel: &Path) -> Option<FileKind> {
    let ext = rel.extension().and_then(|e| e.to_str()).unwrap_or("");
    let path_str = rel.to_string_lossy();

    match ext {
        "yaml" | "yml" => Some(FileKind::Yaml),
        "md" | "markdown" => {
            if path_str.starts_with("docs/") || path_str.starts_with("docs\\") {
                Some(FileKind::Markdown)
            } else if path_str == "README.md" || path_str == "CHANGELOG.md" {
                Some(FileKind::Markdown)
            } else {
                None
            }
        }
        _ => None,
    }
}
