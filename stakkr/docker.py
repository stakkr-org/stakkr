"""Docker functions to get info about containers"""


from json import loads as json_loads
import subprocess


running_cts = 0
cts_info = dict()


def check_cts_are_running(project_name: str, config: str = None):
    """Throws an error if cts are not running"""

    global cts_info

    running_cts, cts_info = get_running_containers(project_name, config)
    if running_cts is 0:
        raise SystemError('Have you started your server with the start action ?')

    return (running_cts, cts_info)


def container_running(name: str):
    """Returns True if the container is running else False"""

    cmd = ['docker', 'inspect', '-f', '{{.State.Running}}', name]
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).splitlines()[0]
        return False if result.decode() == 'false' else True
    except subprocess.CalledProcessError as e:
        return False


def get_ct_item(compose_name: str, item_name: str):
    """Get a value from a container, such as name or IP"""
    for ct_id, ct_data in cts_info.items():
        if ct_data['compose_name'] == compose_name:
            return ct_data[item_name]

    return ''


def get_ct_name(ct: str):
    ct_name = get_ct_item(ct, 'name')
    if ct_name == '':
        raise Exception('{} does not seem to be started ...'.format(ct))

    return ct_name


def get_running_containers(project_name: str, config: str = None):
    """Get a list of IDs of running containers for the current stakkr instance"""

    global cts_info

    config_params = []
    if config is not None:
        config_params = ['-c', config]

    running_cts = 0
    cts_id = subprocess.check_output(['stakkr-compose'] + config_params + ['ps', '-q'])
    cts_info = dict()
    for ct_id in cts_id.splitlines():
        ct_id = ct_id.decode()
        cts_info[ct_id] = _extract_container_info(project_name, ct_id)

        if cts_info[ct_id]['running'] is True:
            running_cts += 1

    return (running_cts, cts_info)


def _extract_container_info(project_name: str, ct_id: str):
    """Get a hash of info about a container : name, ports, image, ip ..."""

    try:
        result = subprocess.check_output(['docker', 'inspect', ct_id], stderr=subprocess.STDOUT)
        ct_data = json_loads(result.decode().rstrip('\n'))

        ct_info = {
            'name': ct_data[0]['Name'].lstrip('/'),
            'compose_name': ct_data[0]['Config']['Labels']['com.docker.compose.service'],
            'ports': ct_data[0]['Config']['ExposedPorts'].keys() if 'ExposedPorts' in ct_data[0]['Config'] else [],
            'image': ct_data[0]['Config']['Image'],
            'ip': _get_ip_from_networks(project_name, ct_data[0]['NetworkSettings']['Networks']),
            'running': ct_data[0]['State']['Running'],
        }

        return ct_info
    except subprocess.CalledProcessError as e:
        return None


def _get_ip_from_networks(project_name: str, networks: list):
    """Get a list of IPs for a network"""

    network_settings = {}
    if '{}_stakkr'.format(project_name) in networks:
        network_settings = networks['{}_stakkr'.format(project_name)]

    return network_settings['IPAddress'] if 'IPAddress' in network_settings else ''


def create_network(network: str):
    """Create a Network"""

    if _network_exists(network) is True:
        return False

    cmd = ['docker', 'network', 'create', '--driver', 'bridge', network]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    return True


def add_container_to_network(container: str, network: str):
    """Attach a container to a network"""

    if _container_in_network(container, network) is True:
        return False

    cmd = ['docker', 'network', 'connect', network, container]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    return True


def _container_in_network(container: str, expected_network: str):
    """Returns True if a container is in a network else false. Used by add_container_to_network"""

    try:
        cmd = ['docker', 'inspect', container]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except Exception:
        raise SystemError('Container {} does not seem to exist'.format(container))

    ct_data = json_loads(result.decode().rstrip('\n'))
    for connected_network in ct_data[0]['NetworkSettings']['Networks'].keys():
        if connected_network == expected_network:
            return True

    return False


def _network_exists(network: str):
    """Returns True if a network exists. Used by create_network"""

    cmd = ['docker', 'network', 'ls', '--filter', 'name={}'.format(network)]
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    networks_list = result.decode().splitlines()
    if len(networks_list) > 1:
        return True

    return False
