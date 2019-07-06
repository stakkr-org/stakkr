#!/usr/bin/env python
# coding: utf-8
"""
CLI Entry Point.

From click, build stakkr.
Give all options to manage services to be launched, stopped, etc.
"""

import sys
import click
from click.core import Context
from stakkr.docker_actions import get_running_containers_names
from stakkr.aliases import get_aliases


@click.group(help="""Main CLI Tool that easily create / maintain
a stack of services, for example for web development.

Read the configuration file and setup the required services by
linking and managing everything for you.""")
@click.version_option('4.1.3')
@click.option('--config', '-c', help='Set the configuration filename (stakkr.yml by default)')
@click.option('--debug/--no-debug', '-d', default=False)
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def stakkr(ctx: Context, config=None, debug=False, verbose=True):
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
def console(ctx: Context, container: str, user: str, tty: bool):
    """See command Help."""
    ctx.obj['STAKKR'].init_project()
    ctx.obj['CTS'] = get_running_containers_names(ctx.obj['STAKKR'].project_name)
    if ctx.obj['CTS']:
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
def exec_cmd(ctx: Context, user: str, container: str, command: tuple, tty: bool):
    """See command Help."""
    ctx.obj['STAKKR'].init_project()
    ctx.obj['CTS'] = get_running_containers_names(ctx.obj['STAKKR'].project_name)
    if ctx.obj['CTS']:
        click.Choice(ctx.obj['CTS']).convert(container, None, ctx)

    ctx.obj['STAKKR'].exec_cmd(container, _get_cmd_user(user, container), command, tty)


@stakkr.command(help="Restart all (or a single as CONTAINER) container(s)")
@click.argument('container', required=False)
@click.option('--pull', '-p', help="Force a pull of the latest images versions", is_flag=True)
@click.option('--recreate', '-r', help="Recreate all containers", is_flag=True)
@click.option('--proxy/--no-proxy', '-P', help="Restart the proxy", default=True)
@click.pass_context
def restart(ctx: Context, container: str, pull: bool, recreate: bool, proxy: bool):
    """See command Help."""
    print(click.style('[RESTARTING]', fg='green') + ' your stakkr services')
    try:
        ctx.invoke(stop, container=container, proxy=proxy)
    except Exception:
        pass

    ctx.invoke(start, container=container, pull=pull, recreate=recreate, proxy=proxy)


@stakkr.command(help="""List available services available for stakkr.yml
(with info if the service is enabled)""")
@click.pass_context
def services(ctx):
    """See command Help."""
    ctx.obj['STAKKR'].init_project()

    from stakkr.stakkr_compose import get_available_services

    print('Available services usable in stakkr.yml ', end='')
    print('({} = disabled) : '.format(click.style('✘', fg='red')))

    svcs = ctx.obj['STAKKR'].get_config()['services']
    enabled_svcs = [svc for svc, opts in svcs.items() if opts['enabled'] is True]
    available_svcs = get_available_services(ctx.obj['STAKKR'].project_dir)
    for available_svc in sorted(list(available_svcs.keys())):
        sign = click.style('✘', fg='red')
        if available_svc in enabled_svcs:
            version = svcs[available_svc]['version']
            sign = click.style(str(version), fg='green')

        print('  - {} ({})'.format(available_svc, sign))


@stakkr.command(help="""Download a pack of services from github (see github) containing services.
PACKAGE is the git url or package name.
NAME is the directory name to clone the repo.
""")
@click.argument('package', required=True)
@click.argument('name', required=False)
@click.pass_context
def services_add(ctx: Context, package: str, name: str):
    """See command Help."""
    from stakkr.services import install

    project_dir = _get_project_dir(ctx.obj['CONFIG'])
    services_dir = '{}/services'.format(project_dir)
    name = package if name is None else name
    success, message = install(services_dir, package, name)
    if success is False:
        click.echo(click.style(message, fg='red'))
        sys.exit(1)

    stdout_msg = 'Package "' + click.style(package, fg='green') + '" installed successfully'
    if message is not None:
        stdout_msg = click.style(message, fg='yellow')

    click.echo(stdout_msg)
    click.echo('Try ' + click.style('stakkr services', fg='green') + ' to see new available services')


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
def start(ctx: Context, container: str, pull: bool, recreate: bool, proxy: bool):
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
def stop(ctx: Context, container: str, proxy: bool):
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


def run_commands(ctx: Context, extra_args: tuple, tty: bool):
    """Run commands for a specific alias"""
    commands = ctx.obj['STAKKR'].get_config()['aliases'][ctx.command.name]['exec']
    for command in commands:
        user = command['user'] if 'user' in command else 'root'
        container = command['container']
        args = command['args'] + list(extra_args) if extra_args is not None else []

        ctx.invoke(exec_cmd, user=user, container=container, command=args, tty=tty)


def main():
    """Call the CLI Script."""
    try:
        for alias, conf in get_aliases().items():
            if conf is None:
                continue

            cmd_help = conf['description'] if 'description' in conf else 'No description'

            @stakkr.command(help=cmd_help, name=alias)
            @click.option('--tty/--no-tty', '-t/ ', is_flag=True, default=True, help="Use a TTY")
            @click.argument('extra_args', required=False, nargs=-1, type=click.UNPROCESSED)
            @click.pass_context
            def _f(ctx: Context, extra_args: tuple, tty: bool):
                """See command Help."""
                run_commands(ctx, extra_args, tty)

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
