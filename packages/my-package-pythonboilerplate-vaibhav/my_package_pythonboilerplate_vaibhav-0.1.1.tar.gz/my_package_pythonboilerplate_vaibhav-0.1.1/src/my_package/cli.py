import click
from . import __version__

@click.command()
@click.option("--name", "-n", default="World", help="Who to greet")
def hello(name: str) -> None:
    """Say hello from my_package."""
    click.echo(f"Hello, {name}! (from my_package {__version__})")

if __name__ == "__main__":
    hello()
