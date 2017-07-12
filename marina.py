import click
import os
import subprocess
import sys

from click_plugins import with_plugins
from pkg_resources import iter_entry_points


# TODO Remplacer certaines options de configuration par @click.option('--uid', envvar='UID') ?
@with_plugins(iter_entry_points('marina.plugins'))
@click.group(help="""Main CLI Tool that easily create / maintain
a stack of services, for example for web development.

Read the configuration file and setup the required services by
linking and managing everything for you.""")
@click.version_option('2.0')
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def marina(ctx, debug):
    from lib import marina

    ctx.obj['DEBUG'] = debug
    ctx.obj['MARINA'] = marina.Marina(os.path.dirname(os.path.realpath(__file__)))


@marina.command(help="""Enter a container to perform direct actions such as install packages, run commands ...

Valid values for CONTAINER : 'apache', 'mysql' or 'php'""")
@click.option('--user', help="User's name. Valid choices : www-data or root", type=click.Choice(['www-data', 'root']))
@click.argument('container', required=True, type=click.Choice(['apache', 'mysql', 'php']))
@click.pass_context
def console(ctx, container: str, user: str):
    if container in ['php', 'apache'] and user is None:
        user = 'www-data'
    elif container not in ['php', 'apache'] and user == 'www-data':
        user = 'root'
    elif user is None:
        user = 'root'

    marina = ctx.obj['MARINA']
    marina.console(container, user)


@marina.command(
    help="""Start or Stop the DNS forwarder.
Only one DNS Forwarded by host is possible. Done with mgood/resolvable.

Valid values for ACTION : 'start' or 'stop'""",
    name="dns"
    )
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


@marina.command(help="In case you don't use images but Git repos, run that command to build your images.")
@click.pass_context
def fullstart(ctx):
    print(click.style('Building required images ...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.fullstart()
    print(click.style('Build done\n', fg='green'))


@marina.command(help='Required to be launched if you install a new plugin', name="refresh-plugins")
def refresh_plugins():
    from subprocess import DEVNULL
    from lib.plugins import get_plugins

    print('Will add to setup.py :')
    plugins = get_plugins()
    for plugin in plugins:
        print('  -> {}'.format(plugin.split('=')[0]))
    print()

    subprocess.check_call(['pip', 'install', '-e', '.'], stdout=DEVNULL)
    print(click.style('Plugins refreshed.\n', fg='green'))


@marina.command(help="Restart all containers")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', help="Recreate all containers", is_flag=True)
@click.pass_context
def restart(ctx, pull: bool, recreate: bool):
    print(click.style('Restarting marina services ...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.restart(pull, recreate)
    print(click.style('marina services have been restarted.\n', fg='green'))

    marina.display_services_ports()


@marina.command(
    help="""Run a command to a container.

Valid values for CONTAINER : 'mysql' or 'php'. You can add more arguments after the container name.

Examples:\n
- marina run php -v\n
- zcat dump.sql.gz | marina run mysql my_database\n
- marina run php www/myfile.php\n
""",
    context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.option('--user', '-u', help="User's name. Valid values: www-data or root", type=click.Choice(['www-data', 'root']))
@click.argument('container', required=True, type=click.Choice(['mysql', 'php']))
@click.argument('run_args', nargs=-1, type=click.UNPROCESSED)
def run(ctx, container: str, user: str, run_args: tuple):
    if container == 'php' and user is None:
        user = 'www-data'
    elif user is None:
        user = 'root'

    run_args = ' '.join(run_args)
    marina = ctx.obj['MARINA']
    if container == 'php':
        marina.run_php(user, run_args)
    elif container == 'mysql':
        marina.run_mysql(run_args)


@marina.command(help="Start containers defined in compose.ini")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option(
    '--recreate',
    help="Remove images once stopped (useful for containers that consumes spaces)",
    is_flag=True)
@click.pass_context
def start(ctx, pull: bool, recreate: bool):
    print(click.style('Starting your marina services ...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.start(pull, recreate)
    print(click.style('marina services have been started\n', fg='green'))

    marina.display_services_ports()


@marina.command(help="Display a list of running containers")
@click.pass_context
def status(ctx):
    marina = ctx.obj['MARINA']
    marina.status()


@marina.command(help="Stop the services")
@click.pass_context
def stop(ctx):
    print(click.style('Stopping marina services...', fg='green'))
    marina = ctx.obj['MARINA']
    marina.stop()
    print(click.style('marina services have been stopped.\n', fg='green'))


def debug_mode():
    if '--debug' in sys.argv:
        return True

    return False


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


        if debug_mode() is True:
            raise e

        sys.exit(1)


if __name__ == '__main__':
    main()
