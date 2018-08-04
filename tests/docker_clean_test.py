import os
import sys
import unittest

from click.testing import CliRunner
from docker.errors import NotFound
from stakkr.docker_clean import clean
from stakkr.docker_actions import get_client as get_docker_client
from subprocess import Popen, DEVNULL, PIPE

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


class DockerCleanTest(unittest.TestCase):
    def test_no_arg(self):
        result = CliRunner().invoke(clean)
        self.assertEqual(0, result.exit_code)
        regex = r'.*Cleaning Docker stopped containers.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused images.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused volumes.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused networks.*'
        self.assertRegex(result.output, regex)

    def test_bad_arg(self):
        result = CliRunner().invoke(clean, ['hello-world'])
        self.assertEqual(2, result.exit_code)
        self.assertRegex(result.output, r'Usage: docker-clean \[OPTIONS\].*')

    def test_full_clean(self):
        # Remove data that could create conflicts
        # Stop all containers
        clean_cts()
        # Remove all networks
        get_docker_client().networks.prune()
        # Remove all volumes
        get_docker_client().volumes.prune()
        # Remove all images
        clean_images()

        # Standard info
        num_default_nets = len(get_docker_client().networks.list())
        num_default_cts = len(get_docker_client().containers.list())
        num_default_images = len(get_docker_client().images.list())
        num_default_vols = len(get_docker_client().volumes.list())

        # Start specific networks
        get_docker_client().networks.create('test_delete')
        net_pytest = get_docker_client().networks.create('network_pytest')
        nets = get_docker_client().networks.list()
        # 5 because by default I have already 3
        self.assertIs(len(nets), (2 + num_default_nets))

        # We should have volumes also stored
        get_docker_client().volumes.create('hello')
        self.assertIs(len(get_docker_client().volumes.list()), (1 + num_default_vols))

        # Create 2 ct that'll be off but present
        # don't remove the first
        get_docker_client().containers.run('alpine:latest', name='hello_world_test')
        ct_test = get_docker_client().containers.run('edyan/adminer:latest',
                                                     remove=False, detach=True, name='ct_test')

        net_pytest.connect(ct_test)

        # Make sure we have two new image : hello-world + adminer
        num_images = len(get_docker_client().images.list())
        self.assertIs(num_images, (2 + num_default_images))

        # Make sure we have two new containers
        cts = get_docker_client().containers.list(all=True)
        self.assertIs(len(cts), (2 + num_default_cts))

        # CLEAN
        result = CliRunner().invoke(clean, ['--force', '--verbose'])
        self.assertEqual(0, result.exit_code)
        regex = r'.*Cleaning Docker stopped containers.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Removed 1 exited container\(s\), saved 0 bytes.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused images.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Removed [0-9]+ images\(s\).*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused volumes.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Removed 1 volume\(s\), saved 0 bytes.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused networks.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Removed 1 network\(s\).*'
        self.assertRegex(result.output, regex)

        # Make sure it has been cleaned
        # Except ct_test that is running so : 1 image, 1 network, 1 container
        self.assertIs(len(get_docker_client().networks.list()), num_default_nets + 1)
        self.assertIs(len(get_docker_client().volumes.list()), num_default_vols)
        debug = 'Total Images: {} / Images by default: {}'.format(len(get_docker_client().images.list()), num_default_images)
        self.assertIs(len(get_docker_client().images.list()), num_default_images + 1)
        self.assertIs(len(get_docker_client().networks.list()), num_default_nets + 1)

        ct_test.stop()

        # Stop adminer and clean again
        result = CliRunner().invoke(clean, ['--force', '--verbose'])
        self.assertEqual(0, result.exit_code)
        regex = r'.*Cleaning Docker stopped containers.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Removed 1 exited container\(s\), saved 0 bytes.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused images.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Removed [0-9]+ images\(s\).*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused volumes.*'
        self.assertRegex(result.output, regex)
        regex = r'.*No volume to remove*'
        self.assertRegex(result.output, regex)
        regex = r'.*Cleaning Docker unused networks.*'
        self.assertRegex(result.output, regex)
        regex = r'.*Removed 1 network\(s\).*'
        self.assertRegex(result.output, regex)

        # Make sure it has been cleaned
        # Except ct_test so : 1 image, 1 network, 1 container
        self.assertIs(len(get_docker_client().networks.list()), num_default_nets)
        self.assertIs(len(get_docker_client().volumes.list()), num_default_vols)
        self.assertIs(len(get_docker_client().images.list()), num_default_images)
        self.assertIs(len(get_docker_client().networks.list()), num_default_nets)


def clean_cts():
    cts = get_docker_client().containers.list(all=True)
    for ct in cts:
        try:
            ct.stop()
            ct.remove(v=True, force=True)
        except NotFound:
            pass


def clean_images():
    images = get_docker_client().images.list()
    for image in images:
        try:
            get_docker_client().images.remove(image.id)
        except NotFound:
            pass


if __name__ == "__main__":
    unittest.main()
