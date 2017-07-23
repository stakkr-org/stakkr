"""Docker functions to get info about containers"""


from json import loads as json_loads
import subprocess


def container_running(name: str):
    """Returns True if the container is running else False"""

    cmd = ['docker', 'inspect', '-f', '{{.State.Running}}', name]
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).splitlines()[0]
        return False if result.decode() == 'false' else True
    except subprocess.CalledProcessError as e:
        return False


def get_running_containers(project_name: str):
    """Get a list of IDs of running containers for the current stakkr instance"""

    cmd = ['stakkr-compose', 'ps', '-q']
    vms_id = subprocess.check_output(cmd).splitlines()
    vms_info = dict()
    for vm_id in vms_id:
        vm_id = vm_id.decode('utf-8', 'strict')
        vms_info[vm_id] = _extract_container_info(project_name, vm_id)

    return vms_info


def _extract_container_info(project_name: str, vm_id: str):
    """Get a hash of info about a container : name, ports, image, ip ..."""

    try:
        result = subprocess.check_output(['docker', 'inspect', vm_id], stderr=subprocess.STDOUT)
        vm_data = json_loads(result.decode().rstrip('\n'))

        vm_info = {
            'name': vm_data[0]['Name'].lstrip('/'),
            'compose_name': vm_data[0]['Config']['Labels']['com.docker.compose.service'],
            'ports': vm_data[0]['Config']['ExposedPorts'].keys() if 'ExposedPorts' in vm_data[0]['Config'] else [],
            'image': vm_data[0]['Config']['Image'],
            'ip': _get_ip_from_networks(project_name, vm_data[0]['NetworkSettings']['Networks']),
            'running': vm_data[0]['State']['Running'],
        }

        return vm_info
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

    result = subprocess.check_output(['docker', 'inspect', container], stderr=subprocess.STDOUT)
    vm_data = json_loads(result.decode().rstrip('\n'))
    for connected_network in vm_data[0]['NetworkSettings']['Networks'].keys():
        if connected_network == expected_network:
            return True

    return False


def _network_exists(network: str):
    """Returns True if a network exists. Used by create_network"""

    result = subprocess.check_output(['docker', 'network', 'ls', '--filter', 'name=dns'], stderr=subprocess.STDOUT)
    networks_list = result.decode().splitlines()
    if len(networks_list) > 1:
        return True

    return False
