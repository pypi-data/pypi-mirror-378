import click
from .io import load_toy

@click.group()
def app():
    pass

@app.command()
def demo():
    ds = load_toy()
    click.echo(f'Loaded groups: {list(ds)}')

if __name__ == '__main__':
    app()
