import click
from rich import print as rprint
from contexter.core.ctx import ContexterCore


@click.group(help="Contexter — Prompt-first, Codex-only context pack generator")
def main():
    """Contexter CLI - Generate context packs for repositories using Codex."""
    pass


@main.command()
@click.option(
    "--config", "-c", type=click.Path(exists=False), help="Path to CONTEXTER.yaml"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run(config, verbose):
    """Prepare slices/manifest and master prompt; Codex writes packs."""
    core = ContexterCore(config_path=config, verbose=verbose)
    core.run()
    rprint(
        "[green]Prepared prompt at contexter/.prompt.txt. Paste into Codex and approve writes.[/green]"
    )


@main.command()
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
def init(force):
    """Initialize a repo with templates (CONTEXTER.yaml, PLAN.md, CI)."""
    from pathlib import Path
    from contexter.utils.files import write_text

    root = Path.cwd()
    templates = Path(__file__).parent.parent.parent / "templates"

    for name in ["CONTEXTER.yaml.template", "PLAN.md.template", ".gitignore.template"]:
        src = templates / name
        dest = root / name.replace(".template", "")

        if dest.exists() and not force:
            rprint(
                f"[yellow]Skipping {dest} (exists). Use --force to overwrite.[/yellow]"
            )
            continue

        if src.exists():
            write_text(dest, src.read_text(encoding="utf-8"))
            rprint(f"[green]Wrote {dest}[/green]")
        else:
            rprint(f"[red]Template {src} not found[/red]")

    rprint(
        "[green]Repo initialized. Edit CONTEXTER.yaml and run `contexter run`.[/green]"
    )


@main.command()
def version():
    """Show version information"""
    from contexter import __version__

    rprint(f"contexter-codex {__version__}")


@main.command()
@click.option(
    "--config", "-c", type=click.Path(exists=False), help="Path to CONTEXTER.yaml"
)
def config(config):
    """Print effective configuration"""
    from contexter.core.config import load_config
    import json

    try:
        cfg = load_config(config)
        rprint(json.dumps(cfg, indent=2))
    except Exception as e:
        rprint(f"[red]Error loading config: {e}[/red]")
