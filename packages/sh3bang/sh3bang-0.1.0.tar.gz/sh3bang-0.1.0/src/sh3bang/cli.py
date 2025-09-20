import typer

from sh3bang.automation import url_shortener
from sh3bang.files import renamer

app = typer.Typer(help="sh3bang - personal CLI")

files_app = typer.Typer(help="File & folder utilities")
auto_app = typer.Typer(help="Automation utilities")

app.add_typer(files_app, name="files")
app.add_typer(auto_app, name="auto")


# --------------
# Files Commands
# --------------
@auto_app.command("rename")
def rename(
    folder: str,
    prefix: str = typer.Option("", help="Optional prefix for filenames"),
    dry_run: bool = typer.Option(
        False, help="Show what would be renamed without making changes"
    ),
):
    """Rename files in a folder (replace spaces, add optional prefix)."""
    renamer.rename_files(folder, prefix, dry_run)


if __name__ == "__main__":
    app()
