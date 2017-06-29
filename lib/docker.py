from json import loads as json_loads
import subprocess


def get_vms(project_name: str):
    cmd = ['python', 'bin/compose', 'ps', '-q']
    vms_id = subprocess.check_output(cmd).splitlines()
    vms_info = dict()
    for vm_id in vms_id:
        vm_id = vm_id.decode('utf-8', 'strict')
        vms_info[vm_id] = extract_vm_info(project_name, vm_id)

    return vms_info


def extract_vm_info(project_name: str, vm_id: str):
    try:
        result = subprocess.check_output(['docker', 'inspect', vm_id], stderr=subprocess.STDOUT)
        vm_data = json_loads(result.decode().rstrip('\n'))

        vm_info = {
            'name': vm_data[0]['Name'].lstrip('/'),
            'compose_name': vm_data[0]['Config']['Labels']['com.docker.compose.service'],
            'ports': vm_data[0]['Config']['ExposedPorts'].keys() if 'ExposedPorts' in vm_data[0]['Config'] else [],
            'image': vm_data[0]['Config']['Image'],
            'ip': get_ip_from_networks(project_name, vm_data[0]['NetworkSettings']['Networks']),
            'running': vm_data[0]['State']['Running'],
        }

        return vm_info
    except subprocess.CalledProcessError as e:
        return None


def get_ip_from_networks(project_name: str, networks: list):
    network_settings = {}
    if '{}_lamp'.format(project_name) in networks:
        network_settings = networks['{}_lamp'.format(project_name)]

    return network_settings['IPAddress'] if 'IPAddress' in network_settings else ''


def container_running(name: str):
    cmd = ['docker', 'inspect', '-f', '{{.State.Running}}', name]
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).splitlines()[0]
        return False if result.decode() == 'false' else True
    except subprocess.CalledProcessError as e:
        return False


def add_container_to_network(container: str, network: str):
    if container_in_network(container, network) is True:
        return False

    cmd = ['docker', 'network', 'connect', network, container]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return True


def create_network(network: str):
    if network_exists(network) is True:
        return False

    cmd = ['docker', 'network', 'create', '--driver', 'bridge', network]
    subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return True


def container_in_network(container: str, expected_network: str):
    result = subprocess.check_output(['docker', 'inspect', container], stderr=subprocess.STDOUT)
    vm_data = json_loads(result.decode().rstrip('\n'))
    for connected_network in vm_data[0]['NetworkSettings']['Networks'].keys():
        if connected_network == expected_network:
            return True

    return False


def network_exists(network: str):
    result = subprocess.check_output(['docker', 'network', 'ls', '--filter', 'name=dns'], stderr=subprocess.STDOUT)
    networks_list = result.decode().splitlines()
    if len(networks_list) > 1:
        return True

    return False
