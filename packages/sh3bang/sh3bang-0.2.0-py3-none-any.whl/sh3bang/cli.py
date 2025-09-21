import typer

from sh3bang.clipboard_manager.cli import app as clip_app
from sh3bang.files.cli import app as files_app
from sh3bang.imgtool.cli import app as imgtool_app

app = typer.Typer(help="sh3bang - personal CLI")

# Register subcommands
app.add_typer(files_app, name="files")
app.add_typer(clip_app, name="clip")
app.add_typer(imgtool_app, name="imgtool")

if __name__ == "__main__":
    app()
