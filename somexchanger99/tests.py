import unittest
from unittest.mock import patch
from django.test import TestCase

from . import erp_utils
from .tasks import get_curves


class TestErpUtils(TestCase):

    erp = erp_utils.ErpUtils()

    def setUp(self):
        self.maxDiff = None

    @patch.object(erp, 'get_sftp_providers')
    def test__get_sftp_providers_f5d(self, mock):
        mock.return_value = [{
            'f5d_syntax': 'F5D_0022_0762_(\\d{8})',
            'host': 'penosa.com',
            'id': 15,
            'name': 'Unión Penosa',
            'password': False,
            'port': 22,
            'private_key': False,
            'private_key_binary': False,
            'private_key_pass': False,
            'read_dir': '/',
            'root_dir': '/',
            'user': 'user'
        }]
        providers_list = self.erp.get_sftp_providers('f5d')

        is_f5d_pattern = all(
            ['f5d_syntax' in provider for provider in providers_list]
        )
        mock.assert_called_once_with('f5d')
        self.assertEqual(len(providers_list), 1)
        self.assertTrue(is_f5d_pattern)

    def test__get_sftp_providers_p5d(self):
        providers_list = self.erp.get_sftp_providers('p5d')

        is_p5d_pattern = all(
            ['p5d_syntax' in provider for provider in providers_list]
        )
        self.assertGreater(len(providers_list), 0)
        self.assertTrue(is_p5d_pattern)

    def test__get_curves_f5d(self):
        curves = get_curves('f5d')

        self.assertDictEqual(curves, dict())
