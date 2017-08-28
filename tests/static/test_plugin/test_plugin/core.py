"""
Test Plugin
"""

import click


@click.command(help="""For testing purpose""", name="hello-world")
@click.pass_context
def my_test(ctx):
    print('Hello test !')
