import click
import os
import sys

from lib import lamp


# TODO Utiliser click , virtualenv et setuptools
# TODO Remplacer certaines options de configuration par @click.option('--uid', envvar='UID') ?
# TODO Système de plugins avec https://github.com/click-contrib/click-plugins
sugar_types = ('Corporate', 'Developer', 'Enterprise', 'Professional', 'Ultimate')


@click.group(help="""Wrapper for Docker Compose that helps
to start / stop / get the status, etc .... of services.

Based on a configuration file located into conf/""")
@click.version_option('0.2')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj['DEBUG'] = debug
    ctx.obj['LAMP'] = lamp.Lamp(os.path.dirname(os.path.realpath(__file__)))


@cli.command(help="""In case you don't use images but Git repos, run that command
to build your images.""")
@click.pass_context
def fullstart(ctx):
    print(click.style('Building required images ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.fullstart()
    print(click.style('Build done\n', fg='green'))


@cli.command(help="Start the servers")
@click.pass_context
def start(ctx):
    print(click.style('Starting your lamp server ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.start()
    print(click.style('lamp server has been started\n', fg='green'))

    lamp.display_services_ports()


@cli.command(help="Stop the servers")
@click.pass_context
def stop(ctx):
    print(click.style('Stopping docker-lamp ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.stop()
    print(click.style('docker-lamp has been stopped.\n', fg='green'))


@cli.command(help="Restart the servers")
@click.pass_context
def restart(ctx):
    print(click.style('Restarting docker-lamp ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.restart()
    print(click.style('docker-lamp has been restarted.\n', fg='green'))


@cli.command(help="Display the list of running servers")
@click.pass_context
def status(ctx):
    lamp = ctx.obj['LAMP']
    lamp.status()


@cli.command(help="Enter a VM")
@click.pass_context
@click.option('--user', help="User's name", type=click.Choice(['www-data', 'root']))
@click.argument('vm', required=True, type=click.Choice(['mysql', 'php']))
def console(ctx, vm: str, user: str):
    if vm == 'php' and user is None:
        user = 'www-data'
    elif vm != 'php' and user == 'www-data':
        user = 'root'
    elif user is None:
        user = 'root'

    lamp = ctx.obj['LAMP']
    lamp.console(vm, user)


@cli.command(help="Run a command to a VM", context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.option('--user', '-u', help="User's name", type=click.Choice(['www-data', 'root']))
@click.argument('vm', required=True, type=click.Choice(['mysql', 'php']))
@click.argument('run_args', nargs=-1, type=click.UNPROCESSED)
def run(ctx, vm: str, user: str, run_args: tuple):
    if vm == 'php' and user is None:
        user = 'www-data'
    elif user is None:
        user = 'root'

    run_args = ' '.join(run_args)
    lamp = ctx.obj['LAMP']
    if vm == 'php':
        lamp.run_php(user, run_args)
    elif vm == 'mysql':
        lamp.run_mysql(run_args)


@cli.command(help="Run a sugarcli command", context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.argument('run_args', nargs=-1, type=click.UNPROCESSED)
def sugarcli(ctx, run_args: tuple):
    run_args = ' '.join(run_args)

    lamp = ctx.obj['LAMP']
    lamp.sugarcli(run_args)


@cli.command(help='Install SugarCRM', name='sugar-install')
@click.pass_context
@click.option('--sugar-type', '-s', required=True, help="SugarCRM Type", type=click.Choice(sugar_types))
@click.option('--version', required=True, help="SugarCRM Version (Example: 6.5.0)")
@click.option('--path', '-p', required=True, help="Where to install", type=click.Path())
@click.option('--demo-data', help="Install demo data", is_flag=True)
@click.option('--force', '-f', help="Remove an existing installation", is_flag=True)
def sugar_install(ctx, sugar_type: str, version: str, path: str, demo_data: bool, force: bool):
    lamp = ctx.obj['LAMP']
    lamp.sugar_install(sugar_type, version, path, demo_data, force)


def main():
    try:
        cli(obj={})
    except Exception as e:
        msg = click.style(r""" ______ _____  _____   ____  _____
|  ____|  __ \|  __ \ / __ \|  __ \
| |__  | |__) | |__) | |  | | |__) |
|  __| |  _  /|  _  /| |  | |  _  /
| |____| | \ \| | \ \| |__| | | \ \
|______|_|  \_\_|  \_\\____/|_|  \_\

""", fg='yellow')
        msg += click.style('{}'.format(e), fg='red')

        print(msg)
        print("")
        raise e
        sys.exit(1)


if __name__ == '__main__':
    main()
