"""Docker functions to get info about containers"""

from docker import APIClient, client
from docker.errors import NotFound


cts_info = dict()
docker_apiclient = APIClient()
docker_client = client.from_env()
running_cts = 0


def check_cts_are_running(project_name: str, config: str = None):
    """Throws an error if cts are not running"""

    global cts_info

    running_cts, cts_info = get_running_containers(project_name, config)
    if running_cts is 0:
        raise SystemError('Have you started your server with the start action ?')

    return (running_cts, cts_info)


def container_running(container: str):
    """Returns True if the container is running else False"""

    try:
        ct_data = docker_apiclient.inspect_container(container)

        return ct_data['State']['Running']
    except Exception:
        return False


def get_ct_item(compose_name: str, item_name: str):
    """Get a value from a container, such as name or IP"""
    for ct_id, ct_data in cts_info.items():
        if ct_data['compose_name'] == compose_name:
            return ct_data[item_name]

    return ''


def get_ct_name(container: str):
    ct_name = get_ct_item(container, 'name')
    if ct_name == '':
        raise Exception('{} does not seem to be started ...'.format(container))

    return ct_name


def get_running_containers(project_name: str, config: str = None):
    """Get a list of IDs of running containers for the current stakkr instance"""

    filters = {
        'name': '{}_'.format(project_name),
        'network': '{}_stakkr'.format(project_name).replace('-', '')}

    cts = docker_client.containers.list(filters=filters)
    running_cts = len(cts)

    for ct in cts:
        cts_info[ct.id] = _extract_container_info(project_name, ct.id)

    return (running_cts, cts_info)


def _extract_container_info(project_name: str, ct_id: str):
    """Get a hash of info about a container : name, ports, image, ip ..."""

    try:
        ct_data = docker_apiclient.inspect_container(ct_id)
        ct_info = {
            'name': ct_data['Name'].lstrip('/'),
            'compose_name': ct_data['Config']['Labels']['com.docker.compose.service'],
            'ports': ct_data['Config']['ExposedPorts'].keys() if 'ExposedPorts' in ct_data['Config'] else [],
            'image': ct_data['Config']['Image'],
            'ip': _get_ip_from_networks(project_name, ct_data['NetworkSettings']['Networks']),
            'running': ct_data['State']['Running']
        }

        return ct_info
    except Exception as e:
        return None


def _get_ip_from_networks(project_name: str, networks: list):
    """Get a list of IPs for a network"""

    project_name = project_name.replace('-', '')
    network_settings = {}
    if '{}_stakkr'.format(project_name) in networks:
        network_settings = networks['{}_stakkr'.format(project_name)]

    return network_settings['IPAddress'] if 'IPAddress' in network_settings else ''


def create_network(network: str):
    """Create a Network"""

    if network_exists(network):
        return False

    return docker_client.networks.create(network, driver='bridge').id


def get_subnet(project_name: str):
    network_info = docker_client.networks.get(project_name.replace('-', '') + '_stakkr').attrs

    return network_info['IPAM']['Config'][0]['Subnet'].split('/')[0]


def get_switch_ip():
    import socket
    from subprocess import check_output

    cmd = r"""/bin/sh -c "ip addr show hvint0 | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}'" """
    res = docker_client.containers.run(
        'alpine', remove=True, tty=True, privileged=True, network_mode='host', pid_mode='host', command=cmd)
    ip = res.strip().decode()

    try:
        socket.inet_aton(ip)
        return ip
    except socket.error:
        raise ValueError('{} is not a valid ip, check docker is running')


def network_exists(network: str):
    try:
        docker_client.networks.get(network)
        return True
    except NotFound:
        return False


def add_container_to_network(container: str, network: str):
    """Attach a container to a network"""

    if _container_in_network(container, network) is True:
        return False

    docker_network = docker_client.networks.get(network)
    docker_network.connect(container)

    return True


def _container_in_network(container: str, expected_network: str):
    """Returns True if a container is in a network else false. Used by add_container_to_network"""

    try:
        ct_data = docker_apiclient.inspect_container(container)
    except Exception:
        raise SystemError('Container {} does not seem to exist'.format(container))

    for connected_network in ct_data['NetworkSettings']['Networks'].keys():
        if connected_network == expected_network:
            return True

    return False
