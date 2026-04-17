// Semantic router / gatekeeper.
//
// Flow:
//   1. Parse & validate the workflow YAML.
//   2. Load the optional markdown context.
//   3. Sanitise both (strip API keys, passwords, bearer tokens).
//   4. Either:
//        a) talk to the AgentDir HTTP gateway (`server.py`) if it is reachable, or
//        b) fall back to a local echo stub so the UI stays functional.
//   5. Return a `RunWorkflowResult` shaped like the orchestrator's summary.

use std::time::Duration;

use anyhow::{anyhow, Context, Result};
use serde::{Deserialize, Serialize};

use crate::fs_handler::read_file_text;
use crate::local_ai::{local_stub_echo, sanitise_for_egress};

const DEFAULT_GATEWAY: &str = "http://127.0.0.1:8080";

#[derive(Debug, Deserialize)]
pub struct RunWorkflowRequest {
    pub workflow_path: String,
    pub context_path: Option<String>,
    #[serde(default = "default_mode")]
    pub mode: String,
}

fn default_mode() -> String {
    "openclaw".to_string()
}

#[derive(Debug, Serialize)]
pub struct RunWorkflowResult {
    pub success: bool,
    pub summary: String,
    pub model: String,
    pub mode: String,
    pub print_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

pub async fn run_workflow(req: RunWorkflowRequest) -> Result<RunWorkflowResult> {
    // 1. Read + validate the YAML harness.
    let yaml_raw =
        read_file_text(&req.workflow_path).context("lukeminen epäonnistui (workflow_path)")?;
    let _parsed: serde_yaml::Value = serde_yaml::from_str(&yaml_raw).map_err(|e| {
        anyhow!(
            "ACHII_VAL_ERR: .yaml ei ole validi ({e}) — valjaiden oltava puhtaat ennen ajoa"
        )
    })?;

    // 2. Optional markdown context.
    let context = match &req.context_path {
        Some(p) => read_file_text(p).unwrap_or_default(),
        None => String::new(),
    };

    // 3. Sanitise both sides before any egress.
    let sanitised_yaml = sanitise_for_egress(&yaml_raw);
    let sanitised_ctx = sanitise_for_egress(&context);

    // 4. Try the local AgentDir HTTP gateway first.
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(30))
        .build()
        .context("reqwest client init")?;

    let task = format!(
        "Harness: {}\n\nContext:\n{}",
        sanitised_yaml, sanitised_ctx
    );

    match post_to_gateway(&client, &task, &req.mode).await {
        Ok(res) => Ok(res),
        Err(err) => {
            // 5. Graceful fallback — never block the UI on a missing Python core.
            log::warn!("gateway unavailable, falling back to local stub: {err:#}");
            Ok(local_stub_echo(&req.mode, &task))
        }
    }
}

#[derive(Debug, Serialize)]
struct GatewayRequest<'a> {
    task: &'a str,
    mode: &'a str,
}

#[derive(Debug, Deserialize)]
struct GatewayResponse {
    #[serde(default)]
    success: bool,
    #[serde(default)]
    summary: String,
    #[serde(default)]
    model: String,
    #[serde(default)]
    mode: String,
    #[serde(default)]
    print_id: String,
}

async fn post_to_gateway(
    client: &reqwest::Client,
    task: &str,
    mode: &str,
) -> Result<RunWorkflowResult> {
    let url = format!("{}/task", DEFAULT_GATEWAY);
    let payload = GatewayRequest { task, mode };
    let resp = client.post(url).json(&payload).send().await?;
    if !resp.status().is_success() {
        return Err(anyhow!("gateway returned {}", resp.status()));
    }
    let gw: GatewayResponse = resp.json().await?;
    Ok(RunWorkflowResult {
        success: gw.success,
        summary: gw.summary,
        model: gw.model,
        mode: gw.mode,
        print_id: gw.print_id,
        error: None,
    })
}
