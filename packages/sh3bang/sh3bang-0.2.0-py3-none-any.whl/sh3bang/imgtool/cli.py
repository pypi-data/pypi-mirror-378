import typer

from . import core

app = typer.Typer(help="imgtool - A simple image processing CLI tool")


@app.command()
def resize(
    input: str = typer.Argument(..., help="Input image path"),
    output: str = typer.Argument(..., help="Output image path"),
    width: int = typer.Option(..., help="New width"),
    height: int = typer.Option(..., help="New height"),
):
    """Resize an image to WIDTH x HEIGHT"""
    core.resize_image(input, output, width, height)
    typer.echo(f"Resized image saved to {output}")


@app.command()
def convert(
    input: str = typer.Argument(..., help="Input image path"),
    output: str = typer.Argument(..., help="Output image path"),
    format: str = typer.Option(..., help="Output format (png, jpeg, etc.)"),
):
    """Convert image to another format"""
    core.convert_format(input, output, format)
    typer.echo(f"Image convert and saved to {output}")


@app.command()
def info(
    input: str = typer.Argument(..., help="input image path"),
):
    """Show image info (format, mode, size)"""
    info = core.get_info(input)
    typer.echo(f"Format: {info['format']}, Mode: {info['mode']}, Size: {info['size']}")
