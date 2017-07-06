import click
import os
import subprocess
import sys

from click_plugins import with_plugins
from pkg_resources import iter_entry_points


# TODO Remplacer certaines options de configuration par @click.option('--uid', envvar='UID') ?
@with_plugins(iter_entry_points('marina.plugins'))
@click.group(help="""A recompose tool that uses docker compose to easily create / maintain
a stack of services, for example for web development.

Via a configuration file you can setup the required services and let marina
link and start everything for you.""")
@click.version_option('2.0')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def marina(ctx, debug):
    from lib import marina

    ctx.obj['DEBUG'] = debug
    ctx.obj['MARINA'] = marina.Marina(os.path.dirname(os.path.realpath(__file__)))


@marina.command(help="""In case you don't use images but Git repos, run that command
to build your images.""")
@click.pass_context
def fullstart(ctx):
    print(click.style('Building required images ...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.fullstart()
    print(click.style('Build done\n', fg='green'))


@marina.command(help="Start services defined in compose.ini")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', help="Remove images once stopped (useful for some disk space consuming services)", is_flag=True)
@click.pass_context
def start(ctx, pull: bool, recreate: bool):
    print(click.style('Starting your marina services ...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.start(pull, recreate)
    print(click.style('marina services have been started\n', fg='green'))

    marina.display_services_ports()


@marina.command(help="Stop the services")
@click.pass_context
def stop(ctx):
    print(click.style('Stopping marina services...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.stop()
    print(click.style('marina services have been stopped.\n', fg='green'))


@marina.command(help="Restart the servers")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', help="Recreate all containers", is_flag=True)
@click.pass_context
def restart(ctx, pull: bool, recreate: bool):
    print(click.style('Restarting marina services ...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.restart(pull, recreate)
    print(click.style('marina services have been restarted.\n', fg='green'))

    marina.display_services_ports()


@marina.command(help="Display the list of running services")
@click.pass_context
def status(ctx):
    marina = ctx.obj['MARINA']
    marina.status()


@marina.command(help="Enter a Container (apache, mysql or php)")
@click.pass_context
@click.option('--user', help="User's name", type=click.Choice(['www-data', 'root']))
@click.argument('vm', required=True, type=click.Choice(['apache', 'mysql', 'php']))
def console(ctx, vm: str, user: str):
    if vm in ['php', 'apache'] and user is None:
        user = 'www-data'
    elif vm not in ['php', 'apache'] and user == 'www-data':
        user = 'root'
    elif user is None:
        user = 'root'

    marina = ctx.obj['MARINA']
    marina.console(vm, user)


@marina.command(help="Run a command to a VM", context_settings=dict(ignore_unknown_options=True))
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
    marina = ctx.obj['MARINA']
    if vm == 'php':
        marina.run_php(user, run_args)
    elif vm == 'mysql':
        marina.run_mysql(run_args)


@marina.command(help="Manage the DNS forwarder", name="dns")
@click.argument('action', required=True, type=click.Choice(['start', 'stop']))
@click.pass_context
def dns(ctx, action: str):
    marina = ctx.obj['MARINA']

    if action == 'start':
        str_action = 'Starting'
    elif action == 'stop':
        str_action = 'Stopping'

    print(click.style('{} the DNS forwarder ...'.format(str_action), fg='green'))
    marina.manage_dns(action)


@marina.command(help='Launch that command if you install a new plugin', name="refresh-plugins")
def refresh_plugins():
    from subprocess import DEVNULL

    subprocess.check_call(['pip', 'install', '-e', '.'], stdout=DEVNULL)
    print(click.style('Plugins refreshed.\n', fg='green'))


def main():
    try:
        marina(obj={})
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
