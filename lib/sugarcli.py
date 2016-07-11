import os
import stat
import sys
import subprocess


def download_sugarcli(install_path: str):
    from urllib.request import urlretrieve
    # download sugarcli if it's not the case
    if os.path.isfile(install_path) is False:
        urlretrieve('http://apt.inetprocess.fr/pub/sugarcli.phar', install_path)
        os.chmod(install_path, stat.S_IRWXU)
        print('sugarcli has not been downloaded yet, downloading ...')


def run(vm_name: str, relative_dir: str, sugarcli_cmd: str):
    download_sugarcli('home/www-data/bin/sugarcli.phar')

    tty = 't' if sys.stdin.isatty() else ''
    cmd = ['docker', 'exec', '-u', 'www-data', '-i' + tty, vm_name]
    cmd += ['bash', '-c', '--']
    cmd += ['cd /var/' + relative_dir + '; exec /usr/bin/php ~/bin/sugarcli.phar ' + sugarcli_cmd]
    subprocess.call(cmd, stdin=sys.stdin, stderr=subprocess.STDOUT)


# To generate a token: https://files.inetprocess.fr/api/ecf9a003a50b156a927b06a177bd273f/keystore_generate_auth_token/docker_lamp
# or go to my account
def download_sugar_package(token, private, sugar_type, sugar_version):
    from lib import pydiodownload
    import uuid

    pydio_ws_url = 'https://files.inetprocess.fr/api/ecf9a003a50b156a927b06a177bd273f'

    if token is None or private is None:
        raise ValueError('To download Sugar you must set pydio.token and pydio.private in your compose.ini')

    try:
        file_name = pydiodownload.get_installation_file_url(pydio_ws_url, sugar_type, sugar_version, token, private)
    except IOError as e:
        raise ValueError('Check your Sugar type, version or your token / private: {}'.format(e))

    # download the file, run sugarcli
    tmp_output_file = 'www/SugarCRM-{}.zip'.format(uuid.uuid4())
    pydiodownload.get_raw_file(pydio_ws_url, file_name, token, private, tmp_output_file)

    return tmp_output_file
