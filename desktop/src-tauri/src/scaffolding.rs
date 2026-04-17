// Materialise the AgentDir × Achii directory scaffold.
//
// The frontend invokes `create_agent_dir_structure` with a target directory;
// we materialise the full reference layout:
//
//   <target>/
//     .achii/templates/agent.yaml   ← example harness
//     docs/00-SPARK.md              ← vision
//     docs/01-PRD.md                ← product spec
//     docs/03-PRDs/refactor.md      ← default editor context
//     Inbox/.gitkeep
//     Outbox/.gitkeep
//     Workspace/.gitkeep
//
// Existing files are skipped, never overwritten — we do not want to surprise
// the user by clobbering work.

use std::fs;
use std::path::{Path, PathBuf};

use serde::Serialize;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ScaffoldError {
    #[error("target dir does not exist: {0}")]
    MissingTarget(String),
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
}

#[derive(Debug, Serialize)]
pub struct ScaffoldResult {
    pub target_dir: String,
    pub created_files: Vec<String>,
    pub skipped_files: Vec<String>,
}

const AGENT_YAML: &str = r#"# FILE: .achii/templates/agent.yaml
# AgentDir × Achii harness template — copy to spin up a new workflow.
workflow_metadata:
  name: "default_agent"
  version: "0.1.0"
  role: "Elite Sovereign Agent"

tech_stack_constraints:
  core: "Python 3.11 + AgentDir orchestrator"
  local_ai: "Ollama / Gemma 4"
  cloud_escalation: "Anthropic Claude (opt-in)"

strict_rules:
  - NO_YAPPING: "Respond with structured YAML/JSON, not prose."
  - LOCAL_FIRST: "Never escalate to cloud without sanitisation."
  - NO_SECRETS: "Strip API keys, tokens and credentials before any egress."

state_machine:
  states: [IDLE, THINKING_LOCAL, THINKING_CLOUD, ERROR, SUCCESS]
"#;

const SPARK_MD: &str = r#"# 00 · SPARK

> Jokainen kansio on itsenäinen, oppiva tekoälyagentti.

Tämä työtila on AgentDir × Achii **Sovereign Engine** -ympäristö. Pudota
tiedosto `Inbox/`-kansioon tai kuvaile tehtävä `docs/01-PRD.md`-tiedostossa,
ja paina desktop-sovelluksessa **Run Workflow**.
"#;

const PRD_MD: &str = r#"# 01 · PRD

## Tavoite
Kirjoita tähän mitä haluat Achiin tekevän. Pidä kieli tiiviinä ja
rakenteellisena — tämä dokumentti on Achiin "konteksti-aivot".

## Syöte
- Tiedostot: listaa `Inbox/`-tiedostot
- Parametrit: listaa tärkeimmät parametrit

## Tulos
- Odotettu muoto (esim. `Outbox/vastaus_*.md`)
- Tarkistuslista, milloin tulos on "hyväksytty"
"#;

const REFACTOR_MD: &str = r#"# docs / 03-PRDs / refactor.md

> **Sovereign Engine v4.1** — yhdistetty Tauri-desktop-kerros Achiin elävälle
> käyttöliittymälle. Pudota `Inbox/`-kansioon tehtävä, seuraa Achiita oikeassa
> alakulmassa ja katso valjaiden ohjaavan tuloksen putkeen.

## Flow
1. Valitse työnkulku (`.achii/templates/*.yaml`).
2. Syötä konteksti (`docs/*.md`).
3. Paina **Run Workflow** → Rust-gatekeeper validoi → Python-ydin suorittaa.
4. Achii signaloi tilan (IDLE → PROCESSING → SUCCESS/ERROR).
"#;

pub fn create_agent_dir_structure(target: &str) -> Result<ScaffoldResult, ScaffoldError> {
    let target = PathBuf::from(target);
    if !target.exists() {
        fs::create_dir_all(&target)?;
    }

    let files: [(&str, &str); 7] = [
        (".achii/templates/agent.yaml", AGENT_YAML),
        ("docs/00-SPARK.md", SPARK_MD),
        ("docs/01-PRD.md", PRD_MD),
        ("docs/03-PRDs/refactor.md", REFACTOR_MD),
        ("Inbox/.gitkeep", ""),
        ("Outbox/.gitkeep", ""),
        ("Workspace/.gitkeep", ""),
    ];

    let mut created = Vec::new();
    let mut skipped = Vec::new();

    for (rel, body) in files {
        let path = target.join(rel);
        if path.exists() {
            skipped.push(rel.to_string());
            continue;
        }
        write_with_parents(&path, body)?;
        created.push(rel.to_string());
    }

    Ok(ScaffoldResult {
        target_dir: target.to_string_lossy().into_owned(),
        created_files: created,
        skipped_files: skipped,
    })
}

fn write_with_parents(path: &Path, body: &str) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, body)
}
