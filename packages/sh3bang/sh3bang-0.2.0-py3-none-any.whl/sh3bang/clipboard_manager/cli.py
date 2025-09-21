from datetime import datetime

import typer
from tabulate import tabulate

from . import core

app = typer.Typer(help="clipboard_manager CLI")


@app.command()
def watch(poll: float = 0.5, foreground: bool = False):
    """Start monitoring clipboard and saving history."""
    typer.echo("Starting clipboard watcher. Press Ctrl+C to stop (if foreground).")
    core.start_watcher(poll_interval=poll, foreground=foreground)


@app.command()
def save(text: str = typer.Argument(..., help="Text to save to clipboard and history")):
    core.save_text(text)
    typer.echo("Saved to history and copied to clipboard.")


@app.command()
def show(limit: int = 50):
    """Show recent clipboard history."""
    items = core.list_items(limit=limit)
    if not items:
        typer.echo("No history yet.")
        raise typer.Exit()
    table = [
        (row[0], row[2][:19], (row[1][:80] + ("..." if len(row[1]) > 80 else "")))
        for row in items
    ]
    try:
        typer.echo(tabulate(table, headers=["id", "when (UTC)", "text"]))
    except Exception:
        for r in table:
            typer.echo(f"[{r[0]}] {r[1]} {r[2]}")


@app.command()
def copy(
    clip_id: int = typer.Argument(
        ..., help="ID of the history item to copy back to clipboard"
    )
):
    ok = core.copy_item(clip_id)
    if not ok:
        typer.echo("Item not found.")
    else:
        typer.echo("Copied to clipboard.")


@app.command()
def clear(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirm clear history")
):
    if not confirm:
        typer.echo("Refusing to clear history. Pass --yes to confirm.")
        raise typer.Exit()
    core.clear_history()
    typer.echo("History cleared.")
