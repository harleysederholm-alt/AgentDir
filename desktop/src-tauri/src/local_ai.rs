// Local AI bridge + shared sanitiser.
//
// Two responsibilities:
//
//  1. `sanitise_for_egress` strips secret-shaped tokens from any payload
//     before the gatekeeper ships it off-device. Regexes are intentionally
//     narrow — we'd rather miss an exotic key format than match a legitimate
//     substring of the user's prose.
//
//  2. `local_stub_echo` produces a deterministic "we couldn't reach the
//     Python core, here's what we would have sent" response so the UI can
//     keep running (and Achii can keep emoting) even when the server is
//     offline. A future iteration will replace this with an Ollama call.

use once_cell::sync::Lazy;
use regex::Regex;

use crate::gatekeeper::RunWorkflowResult;

static SECRET_PATTERNS: Lazy<Vec<Regex>> = Lazy::new(|| {
    vec![
        // Anthropic / Claude
        Regex::new(r"sk-ant-[A-Za-z0-9_-]{20,}").unwrap(),
        // OpenAI
        Regex::new(r"sk-[A-Za-z0-9]{32,}").unwrap(),
        // GitHub
        Regex::new(r"ghp_[A-Za-z0-9]{20,}").unwrap(),
        Regex::new(r"github_pat_[A-Za-z0-9_]{20,}").unwrap(),
        // Bearer tokens
        Regex::new(r"(?i)bearer\s+[A-Za-z0-9._-]{20,}").unwrap(),
        // Generic API_KEY=... lines
        Regex::new(r"(?i)(api[_-]?key|secret|password)\s*=\s*[^\s]+").unwrap(),
    ]
});

pub fn sanitise_for_egress(input: &str) -> String {
    let mut out = input.to_string();
    for pat in SECRET_PATTERNS.iter() {
        out = pat.replace_all(&out, "[REDACTED]").into_owned();
    }
    out
}

pub fn local_stub_echo(mode: &str, task: &str) -> RunWorkflowResult {
    let short = task.chars().take(160).collect::<String>();
    RunWorkflowResult {
        success: true,
        summary: format!(
            "[LOCAL_STUB] Python-yhdyskäytävä ei ole käytettävissä. Valjas validoitu ja sanitoitu. Esikatsaus: {short}"
        ),
        model: "local-stub".to_string(),
        mode: mode.to_string(),
        print_id: "stub-0000".to_string(),
        error: None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sanitises_openai_key() {
        let input = "export OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz0123456789";
        let out = sanitise_for_egress(input);
        assert!(out.contains("[REDACTED]"));
        assert!(!out.contains("sk-abcdef"));
    }

    #[test]
    fn sanitises_bearer_token() {
        let input = "Authorization: Bearer abcdefghijklmnopqrst1234";
        let out = sanitise_for_egress(input);
        assert!(out.contains("[REDACTED]"));
    }

    #[test]
    fn leaves_normal_text_alone() {
        let input = "Kirjoita runo Achiista, ei salaisuuksia tässä.";
        assert_eq!(sanitise_for_egress(input), input);
    }
}
