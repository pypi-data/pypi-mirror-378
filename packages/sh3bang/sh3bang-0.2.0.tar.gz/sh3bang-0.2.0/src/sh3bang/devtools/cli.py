import typer
from . import envreader, portcheck, reqcheck

app = typer.Typer(help="Developer tools for productivity")


# -----------------
# Devtools Commands
# -----------------

@app.command()
def env(file: str = ".env"):
    """Read and display environment variables from a .env file."""
    env_vars = envreader.read_env(file)
    for k, v in env_vars.items():
        typer.echo(f"{k}={v}")

@app.command()
def port(
    host: str = typer.Argument("127.0.0.1", help="Host to check"),
    port: int = typer.Argument(22, help="Port number to check")
    ):
    """Check if a port is open on a given host"""
    status = portcheck.check_port(host=host, port=port)
    typer.echo(f"Port {port} on {host} is {'OPEN' if status else 'CLOSED'}")

@app.command()
def reqs(file: str="requirements.txt"):
    """Check missing Python packages from requirements.txt"""
    missing = reqcheck.check_requirements(file)
    if not missing:
        typer.secho("Missing packages:", fg=typer.colors.RED)
        for pkg in missing:
            typer.echo(f" - {pkg}")
