"""Test stakkr-compose command"""

import os
import sys
import subprocess
import unittest
import stakkr.stakkr_compose as sc

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class StakkrComposeTest(unittest.TestCase):
    services = {
        'a': 'service_a.yml',
        'b': 'service_b.yml',
    }

    def test_get_invalid_config_in_cli(self):
        cmd = ['stakkr-compose', '-c', base_dir + '/static/config_invalid.yml']
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in result.stdout:
            self.assertRegex(line.decode(), 'Failed validating.*config_invalid.yml.*')
            break

    def test_get_uid(self):
        uid = '1000' if os.name == 'nt' else str(os.getuid())
        self.assertEqual(sc._get_uid(None), uid)

    def test_get_gid(self):
        gid = '1000' if os.name == 'nt' else str(os.getgid())
        self.assertEqual(sc._get_gid(None), gid)

    def test_get_uid_whenset(self):
        self.assertEqual(sc._get_uid(1000), '1000')

    def test_get_gid_whenset(self):
        self.assertEqual(sc._get_gid(1000), '1000')

    # def test_get_wrong_enabled_service(self):
    #     with self.assertRaises(SystemExit):
    #         sc._get_enabled_services_files(['c'])

    # def test_get_right_enabled_service(self):
    #     services_files = sc._get_enabled_services_files(['maildev'])
    #     self.assertTrue(services_files[0].endswith('static/services/maildev.yml'))

    def test_get_available_services(self):
        from shutil import rmtree

        stakkr_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/stakkr'
        static_path = os.path.dirname(os.path.realpath(__file__)) + '/static'
        rmtree(static_path + '/services/db', ignore_errors=True)
        rmtree(static_path + '/services/databases', ignore_errors=True)
        rmtree(static_path + '/services/php', ignore_errors=True)

        add_emails = ['stakkr', '-c', base_dir + '/static/stakkr.yml', 'services-add', 'emails']
        subprocess.Popen(add_emails, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        services = sc.get_available_services(static_path)
        self.assertFalse('apache' in services)
        self.assertFalse('mongo' in services)
        self.assertFalse('elasticsearch' in services)
        self.assertTrue('php' in services)
        self.assertTrue('portainer' in services)
        self.assertTrue('maildev' in services)

        self.assertEqual(stakkr_path + '/static/services/portainer.yml', services['portainer'])
        self.assertEqual(static_path + '/services/test/docker-compose/php.yml', services['php'])

    # def test_get_valid_configured_services(self):
    #     services = sc.get_configured_services(base_dir + '/static/stakkr.yml')
    #     self.assertTrue('maildev' in services)
    #     self.assertTrue('php' in services)
    #     self.assertFalse('mongo' in services)
    #     self.assertFalse('elasticsearch' in services)


if __name__ == "__main__":
    unittest.main()
