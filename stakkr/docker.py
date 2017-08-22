"""Docker functions to get info about containers"""

from docker import APIClient, client as DockerClient, utils, errors
from requests.exceptions import ConnectionError
cts_info = dict()
running_cts = 0

params = utils.kwargs_from_env()
base_url = None if 'base_url' not in params else params['base_url']
tls = None if 'tls' not in params else params['tls']
apiclient = APIClient(base_url=base_url, tls=tls)
client = DockerClient.from_env()


def block_ct_ports(service: str, ports: list, project_name: str) -> tuple:
    try:
        ct = client.containers.get(get_ct_item(service, 'id'))
    except Exception:
        return (False, '{} is not started, no port to block'.format(service))

    iptables = ct.exec_run(['which', 'iptables']).decode().strip()
    if iptables == '':
        return (True, "Can't block ports on {}, is iptables installed ?".format(service))

    _allow_contact_subnet(project_name, ct)

    # Now for each port, add an iptable rule
    for port in ports:
        try:
            ct.exec_run([iptables, '-D', 'OUTPUT', '-p', 'tcp', '--dport', port, '-j', 'REJECT'])
        finally:
            ct.exec_run([iptables, '-A', 'OUTPUT', '-p', 'tcp', '--dport', port, '-j', 'REJECT'])

    return (False, 'Blocked ports {} on container {}'.format(', '.join(ports), service))


def check_cts_are_running(project_name: str, config: str = None):
    """Throws an error if cts are not running"""

    global cts_info

    running_cts, cts_info = get_running_containers(project_name)
    if running_cts is 0:
        raise SystemError('Have you started your server with the start action ?')

    return (running_cts, cts_info)


def container_running(container: str):
    """Returns True if the container is running else False"""

    try:
        ct_data = apiclient.inspect_container(container)

        return ct_data['State']['Running']
    except Exception:
        return False


def get_ct_item(compose_name: str, item_name: str):
    """Get a value from a container, such as name or IP"""

    if len(cts_info) is 0:
        raise RuntimeError('Before getting an info from a ct, run check_cts_are_running()')

    for ct_id, ct_data in cts_info.items():
        if ct_data['compose_name'] == compose_name:
            return ct_data[item_name]

    return ''


def get_ct_name(container: str):
    ct_name = get_ct_item(container, 'name')
    if ct_name == '':
        raise Exception('{} does not seem to be started ...'.format(container))

    return ct_name


def get_running_containers(project_name: str) -> tuple:
    """Get the number of running containers and theirs details for the current stakkr instance"""

    filters = {
        'name': '{}_'.format(project_name),
        'status': 'running',
        'network': '{}_stakkr'.format(project_name).replace('-', '')}

    try:
        cts = client.containers.list(filters=filters)
    except ConnectionError:
        raise Exception('Make sure docker is installed and running')

    for ct in cts:
        container_info = _extract_container_info(project_name, ct.id)
        cts_info[container_info['name']] = container_info

    return (len(cts), cts_info)


def get_running_containers_name(project_name: str) -> list:
    """Get a list of compose names of running containers for the current stakkr instance"""

    num_cts, cts = get_running_containers(project_name)

    return sorted([ct_data['compose_name'] for docker_name, ct_data in cts.items()])


def guess_shell(service: str):
    ct = client.containers.get(get_ct_item(service, 'id'))

    shells = ct.exec_run('which -a bash sh', stdout=True, stderr=False).splitlines()
    if b'/bin/bash' in shells:
        return '/bin/bash'
    elif b'/bin/sh' in shells:
        return '/bin/sh'

    raise EnvironmentError('Could not find a shell for that container')


def _extract_container_info(project_name: str, ct_id: str):
    """Get a hash of info about a container : name, ports, image, ip ..."""

    try:
        ct_data = apiclient.inspect_container(ct_id)
        ct_info = {
            'id': ct_id,
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

    return client.networks.create(network, driver='bridge').id


def get_subnet(project_name: str):
    network_info = client.networks.get(project_name.replace('-', '') + '_stakkr').attrs

    return network_info['IPAM']['Config'][0]['Subnet'].split('/')[0]


def get_switch_ip():
    import socket

    cmd = r"""/bin/sh -c "ip addr show hvint0 | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}'" """
    res = client.containers.run(
        'alpine', remove=True, tty=True, privileged=True, network_mode='host', pid_mode='host', command=cmd)
    ip = res.strip().decode()

    try:
        socket.inet_aton(ip)
        return ip
    except socket.error:
        raise ValueError('{} is not a valid ip, check docker is running')


def network_exists(network: str):
    try:
        client.networks.get(network)
        return True
    except errors.NotFound:
        return False


def add_container_to_network(container: str, network: str):
    """Attach a container to a network"""

    if _container_in_network(container, network) is True:
        return False

    docker_network = client.networks.get(network)
    docker_network.connect(container)

    return True


def _allow_contact_subnet(project_name: str, ct) -> None:
    iptables = ct.exec_run(['which', 'iptables']).decode().strip()
    if iptables == '':
        return False

    subnet = get_subnet(project_name) + '/24'
    # Allow internal network
    try:
        ct.exec_run([iptables, '-D', 'OUTPUT', '-d', subnet, '-j', 'ACCEPT'])
    finally:
        ct.exec_run([iptables, '-A', 'OUTPUT', '-d', subnet, '-j', 'ACCEPT'])


def _container_in_network(container: str, expected_network: str):
    """Returns True if a container is in a network else false. Used by add_container_to_network"""

    try:
        ct_data = apiclient.inspect_container(container)
    except Exception:
        raise SystemError('Container {} does not seem to exist'.format(container))

    for connected_network in ct_data['NetworkSettings']['Networks'].keys():
        if connected_network == expected_network:
            return True

    return False
