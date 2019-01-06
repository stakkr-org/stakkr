#!/usr/bin/env python
# coding: utf-8
"""
CLI Entry Point.

From click, build stakkr.
Give all options to manage services to be launched, stopped, etc.
"""

import sys
import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from stakkr.docker_actions import get_running_containers_names


@with_plugins(iter_entry_points('stakkr.plugins'))
@click.group(help="""Main CLI Tool that easily create / maintain
a stack of services, for example for web development.

Read the configuration file and setup the required services by
linking and managing everything for you.""")
@click.version_option('4.0b1')
@click.option('--config', '-c', help='Change the configuration file')
@click.option('--debug/--no-debug', '-d', default=False)
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def stakkr(ctx, config, debug, verbose):
    """Click group, set context and main object."""
    from stakkr.actions import StakkrActions

    ctx.obj['CONFIG'] = config
    ctx.obj['DEBUG'] = debug
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['STAKKR'] = StakkrActions(ctx.obj)


@stakkr.command(help="""Enter a container to perform direct actions such as
install packages, run commands, etc.""")
@click.argument('container', required=True)
@click.option('--user', '-u', help="User's name. Valid choices : www-data or root")
@click.option('--tty/--no-tty', '-t/ ', is_flag=True, default=True, help="Use a TTY")
@click.pass_context
def console(ctx, container: str, user: str, tty: bool):
    """See command Help."""
    ctx.obj['STAKKR'].init_project()
    ctx.obj['CTS'] = get_running_containers_names(ctx.obj['STAKKR'].project_name)
    if len(ctx.obj['CTS']) is not 0:
        ct_choice = click.Choice(ctx.obj['CTS'])
        ct_choice.convert(container, None, ctx)

    ctx.obj['STAKKR'].console(container, _get_cmd_user(user, container), tty)


@stakkr.command(help="""Execute a command into a container.

Examples:\n
- ``stakkr -v exec mysql mysqldump -p'$MYSQL_ROOT_PASSWORD' mydb > /tmp/backup.sql``\n
- ``stakkr exec php php -v`` : Execute the php binary in the php container with option -v\n
- ``stakkr exec apache service apache2 restart``\n
""", name='exec', context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False))
@click.pass_context
@click.option('--user', '-u', help="User's name. Be careful, each container have its own users.")
@click.option('--tty/--no-tty', '-t/ ', is_flag=True, default=True, help="Use a TTY")
@click.argument('container', required=True)
@click.argument('command', required=True, nargs=-1, type=click.UNPROCESSED)
def exec_cmd(ctx, user: str, container: str, command: tuple, tty: bool):
    """See command Help."""
    ctx.obj['STAKKR'].init_project()
    ctx.obj['CTS'] = get_running_containers_names(ctx.obj['STAKKR'].project_name)
    if len(ctx.obj['CTS']) is not 0:
        click.Choice(ctx.obj['CTS']).convert(container, None, ctx)

    ctx.obj['STAKKR'].exec_cmd(container, _get_cmd_user(user, container), command, tty)


@stakkr.command(help="""`stakkr mysql` is a wrapper for the mysql binary
located in the mysql service.

You can run any mysql command as root, such as :\n
- ``stakkr mysql -e "CREATE DATABASE mydb"`` to create a DB from outside\n
- ``stakkr mysql`` to enter the mysql console\n
- ``cat myfile.sql | stakkr mysql --no-tty mydb`` to import a file from outside to mysql\n

For scripts, you must use the relative path.
""", context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False))
@click.pass_context
@click.option('--tty/--no-tty', '-t/ ', is_flag=True, default=True, help="Use a TTY")
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def mysql(ctx, tty: bool, command: tuple):
    """See command Help."""
    command = ('mysql', '-p$MYSQL_ROOT_PASSWORD') + command
    ctx.invoke(exec_cmd, user='root', container='mysql', command=command, tty=tty)


@stakkr.command(help='Required to be launched if you install a new plugin', name="refresh-plugins")
@click.pass_context
def refresh_plugins(ctx):
    """See command Help."""
    from stakkr.plugins import add_plugins

    print(click.style('Not implemented yet in v4', fg='red'))
    exit(1)

    print(click.style('Adding plugins from plugins/', fg='green'))
    plugins = add_plugins()
    if len(plugins) is 0:
        print(click.style('No plugin to add', fg='yellow'))
        exit(0)

    print()
    print(click.style('Plugins refreshed', fg='green'))


@stakkr.command(help="Restart all (or a single as CONTAINER) container(s)")
@click.argument('container', required=False)
@click.option('--pull', '-p', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', '-r', help="Recreate all containers", is_flag=True)
@click.option('--proxy/--no-proxy', '-P', help="Restart the proxy", default=True)
@click.pass_context
def restart(ctx, container: str, pull: bool, recreate: bool, proxy: bool):
    """See command Help."""
    print(click.style('[RESTARTING]', fg='green') + ' your stakkr services')
    try:
        ctx.invoke(stop, container=container, proxy=proxy)
    except Exception:
        print()

    ctx.invoke(start, container=container, pull=pull, recreate=recreate, proxy=proxy)


@stakkr.command(help="List available services available for compose.ini (with info if the service is enabled)")
@click.pass_context
def services(ctx):
    """See command Help."""
    ctx.obj['STAKKR'].init_project()

    from stakkr.stakkr_compose import get_available_services

    print('Available services usable in stakkr.yml ', end='')
    print('({} = disabled) : '.format(click.style('✘', fg='red')))

    services = ctx.obj['STAKKR']._get_config()['services']
    enabled_services = [svc for svc, opts in services.items() if opts['enabled'] is True]
    available_services = get_available_services(ctx.obj['STAKKR'].project_dir)
    for available_service in sorted(list(available_services.keys())):
        sign = click.style('✘', fg='red')
        if available_service in enabled_services:
            version = services[available_service]['version']
            sign = click.style(str(version), fg='green')

        print('  - {} ({})'.format(available_service, sign))


@stakkr.command(help="Download a pack of services from github (see github) containing services")
@click.argument('package', required=True)
@click.pass_context
def services_add(ctx, package: str):
    """See command Help."""
    from stakkr.services import install

    project_dir = _get_project_dir(ctx.obj['CONFIG'])
    services_dir = '{}/services'.format(project_dir)
    success, message = install(services_dir, package)
    if success is False:
        click.echo(click.style(message, fg='red'))
        sys.exit(1)

    print(click.style(package, fg='green') + ' installed successfully')
    print('Try ' + click.style('stakkr services', fg='green') + ' to see new available services')


@stakkr.command(help="Update all services packs in services/")
@click.pass_context
def services_update(ctx):
    """See command Help."""
    from stakkr.services import update_all

    project_dir = _get_project_dir(ctx.obj['CONFIG'])
    services_dir = '{}/services'.format(project_dir)
    update_all(services_dir)
    print(click.style('Packages updated', fg='green'))


@stakkr.command(help="Start all (or a single as CONTAINER) container(s) defined in compose.ini")
@click.argument('container', required=False)
@click.option('--pull', '-p', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', '-r', help="Recreate all containers", is_flag=True)
@click.option('--proxy/--no-proxy', '-P', help="Start proxy", default=True)
@click.pass_context
def start(ctx, container: str, pull: bool, recreate: bool, proxy: bool):
    """See command Help."""
    print(click.style('[STARTING]', fg='green') + ' your stakkr services')

    ctx.obj['STAKKR'].start(container, pull, recreate, proxy)
    _show_status(ctx)


@stakkr.command(help="Display a list of running containers")
@click.pass_context
def status(ctx):
    """See command Help."""
    ctx.obj['STAKKR'].status()


@stakkr.command(help="Stop all (or a single as CONTAINER) container(s)")
@click.argument('container', required=False)
@click.option('--proxy/--no-proxy', '-P', help="Stop the proxy", default=True)
@click.pass_context
def stop(ctx, container: str, proxy: bool):
    """See command Help."""
    print(click.style('[STOPPING]', fg='yellow') + ' your stakkr services')
    ctx.obj['STAKKR'].stop(container, proxy)


def _get_cmd_user(user: str, container: str):
    users = {'apache': 'www-data', 'nginx': 'www-data', 'php': 'www-data'}

    cmd_user = 'root' if user is None else user
    if container in users and user is None:
        cmd_user = users[container]

    return cmd_user


def _show_status(ctx):
    services_ports = ctx.obj['STAKKR'].get_services_urls()
    if services_ports == '':
        print('\nServices Status:')
        ctx.invoke(status)
        return

    print('\nServices URLs :')
    print(services_ports)


def _get_project_dir(config: str):
    from os.path import abspath, dirname

    if config is not None:
        config = abspath(config)
        return dirname(config)

    from stakkr.file_utils import find_project_dir
    return find_project_dir()


def debug_mode():
    """Guess if we are in debug mode, useful to display runtime errors."""
    if '--debug' in sys.argv or '-d' in sys.argv:
        return True

    return False


def main():
    """Call the CLI Script."""
    try:
        stakkr(obj={})
    except Exception as error:
        msg = click.style(r""" ______ _____  _____   ____  _____
|  ____|  __ \|  __ \ / __ \|  __ \
| |__  | |__) | |__) | |  | | |__) |
|  __| |  _  /|  _  /| |  | |  _  /
| |____| | \ \| | \ \| |__| | | \ \
|______|_|  \_\_|  \_\\____/|_|  \_\

""", fg='yellow')
        msg += click.style('{}'.format(error), fg='red')
        print(msg + '\n', file=sys.stderr)

        if debug_mode() is True:
            raise error

        sys.exit(1)


if __name__ == '__main__':
    main()
