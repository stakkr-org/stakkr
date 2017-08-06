import click
import sys

from . import package_utils
from click_plugins import with_plugins
from pkg_resources import iter_entry_points


@with_plugins(iter_entry_points('stakkr.plugins'))
@click.group(help="""Main CLI Tool that easily create / maintain
a stack of services, for example for web development.

Read the configuration file and setup the required services by
linking and managing everything for you.""")
@click.version_option('3.0')
@click.option('--config', '-c', help='Change the configuration file')
@click.option('--debug/--no-debug', '-d', default=False)
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def stakkr(ctx, config, debug, verbose):
    from stakkr.actions import StakkrActions

    # Add the virtual env in the path
    venv_base = package_utils.get_venv_basedir()
    sys.path.append(venv_base)

    ctx.obj['CONFIG'] = config
    ctx.obj['DEBUG'] = debug
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['STAKKR'] = StakkrActions(venv_base, ctx.obj)


@stakkr.command(help="""Enter a container to perform direct actions such as install packages, run commands ...

Valid values for CONTAINER : 'apache', 'mysql' or 'php'""")
@click.option('--user', '-u', help="User's name. Valid choices : www-data or root",
              default='www-data',
              type=click.Choice(['www-data', 'root']))
@click.argument('container', required=True)
@click.pass_context
def console(ctx, container: str, user: str):
    cmd_user = None

    if container not in ['php', 'apache'] and user == 'www-data':
        cmd_user = 'root'
    elif cmd_user is None:
        cmd_user = user

    ctx.obj['STAKKR'].console(container, cmd_user)


@stakkr.command(
    help="""Start or Stop the DNS forwarder.
Only one DNS Forwarded by host is possible. Done with mgood/resolvable.
Also, that is completely useless under Windows as we can't mount /etc/resolv.conf

Valid values for ACTION : 'start' or 'stop'""",
    name="dns"
    )
@click.argument('action', required=True, type=click.Choice(['start', 'stop']))
@click.pass_context
def dns(ctx, action: str):
    print(click.style('[{}]'.format(action.upper()), fg='green') + ' DNS forwarder ...')
    ctx.obj['STAKKR'].manage_dns(action)


@stakkr.command(help="""Execute a command into a container.

Examples:\n
- ``stakkr -v exec mysql mysqldump -p'$MYSQL_ROOT_PASSWORD' mydb > /tmp/backup.sql``\n
- ``stakkr exec php php -v`` : Execute the php binary in the php container with option -v\n
- ``stakkr exec apache service apache2 restart``\n
""", context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.option('--user', '-u', help="User's name. Be careful, each container have its own users.")
@click.argument('container', required=True)
@click.argument('command', required=True, nargs=-1, type=click.UNPROCESSED)
def exec(ctx, user: str, container: str, command: tuple):
    users = {
        'php': 'www-data'
    }
    if user is None:
        user = users[container] if container in users else 'root'

    ctx.obj['STAKKR'].exec(container, user, command)


@stakkr.command(
    help="""`stakkr mysql` is a wrapper for the mysql binary located in the mysql service.

You can run any mysql command as root, such as :\n
- ``stakkr mysql -e "CREATE DATABASE mydb"`` to create a DB from outside\n
- ``stakkr mysql`` to enter the mysql console\n
- ``cat myfile.sql | stakkr mysql mydb`` to import a file from outside to mysql\n

For scripts, you must use the relative path.
""", context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def mysql(ctx, command: tuple):
    command = ('mysql', '-p$MYSQL_ROOT_PASSWORD') + command
    ctx.invoke(exec, user='root', container='mysql', command=command)


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
@click.option('--pull', '-p', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', '-r', help="Recreate all containers", is_flag=True)
@click.pass_context
def restart(ctx, pull: bool, recreate: bool):
    print(click.style('[RESTARTING]', fg='green') + ' your stakkr services')
    try:
        ctx.invoke(stop)
    except Exception:
        print()

    ctx.invoke(start, pull=pull, recreate=recreate)


@stakkr.command(help='DEPRECATED, USE `stakkr exec`', context_settings=dict(ignore_unknown_options=True))
@click.pass_context
@click.option('--user', '-u', help="User's name. Valid values: www-data or root", type=click.Choice(['www-data', 'root']))
@click.argument('container', required=True, type=click.Choice(['mysql', 'php']))
@click.argument('run_args', nargs=-1, type=click.UNPROCESSED)
def run(ctx, container: str, user: str, run_args: tuple):
    print(click.style('[DEPRECATED]', fg='red') + ' You must use either `stakkr mysql` or `stakkr exec php php`')


@stakkr.command(help="Start containers defined in compose.ini")
@click.option('--pull', help="Force a pull of the latest images versions", is_flag=True)
@click.option(
    '--recreate',
    help="Remove images once stopped (useful for containers that consumes spaces)",
    is_flag=True)
@click.pass_context
def start(ctx, pull: bool, recreate: bool):
    print(click.style('[STARTING]', fg='green') + ' your stakkr services')
    ctx.obj['STAKKR'].start(pull, recreate)
    services_ports = ctx.obj['STAKKR'].get_services_ports()
    if services_ports == '':
        print('\nServices Status:')
        ctx.invoke(status)
        return

    print('\nServices URLs :')
    print(services_ports)


@stakkr.command(help="Display a list of running containers")
@click.pass_context
def status(ctx):
    ctx.obj['STAKKR'].status()


@stakkr.command(help="Stop the services")
@click.pass_context
def stop(ctx):
    print(click.style('[STOPPING]', fg='yellow') + ' your stakkr services')
    ctx.obj['STAKKR'].stop()


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
        print(msg + '\n', file=sys.stderr)

        if debug_mode() is True:
            raise e

        sys.exit(1)


if __name__ == '__main__':
    main()
