import typer

from .renamer import rename_files

app = typer.Typer(help="File & folder utilities")

# --------------
# Files Commands
# --------------

@app.command()
def rename(
    folder: str,
    prefix: str = typer.Option("", help="Optional prefix for filenames"),
    dry_run: bool = typer.Option(
        False, help="Show what would be renamed without making changes"
    ),
):
    """Rename files in a folder (replace spaces, add optional prefix)."""
    rename_files(folder, prefix, dry_run)
