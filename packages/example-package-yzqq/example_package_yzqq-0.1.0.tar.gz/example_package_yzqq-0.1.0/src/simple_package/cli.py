"""
Command line interface for the simple package.
"""

import click
from .core import Calculator, greet
from .utils import format_number


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Simple Package CLI - A demonstration of packaging with uv."""
    pass


@main.command()
@click.option('--name', default='World', help='Name to greet')
def hello(name):
    """Say hello to someone."""
    message = greet(name)
    click.echo(message)


@main.command()
@click.argument('a', type=float)
@click.argument('b', type=float)
@click.option('--operation', '-o', 
              type=click.Choice(['add', 'subtract', 'multiply', 'divide']),
              default='add', help='Mathematical operation to perform')
def calc(a, b, operation):
    """Perform basic mathematical operations."""
    calculator = Calculator()
    
    try:
        if operation == 'add':
            result = calculator.add(a, b)
        elif operation == 'subtract':
            result = calculator.subtract(a, b)
        elif operation == 'multiply':
            result = calculator.multiply(a, b)
        elif operation == 'divide':
            result = calculator.divide(a, b)
        
        formatted_result = format_number(result)
        click.echo(f"Result: {formatted_result}")
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()