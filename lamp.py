import click
import os
import subprocess
import sys

from click_plugins import with_plugins
from pkg_resources import iter_entry_points


# TODO Remplacer certaines options de configuration par @click.option('--uid', envvar='UID') ?
@with_plugins(iter_entry_points('lamp.plugins'))
@click.group(help="""Wrapper for Docker Compose that helps
to start / stop / get the status, etc .... of services.

Based on a configuration file located into conf/""")
@click.version_option('0.5')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def lamp(ctx, debug):
    from lib import lamp

    ctx.obj['DEBUG'] = debug
    ctx.obj['LAMP'] = lamp.Lamp(os.path.dirname(os.path.realpath(__file__)))


@lamp.command(help="""In case you don't use images but Git repos, run that command
to build your images.""")
@click.pass_context
def fullstart(ctx):
    print(click.style('Building required images ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.fullstart()
    print(click.style('Build done\n', fg='green'))


@lamp.command(help="Start the servers")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', help="Remove images once stopped (useful for some disk space consuming services)", is_flag=True)
@click.pass_context
def start(ctx, pull: bool, recreate: bool):
    print(click.style('Starting your lamp server ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.start(pull, recreate)
    print(click.style('lamp server has been started\n', fg='green'))

    lamp.display_services_ports()


@lamp.command(help="Stop the servers")
@click.pass_context
def stop(ctx):
    print(click.style('Stopping docker-lamp ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.stop()
    print(click.style('docker-lamp has been stopped.\n', fg='green'))


@lamp.command(help="Restart the servers")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', help="Remove images once stopped (useful for some disk space consuming services)", is_flag=True)
@click.pass_context
def restart(ctx, pull: bool, recreate: bool):
    print(click.style('Restarting docker-lamp ...', fg='green'))
    lamp = ctx.obj['LAMP']
    lamp.restart(pull, recreate)
    print(click.style('docker-lamp has been restarted.\n', fg='green'))

    lamp.display_services_ports()


@lamp.command(help="Display the list of running servers")
@click.pass_context
def status(ctx):
    lamp = ctx.obj['LAMP']
    lamp.status()


@lamp.command(help="Enter a VM")
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


@lamp.command(help="Run a command to a VM", context_settings=dict(ignore_unknown_options=True))
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


@lamp.command(help="Manage the DNS forwarder (only one per host)", name="dns")
@click.argument('action', required=True, type=click.Choice(['start', 'stop']))
@click.pass_context
def dns(ctx, action: str):
    lamp = ctx.obj['LAMP']
    lamp.manage_dns(action)

    if action == 'start':
        str_action = 'Starting'
    elif action == 'stop':
        str_action = 'Stopping'

    print(click.style('{} the DNS forwarder ...'.format(str_action), fg='green'))


@lamp.command(help="Run Phing with the build.xml file located in the current directory", name="phing")
@click.pass_context
def phing(ctx):
    lamp = ctx.obj['LAMP']
    lamp.phing()


@lamp.command(help='Launch that command if you install a new plugin', name="refresh-plugins")
def refresh_plugins():
    from subprocess import DEVNULL

    subprocess.check_call(['pip', 'install', '-e', '.'], stdout=DEVNULL)
    print(click.style('Plugins refreshed.\n', fg='green'))


def main():
    try:
        lamp(obj={})
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
        # raise e
        sys.exit(1)


if __name__ == '__main__':
    main()
