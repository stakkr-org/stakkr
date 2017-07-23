import click
import sys

from click_plugins import with_plugins
from . import package_utils
from pkg_resources import iter_entry_points


# TODO Remplacer certaines options de configuration par @click.option('--uid', envvar='UID') ?
@with_plugins(iter_entry_points('stakkr.plugins'))
@click.group(help="""Main CLI Tool that easily create / maintain
a stack of services, for example for web development.

Read the configuration file and setup the required services by
linking and managing everything for you.""")
@click.version_option('3.0')
@click.option('--verbose', '-v', is_flag=True)
@click.option('--debug/--no-debug', '-d', default=False)
@click.pass_context
def stakkr(ctx, verbose, debug):
    from stakkr.actions import StakkrActions

    # Add the virtual env in the path
    venv_base = package_utils.get_venv_basedir()
    sys.path.append(venv_base)

    ctx.obj['DEBUG'] = debug
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['STAKKR'] = StakkrActions(venv_base, ctx.obj)


@stakkr.command(help="""Enter a container to perform direct actions such as install packages, run commands ...

Valid values for CONTAINER : 'apache', 'mysql' or 'php'""")
@click.option('--user', help="User's name. Valid choices : www-data or root", type=click.Choice(['www-data', 'root']))
@click.argument('container', required=True, type=click.Choice(['apache', 'mysql', 'python', 'php']))
@click.pass_context
def console(ctx, container: str, user: str):
    if container in ['php', 'apache'] and user is None:
        user = 'www-data'
    elif container not in ['php', 'apache'] and user == 'www-data':
        user = 'root'
    elif user is None:
        user = 'root'

    stakkr = ctx.obj['STAKKR']
    stakkr.console(container, user)


@stakkr.command(
    help="""Start or Stop the DNS forwarder.
Only one DNS Forwarded by host is possible. Done with mgood/resolvable.

Valid values for ACTION : 'start' or 'stop'""",
    name="dns"
    )
@click.argument('action', required=True, type=click.Choice(['start', 'stop']))
@click.pass_context
def dns(ctx, action: str):
    stakkr = ctx.obj['STAKKR']

    if action == 'start':
        str_action = 'Starting'
    elif action == 'stop':
        str_action = 'Stopping'

    print(click.style('{} the DNS forwarder ...'.format(str_action), fg='green'))
    stakkr.manage_dns(action)


@stakkr.command(help="In case you don't use images but Git repos, run that command to build your images.")
@click.pass_context
def fullstart(ctx):
    print(click.style('Building required images ...', fg='green'))
    stakkr = ctx.obj['STAKKR']
    stakkr.fullstart()
    print(click.style('Build done\n', fg='green'))


@stakkr.command(help='Required to be launched if you install a new plugin', name="refresh-plugins")
@click.pass_context
def refresh_plugins(ctx):
    from stakkr.plugins import add_plugins

    print(click.style('Adding plugins from plugins/', fg='green'))
    plugins = add_plugins()
    if len(plugins) is 0:
        print(click.style('No plugin to add', fg='yellow'))
        exit(0)

    print()
    print(click.style('Plugins refreshed.\n', fg='green'))


@stakkr.command(help="Restart all containers")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', help="Recreate all containers", is_flag=True)
@click.pass_context
def restart(ctx, pull: bool, recreate: bool):
    print(click.style('Restarting stakkr services ...', fg='green'))
    stakkr = ctx.obj['STAKKR']
    stakkr.restart(pull, recreate)
    print(click.style('stakkr services have been restarted.\n', fg='green'))

    stakkr.display_services_ports()


@stakkr.command(
    help="""Run a command to a container.

Valid values for CONTAINER : 'mysql' or 'php'. You can add more arguments after the container name.

Examples:\n
- stakkr run php -v\n
- zcat dump.sql.gz | stakkr run mysql my_database\n
- stakkr run php www/myfile.php\n
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
    stakkr = ctx.obj['STAKKR']
    if container == 'php':
        stakkr.run_php(user, run_args)
    elif container == 'mysql':
        stakkr.run_mysql(run_args)


@stakkr.command(help="Start containers defined in compose.ini")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option(
    '--recreate',
    help="Remove images once stopped (useful for containers that consumes spaces)",
    is_flag=True)
@click.pass_context
def start(ctx, pull: bool, recreate: bool):
    print(click.style('Starting your stakkr services ...', fg='green'))
    stakkr = ctx.obj['STAKKR']
    stakkr.start(pull, recreate)
    print(click.style('stakkr services have been started\n', fg='green'))

    stakkr.display_services_ports()


@stakkr.command(help="Display a list of running containers")
@click.pass_context
def status(ctx):
    stakkr = ctx.obj['STAKKR']
    stakkr.status()


@stakkr.command(help="Stop the services")
@click.pass_context
def stop(ctx):
    print(click.style('Stopping stakkr services...', fg='green'))
    stakkr = ctx.obj['STAKKR']
    stakkr.stop()
    print(click.style('stakkr services have been stopped.\n', fg='green'))


def debug_mode():
    if '--debug' in sys.argv:
        return True

    return False


def main():
    try:
        stakkr(obj={})
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
