# prdoc/cli.py
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from rich import box
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from prdoc.config import load_config
from prdoc.env import load_env
from prdoc.llm_client import LLMClient
from prdoc.logging import get_logger, setup_logging
from prdoc.patch_generator import DocHit, PatchGenerator
from prdoc.telemetry import TelemetryClient

# Ensure .env is loaded before reading any config/env in commands
load_env()

# Root Typer app (what tests expect)
app = typer.Typer(add_completion=False, no_args_is_help=False)

# One-time process-scoped notice flag (used only in help/diagnose to avoid test interference)
_TELEMETRY_NOTICE_SHOWN = False


@dataclass
class GlobalState:
    console: Console
    verbose: bool
    telemetry_enabled: bool


# Console & small styling helpers


_THEME = Theme(
    {
        "brand": "bold magenta",
        "subtle": "italic dim",
        "ok": "bold green",
        "warn": "bold yellow",
        "error": "bold red",
        "hint": "cyan",
        "tag": "bold blue",
    }
)


def _make_console(no_color: bool) -> Console:
    # Slightly narrower for nicer wrapping on typical terminals; still responsive.
    return Console(
        color_system=None if no_color else "auto",
        width=96,
        soft_wrap=True,
        theme=None if no_color else _THEME,
    )


def _version_str() -> str:
    try:
        from importlib import metadata

        return metadata.version("prdoc")
    except Exception:
        return "0.0.0"


def _truthy(v: Optional[str]) -> bool:
    if not v:
        return False
    return v.strip().lower() in {"1", "true", "yes", "on"}


def _brand_header(console: Console) -> None:
    """Consistent, compact header used by help and diagnose."""
    title = Text("pr-doc-sync", style="brand")
    version = Text(f" v{_version_str()}", style="subtle")
    tagline = Text("Keep your docs in lockstep with your code changes.", style="subtle")
    console.print(title.append_text(version))
    console.print(tagline)
    console.print(Rule(style="dim"))


def _maybe_print_telemetry_note(state: GlobalState) -> None:
    """Print a one-time opt-in telemetry note (only in help/diagnose)."""
    global _TELEMETRY_NOTICE_SHOWN
    if _TELEMETRY_NOTICE_SHOWN:
        return
    if not state.telemetry_enabled and not _truthy(os.getenv("PRDOC_TELEMETRY")):
        note = (
            "[bold]Anonymous telemetry is OFF[/bold]. We only collect counts & timings.\n"
            "Enable with [hint]PRDOC_TELEMETRY=1[/hint] or see [tag]prdoc help telemetry[/tag]."
        )
        state.console.print(Panel(note, title="Telemetry (optional)", box=box.ROUNDED))
        _TELEMETRY_NOTICE_SHOWN = True


# Global options callback


@app.callback(invoke_without_command=True)
def _global(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colors."),
    telemetry: Optional[bool] = typer.Option(
        None,
        "--telemetry/--no-telemetry",
        help="Opt in/out of anonymous usage telemetry for this run.",
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", help="Print version and exit.", is_eager=True
    ),
):
    """
    pr-doc-sync — detect code-doc drift in PRs and propose doc patches.
    """
    if version:
        typer.echo(_version_str())
        raise typer.Exit(code=0)

    console = _make_console(no_color)
    setup_logging(verbose=verbose)
    get_logger()  # ensure logger initialized

    # If the telemetry flag is provided, set env for this process (not persisted).
    if telemetry is not None:
        os.environ["PRDOC_TELEMETRY"] = "1" if telemetry else "0"

    client = TelemetryClient.from_env()
    ctx.obj = GlobalState(console=console, verbose=verbose, telemetry_enabled=client.enabled)

    # If no subcommand provided, show our pretty help
    if ctx.invoked_subcommand is None:
        ctx.invoke(help, command=None)
        raise typer.Exit()


# Helpers kept for tests


def build_llm(provider: str, model: Optional[str]) -> LLMClient:
    """Factory separated for easy monkeypatching in tests."""
    if provider not in {"openai", "groq"}:
        raise typer.BadParameter("provider must be 'openai' or 'groq'")
    return LLMClient(provider=provider, model=model)


def _resolve_for_read(p: str) -> Path:
    """
    Resolve a file path in a way that works with tests that create files under a
    tmp dir and pass relative paths without changing CWD.
    """
    cand = Path(p)
    if cand.is_absolute() and cand.exists():
        return cand
    if cand.exists():
        return cand

    for entry in list(sys.path):
        try:
            base = Path(entry)
        except Exception:
            continue
        if not base.exists() or not base.is_dir():
            continue
        candidate = base / p
        if candidate.exists():
            return candidate

    raise FileNotFoundError(p)


def read_hits_from_paths(paths: List[str]) -> List[DocHit]:
    """Read UTF-8 text files and return DocHit entries."""
    hits: List[DocHit] = []
    for p in paths:
        try:
            file_path = _resolve_for_read(p)
            text = file_path.read_text(encoding="utf-8")
        except FileNotFoundError as err:
            raise typer.BadParameter(f"file not found: {p}") from err
        except UnicodeDecodeError as err:
            raise typer.BadParameter(f"file is not UTF-8 text: {p}") from err
        hits.append(DocHit(path=str(p), text=text))
    return hits


# Pretty HELP


@app.command("help")
def help(
    command: Optional[str] = typer.Argument(
        None, help="Command to show help for (e.g., 'sync', 'apply', 'diagnose', 'telemetry')."
    ),
):
    """Pretty help & examples."""
    console = _make_console(no_color=False)
    _brand_header(console)

    if not command:
        # What is this?
        hdr = Panel.fit(
            Text.from_markup(
                "[b]prdoc[/b] — CLI & GitHub Action that detects code→doc drift in a PR, "
                "generates Markdown patches with an LLM, and optionally applies them."
            ),
            title="What is this?",
            box=box.ROUNDED,
        )

        # Commands grid
        cmd = Table(box=box.SIMPLE_HEAVY, expand=True, show_edge=True, title="Commands")
        cmd.add_column("Command", style="bold", no_wrap=True)
        cmd.add_column("What it does")
        cmd.add_row("sync", "Analyze diff, search docs, propose patches (dry-run by default).")
        cmd.add_row("apply", "Apply patches, commit & push (use --yes to skip prompt).")
        cmd.add_row("diagnose", "Check environment: tokens, Node/ts-morph, versions.")
        cmd.add_row("help [COMMAND]", "Show detailed help and examples for a command.")

        # Global options (quick reference)
        glob = Table.grid(padding=(0, 2))
        glob.add_column(justify="right", style="tag")
        glob.add_column()
        glob.add_row("--verbose / -v", "Enable debug logging.")
        glob.add_row("--no-color", "Disable ANSI colors.")
        glob.add_row("--telemetry/--no-telemetry", "Opt in/out for this run.")
        glob.add_row("--version", "Print version and exit.")
        global_panel = Panel(glob, title="Global options", box=box.ROUNDED)

        # Examples (two-column)
        examples_left = Markdown(
            "\n".join(
                [
                    "**Quickstart**",
                    "```bash\nprdoc help\nprdoc help sync\nprdoc sync --pr 123 --dry-run\nprdoc apply --yes\n```",
                ]
            )
        )
        examples_right = Markdown(
            "\n".join(
                [
                    "**Enable telemetry (optional)**",
                    "```bash\nPRDOC_TELEMETRY=1 prdoc sync --pr 123\n```",
                ]
            )
        )
        examples_group = Group(
            Panel(examples_left, box=box.ROUNDED),
            Panel(examples_right, box=box.ROUNDED),
        )

        console.print(hdr, "\n")
        console.print(cmd, "\n")
        console.print(global_panel, "\n")
        console.print(examples_group)
        console.print(Rule(style="dim"))
        console.print(
            Text("Tip: run ", style="subtle")
            .append_text(Text("prdoc help sync", style="tag"))
            .append(" for command-specific flags.", style="subtle")
        )
        return

    c = command.strip().lower()
    if c in {"sync"}:
        console.print(
            Panel(
                "[b]Usage[/b]: prdoc sync [--pr <num>] [--comment] [--dry-run] [--max-cost $]",
                title="sync",
                box=box.ROUNDED,
            )
        )
        # FIX: use a supported box style (SIMPLE instead of MINIMAL_HEAVY)
        t = Table(box=box.SIMPLE, expand=True)
        t.add_column("Option", style="bold", no_wrap=True)
        t.add_column("Description")
        t.add_row("--pr <num>", "Pull Request number to analyze.")
        t.add_row("--comment", "Post a summary comment to the PR (CI-friendly).")
        t.add_row("--dry-run", "Print patches without writing to disk.")
        t.add_row("--max-cost $", "Abort if estimated LLM spend would exceed this amount.")
        console.print(t)
        ex = Panel(
            "prdoc sync --pr 42 --dry-run\n"
            "prdoc sync --pr 42 --comment\n"
            "PRDOC_TELEMETRY=1 prdoc sync --pr 42 --max-cost 0.10",
            title="Examples",
            box=box.ROUNDED,
        )
        console.print(ex)
        return

    if c in {"apply"}:
        console.print(
            Panel(
                "[b]Usage[/b]: prdoc apply [--yes] [--branch <name>] [--commit-msg '<msg>']",
                title="apply",
                box=box.ROUNDED,
            )
        )
        # FIX: use a supported box style (SIMPLE instead of MINIMAL_HEAVY)
        t = Table(box=box.SIMPLE, expand=True)
        t.add_column("Option", style="bold", no_wrap=True)
        t.add_column("Description")
        t.add_row("--yes", "Do not prompt; apply patches, commit and push.")
        t.add_row("--branch <name>", "Target branch to push changes to.")
        t.add_row("--commit-msg '<msg>' / -m", "Custom commit message (alias: --message).")
        console.print(t)
        ex = Panel(
            "prdoc apply --yes\nprdoc apply --branch docs/update --commit-msg 'docs: align with PR #42'",
            title="Examples",
            box=box.ROUNDED,
        )
        console.print(ex)
        return

    if c in {"diagnose"}:
        console.print(Panel("[b]Usage[/b]: prdoc diagnose", title="diagnose", box=box.ROUNDED))
        console.print("Runs environment checks and prints a short report.")
        return

    if c in {"telemetry"}:
        txt = (
            "[b]Anonymous telemetry[/b] is [i]opt-in[/i]. When enabled, prdoc sends a tiny JSON "
            "payload with step [b]timings[/b] and [b]counts[/b] (no code, no docs, no repo names).\n\n"
            "Enable for this run: [tag]--telemetry[/tag]\n"
            "Enable via env: [tag]PRDOC_TELEMETRY=1[/tag]\n"
            "Disable explicitly: [tag]--no-telemetry[/tag] or [tag]PRDOC_TELEMETRY=0[/tag]"
        )
        console.print(Panel(Text.from_markup(txt), title="Telemetry (optional)", box=box.ROUNDED))
        return

    console.print(f"[error]Unknown command:[/error] {command}. Try: [tag]prdoc help[/tag]")
    raise typer.Exit(code=2)


# DIAGNOSE (pretty, non-fatal)


@app.command("diagnose")
def diagnose(ctx: typer.Context):
    """Check environment (tokens, Node/ts-morph, versions)."""
    state: GlobalState = ctx.obj
    _brand_header(state.console)
    _maybe_print_telemetry_note(state)

    def ok(b: bool) -> str:
        return ("✅ " if b else "⚠️  ") + ("[ok]OK[/ok]" if b else "[warn]MISSING[/warn]")

    table = Table(title="Environment", box=box.SIMPLE_HEAVY, expand=True, show_edge=True)
    table.add_column("Check", style="bold", no_wrap=True)
    table.add_column("Status")

    # Tokens
    gh = bool(os.getenv("GITHUB_TOKEN"))
    oa = bool(os.getenv("OPENAI_API_KEY"))
    gq = bool(os.getenv("GROQ_API_KEY"))
    table.add_row("GITHUB_TOKEN", ok(gh))
    table.add_row("OPENAI_API_KEY (optional)", ok(oa))
    table.add_row("GROQ_API_KEY (optional)", ok(gq))

    # Node + ts-morph
    node_ok = shutil.which("node") is not None
    ts_morph_ok = False
    if node_ok:
        try:
            subprocess.run(
                ["node", "-e", "require.resolve('ts-morph')"],
                check=True,
                capture_output=True,
                text=True,
                timeout=3,
            )
            ts_morph_ok = True
        except Exception:
            ts_morph_ok = False

    table.add_row("Node.js", ok(node_ok))
    table.add_row("ts-morph (optional)", ok(ts_morph_ok))
    table.add_row("prdoc version", f"[tag]{_version_str()}[/tag]")

    tips = []
    if not gh:
        tips.append("Set [tag]GITHUB_TOKEN[/tag] in your shell / CI.")
    if node_ok and not ts_morph_ok:
        tips.append("Install [tag]ts-morph[/tag] in your repo (e.g. `npm i -D ts-morph`).")
    if not node_ok:
        tips.append("Install Node.js for AST-powered search (optional).")

    content = Group(table, Panel("\n".join(tips) or "All set ✅", title="Tips", box=box.ROUNDED))
    state.console.print(Panel(content, box=box.ROUNDED))
    raise typer.Exit(0)


# SYNC


@app.command("sync")
def sync_cmd(
    instruction: Annotated[
        str,
        typer.Option(
            ...,
            "--instruction",
            "-i",
            help="Desired doc update in natural language.",
        ),
    ],
    path: Annotated[
        Optional[List[str]],
        typer.Option(
            "--path",
            "-p",
            help="One or more doc file paths to include. Repeat flag for multiple. (Dry-run only)",
        ),
    ] = None,
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-r",
            help="LLM provider: openai|groq",
        ),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Override model ID.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Verbose logging to stderr.",
        ),
    ] = False,
):
    """
    Orchestrate stages 1–5 and print planned patches (dry-run).
    For Step 6.1 we accept explicit --path inputs rather than reading PR context.
    """
    if not path:
        raise typer.BadParameter("at least one --path is required for now")

    # Load repo/env config and apply precedence
    cfg = load_config(Path.cwd())
    final_provider = provider if provider is not None else cfg.provider
    final_model = model if model is not None else cfg.model
    final_verbose = bool(verbose or cfg.verbose)

    if final_verbose:
        print(
            f"[prdoc] provider={final_provider} model={final_model or '(default)'}", file=sys.stderr
        )
        print(f"[prdoc] instruction={instruction}", file=sys.stderr)
        for p in path:
            print(f"[prdoc] include: {p}", file=sys.stderr)

    llm = build_llm(final_provider, final_model)
    gen = PatchGenerator(llm)

    hits = read_hits_from_paths(path)
    results = gen.generate_for_hits(hits, instruction=instruction)

    if not results:
        typer.echo("No changes suggested. (All files unchanged)")
        raise typer.Exit(code=0)

    # Print each patch with a clear separator
    for idx, res in enumerate(results, start=1):
        if idx > 1:
            typer.echo("\n" + "=" * 72 + "\n")
        typer.echo(f"# Patch for {res.path}\n")
        typer.echo(res.patch.rstrip("\n"))

    raise typer.Exit(code=0)


_PATH_HEADER_RE = re.compile(r"^#\s*Patch\s+for\s+(.+)\s*$")


def _extract_paths_from_sync_output(patch_text: str) -> List[str]:
    """Collect human headers like `# Patch for path` to summarize planned changes."""
    paths: List[str] = []
    for line in patch_text.splitlines():
        m = _PATH_HEADER_RE.match(line)
        if m:
            paths.append(m.group(1).strip())
    return paths


def _run(
    cmd: List[str], cwd: Optional[Path] = None, allow_fail: bool = False
) -> subprocess.CompletedProcess:
    """Run a subprocess and return CompletedProcess."""
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0 and not allow_fail:
        msg = f"command failed: {' '.join(cmd)}\n{proc.stderr.strip()}"
        raise typer.BadParameter(msg)
    return proc


def _git_root_or_none(start: Path) -> Optional[Path]:
    """Return the git repository root directory if inside a repo; else None."""
    try:
        proc = _run(["git", "rev-parse", "--show-toplevel"], cwd=start, allow_fail=True)
        if proc.returncode == 0:
            return Path(proc.stdout.strip())
        return None
    except Exception:
        return None


def _list_remotes(cwd: Path) -> List[str]:
    proc = _run(["git", "remote"], cwd=cwd, allow_fail=True)
    if proc.returncode != 0:
        return []
    remotes = [r.strip() for r in proc.stdout.splitlines() if r.strip()]
    return remotes


# APPLY


@app.command("apply")
def apply_cmd(
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Apply patch, commit, and push without interactive confirmation.",
        ),
    ] = False,
    message: Annotated[
        str,
        typer.Option(
            "--message",
            "-m",
            "--commit-msg",  # alias to support new wording
            help="Commit message to use.",
        ),
    ] = "prdoc: apply doc updates",
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Verbose logging to stderr.",
        ),
    ] = False,
):
    """
    Read unified diff from STDIN, apply it (git apply), commit, and push.
    Skips push if no git remote exists.
    """
    patch_text = sys.stdin.read()
    if not patch_text.strip():
        raise typer.BadParameter("no patch data provided on STDIN")

    # Determine repo root
    cwd = Path.cwd()
    repo_root = _git_root_or_none(cwd)
    if not repo_root:
        raise typer.BadParameter("not inside a git repository (git rev-parse failed)")

    # Friendly summary
    paths = _extract_paths_from_sync_output(patch_text) or []
    if paths:
        typer.echo("Files with planned changes:")
        for p in paths:
            typer.echo(f"  - {p}")
    else:
        typer.echo("No human-readable path headers found; proceeding to apply raw patch.")

    if not yes:
        if not typer.confirm("Apply patch, commit, and push?"):
            typer.echo("Aborted.")
            raise typer.Exit(code=1)

    # Apply patch using git (to working tree), then stage explicitly.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".patch", delete=True) as tf:
        tf.write(patch_text)
        tf.flush()
        if verbose:
            print(f"[prdoc] applying patch: {tf.name}", file=sys.stderr)
        _run(["git", "apply", "-p0", tf.name], cwd=repo_root)

    # Stage and commit
    if verbose:
        print("[prdoc] staging changes…", file=sys.stderr)
    _run(["git", "add", "-A"], cwd=repo_root)

    status = _run(["git", "diff", "--cached", "--name-only"], cwd=repo_root)
    if not status.stdout.strip():
        raise typer.BadParameter("patch applied but nothing to commit (no staged changes)")

    if verbose:
        print(f"[prdoc] committing with message: {message}", file=sys.stderr)
    _run(["git", "commit", "-m", message], cwd=repo_root)

    # Push if remote exists
    remotes = _list_remotes(repo_root)
    if remotes:
        if verbose:
            print(f"[prdoc] pushing to '{remotes[0]}'", file=sys.stderr)
        push_res = _run(["git", "push"], cwd=repo_root, allow_fail=True)
        if push_res.returncode != 0:
            _run(["git", "push", remotes[0], "HEAD"], cwd=repo_root, allow_fail=True)
    else:
        typer.echo("No git remotes found; committed locally and skipped push.")

    typer.echo("Apply + commit complete.")
    raise typer.Exit(0)


# Click entry point compatibility
click_app = typer.main.get_command(app)


def main():
    app()


if __name__ == "__main__":
    main()
