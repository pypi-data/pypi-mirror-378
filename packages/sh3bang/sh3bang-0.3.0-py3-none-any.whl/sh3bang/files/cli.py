from pathlib import Path

import typer

from .converter import docx_to_pdf, pdf_to_docx
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


@app.command()
def convert(
    input_file: str = typer.Argument(..., help="Input file path"),
    output_file: str = typer.Argument(..., help="Output file path"),
):
    """
    Convert between PDF <-> DOCX.
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    if input_file.suffix.lower() == ".pdf" and output_file.suffix.lower() == ".docx":
        typer.echo(f"Coverting PDF -> DOCX: {input_file} -> {output_file}")
        pdf_to_docx(str(input_file), str(output_file))
        typer.echo("Conversion complete.")

    elif input_file.suffix.lower() == ".docx" and output_file.suffix.lower() == ".pdf":
        typer.echo(f"Converting DOCX -> PDF: {input_file} -> {output_file}")
        docx_to_pdf(str(input_file), str(output_file))
        typer.echo("Conversion complete.")

    else:
        typer.echo("Unsupported conversion. Use PDF->DOCX OR DOCX->PDF only.")
