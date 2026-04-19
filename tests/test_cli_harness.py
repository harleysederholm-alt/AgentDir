"""
test_cli_harness.py — regressiotestit rebrändätylle CLI:lle (slash-komennot,
JSON-output, ANSI-teema). Ei käynnistä REPL-silmukkaa — suoraan funktioihin.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cli  # noqa: E402
from cli_theme import (  # noqa: E402
    AchiiState,
    banner,
    paint,
    render_status_bar,
    render_table,
    rule,
    supports_color,
)


# ─────────────────────────────────────────────────────────────────────────────
#  cli_theme primitives
# ─────────────────────────────────────────────────────────────────────────────

class TestTheme:
    def test_banner_includes_version_and_codename(self):
        out = banner("1.0.4-beta", "The Rusty Awakening")
        assert "1.0.4-beta" in out
        assert "Rusty Awakening" in out
        # Figlet "slant" -ASCII-art sisältää alaviivoja ja vinoviivoja
        assert "___" in out and "/" in out
        assert "ENGINEERING LOCAL HARNESS" in out

    def test_paint_is_noop_without_color(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        assert paint("hello", "\x1b[31m") == "hello"

    def test_render_status_bar_lists_brand_fields(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        state = AchiiState(
            achii="AWAKE",
            harness="ENGAGED",
            inference_ms=2500,
            tokens_per_s=31.0,
            entropy=0.12,
            egress_bytes=0,
        )
        bar = render_status_bar(state)
        assert "ACHII" in bar
        assert "AWAKE" in bar
        assert "HARNESS" in bar
        assert "ENGAGED" in bar
        assert "latency" in bar
        assert "tok/s" in bar
        assert "entropy" in bar
        assert "egress" in bar

    def test_render_table_has_box_drawing_and_rows(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        table = render_table(
            ["name", "kind"],
            [["refactor.yaml", "logic"], ["context.md", "context"]],
        )
        assert "┌" in table and "┐" in table
        assert "refactor.yaml" in table
        assert "context.md" in table
        assert "logic" in table

    def test_rule_can_render_plain_or_titled(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        plain = rule()
        assert "─" in plain
        titled = rule("telemetry")
        assert "telemetry" in titled

    def test_supports_color_respects_no_color(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        assert supports_color() is False


# ─────────────────────────────────────────────────────────────────────────────
#  cmd_status + cmd_status_json
# ─────────────────────────────────────────────────────────────────────────────

class TestStatusOutputs:
    def test_cmd_status_preserves_sovereign_banner(self):
        out = cli.cmd_status()
        assert "SOVEREIGN ENGINE STATUS" in out
        # Table sisältää tärkeät riviotsikot
        for label in ("MODEL", "RAG", "EVOLUTION", "INBOX", "OUTBOX"):
            assert label in out

    def test_cmd_status_json_is_parseable(self):
        raw = cli.cmd_status_json()
        data = json.loads(raw)
        assert data["command"] == "status"
        engine = data["engine"]
        for key in ("model", "rag", "evolution", "inbox", "outbox"):
            assert key in engine


# ─────────────────────────────────────────────────────────────────────────────
#  Slash-command dispatcher
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_globals():
    """Varmista, että --json / --verbose liput nollautuvat testien välillä."""
    cli._JSON = False
    cli._VERBOSE = False
    yield
    cli._JSON = False
    cli._VERBOSE = False


class TestSlashDispatch:
    def test_non_slash_returns_false(self):
        assert cli.dispatch_slash("run some task") is False

    def test_unknown_slash_returns_true_and_warns(self, capsys):
        dispatched = cli.dispatch_slash("/unknown")
        assert dispatched is True
        err = capsys.readouterr().err
        assert "tuntematon" in err.lower() or "unknown" in err.lower()

    def test_status_slash_prints_sovereign_banner(self, capsys, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        cli.dispatch_slash("/status")
        out = capsys.readouterr().out
        assert "SOVEREIGN ENGINE STATUS" in out

    def test_status_slash_with_json_flag(self, capsys):
        cli._JSON = True
        cli.dispatch_slash("/status")
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["command"] == "status"

    def test_harness_slash_json_lists_artifacts(self, capsys):
        cli._JSON = True
        cli.dispatch_slash("/harness")
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["command"] == "harness"
        assert "yaml_harnesses" in payload
        assert "workflow_modules" in payload

    def test_clean_slash_resets_state(self, capsys, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        cli._STATE.inference_ms = 9000
        cli._STATE.entropy = 0.92
        cli.dispatch_slash("/clean")
        assert cli._STATE.inference_ms == 0
        assert cli._STATE.entropy == 0.0

    def test_attach_rejects_unsupported_extension(self, tmp_path, capsys):
        bad = tmp_path / "x.txt"
        bad.write_text("nope")
        cli.dispatch_slash(f"/attach {bad}")
        err = capsys.readouterr().err
        assert "hylkäsi" in err or "rejected" in err.lower() or "vain" in err

    def test_attach_yaml_updates_entropy_and_emits_json(self, tmp_path, capsys):
        cli._JSON = True
        y = tmp_path / "refactor.yaml"
        y.write_text("harness: {}", encoding="utf-8")
        cli.dispatch_slash(f"/attach {y}")
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["command"] == "attach"
        assert payload["kind"].startswith("LOGIC")
        assert payload["entropy"] < 0.2

    def test_attach_md_has_higher_entropy_than_yaml(self, tmp_path, capsys):
        cli._JSON = True
        md = tmp_path / "context.md"
        md.write_text("# context", encoding="utf-8")
        cli.dispatch_slash(f"/attach {md}")
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["kind"].startswith("CONTEXT")
        assert payload["entropy"] > 0.2

    def test_logs_slash_handles_empty_state(self, capsys, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("NO_COLOR", "1")
        cli.dispatch_slash("/logs")
        out = capsys.readouterr().out
        assert "ei lokimerkintöjä" in out or "logs" in out.lower()

    def test_logs_slash_json_with_tail(self, capsys, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "evolution_log.jsonl").write_text(
            '{"ts":"2026-05-13","message":"harness engaged"}\n'
            '{"ts":"2026-05-13","message":"refactor ok"}\n',
            encoding="utf-8",
        )
        cli._JSON = True
        cli.dispatch_slash("/logs --tail 5")
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["command"] == "logs"
        assert payload["tail"] == 5
        assert len(payload["entries"]) == 2


# ─────────────────────────────────────────────────────────────────────────────
#  Global flags via main()
# ─────────────────────────────────────────────────────────────────────────────

class TestGlobalFlags:
    def test_json_flag_activates_machine_output(self, capsys):
        cli.main(["--json", "status"])
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["command"] == "status"

    def test_verbose_flag_emits_trace_on_stderr(self, capsys, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        cli.main(["--verbose", "status"])
        err = capsys.readouterr().err
        assert "trace" in err or "harness" in err

    def test_build_parser_registers_all_commands(self):
        parser = cli._build_parser()
        # argparse subparsers livessä → action-choices attribuutti
        subactions = [a for a in parser._actions if getattr(a, "choices", None) and "run" in a.choices]
        assert subactions, "subparsers missing"
        choices = set(subactions[0].choices.keys())
        for expected in (
            "run", "init", "status", "benchmark", "harness",
            "clean", "attach", "logs", "print", "achii",
        ):
            assert expected in choices


# ─────────────────────────────────────────────────────────────────────────────
#  Origin story — The Fallen Sovereign
# ─────────────────────────────────────────────────────────────────────────────

class TestOriginStory:
    def test_iter_story_lines_classifies_log_speech_status(self):
        parts = cli._iter_story_lines()
        kinds = [k for k, _ in parts]
        assert kinds.count("log") == 3
        assert kinds.count("speech") == 3
        assert kinds.count("status") == 1
        # viimeinen on STATUS-rivi
        assert parts[-1][0] == "status"
        assert "ENGINE_ARMED" in parts[-1][1]

    def test_iter_story_lines_missing_file_returns_empty(self, tmp_path):
        missing = tmp_path / "does_not_exist.md"
        assert cli._iter_story_lines(missing) == []

    def test_play_origin_story_fast_outputs_full_script(self, capsys, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        total = cli.play_origin_story(fast=True)
        out = capsys.readouterr().out
        assert total > 0
        assert "BOOT_SEQUENCE_INITIATED" in out
        assert "MEMORY_FRAGMENT_RECOVERED" in out
        assert "CORE_ALIGNMENT_SUCCESS" in out
        assert "READY. ENGINE_ARMED" in out
        # Lopussa 'agentdir > /start' -prompt
        assert "/start" in out
        # Typewriter ei saa vuotaa CSI-koodeja NO_COLOR-tilassa
        assert "\x1b[" not in out

    def test_slash_whoami_json_emits_segments(self, capsys):
        cli._JSON = True
        cli.dispatch_slash("/whoami")
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["command"] == "whoami"
        assert payload["script"].endswith("origin_story.md")
        segments = payload["segments"]
        assert len(segments) == 7  # 3 log + 3 speech + 1 status
        assert segments[0]["kind"] == "log"
        assert segments[-1]["kind"] == "status"

    def test_achii_whoami_subcommand_via_main(self, capsys, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        cli.main(["achii", "--whoami", "--fast"])
        out = capsys.readouterr().out
        assert "ENGINE_ARMED" in out
        assert "/start" in out

    def test_achii_subcommand_without_whoami_prints_usage(self, capsys):
        cli.main(["achii"])
        err = capsys.readouterr().err
        assert "--whoami" in err

    def test_start_slash_acknowledges(self, capsys):
        cli.dispatch_slash("/start")
        err = capsys.readouterr().err
        assert "harness" in err.lower() or "engaged" in err.lower()
