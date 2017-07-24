import os
import sys
import stakkr.stakkr_compose as sc
import subprocess
import unittest

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class StakkrComposeTest(unittest.TestCase):
    services = {
        'a': 'service_a.yml',
        'b': 'service_b.yml',
    }


    def test_get_invalid_config_in_cli(self):
        cmd = ['stakkr-compose', '-c', base_dir + '/static/config_invalid.ini']
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in result.stdout:
            self.assertRegex(line.decode(), 'Failed validating.*config_invalid.ini.*')
            break


    def test_get_uid(self):
        uid = str(os.getuid())
        self.assertEqual(sc._get_uid(None), uid)


    def test_get_gid(self):
        gid = str(os.getgid())
        self.assertEqual(sc._get_gid(None), gid)


    def test_get_uid_whenset(self):
        self.assertEqual(sc._get_uid(1000), '1000')


    def test_get_gid_whenset(self):
        self.assertEqual(sc._get_gid(1000), '1000')


    def test_get_wrong_enabled_service(self):
        with self.assertRaises(SystemExit):
            sc.get_enabled_services(['c'], self.services)


    def test_get_right_enabled_service(self):
        services_files = sc.get_enabled_services(['a'], self.services)
        self.assertEqual(services_files, ['-f', 'service_a.yml'])


    def test_get_available_services(self):
        services = sc.get_available_services()
        self.assertTrue('apache' in services)
        self.assertTrue('mongo' in services)
        self.assertTrue('php' in services)
        self.assertTrue('elasticsearch' in services)

        self.assertEqual('static/services/apache.yml', services['apache'][-26:])
        self.assertEqual('static/services/mongo.yml', services['mongo'][-25:])
