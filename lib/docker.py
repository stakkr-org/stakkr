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
        vm_data = json_loads(result.decode("utf-8", "strict").rstrip('\n'))

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

    return network_settings['IPAddress']


def container_running(name: str):
    cmd = ['docker', 'inspect', '-f', '{{.State.Running}}', name]
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).splitlines()[0]
        return False if result.decode("utf-8", "strict") == 'false' else True
    except subprocess.CalledProcessError as e:
        return False
