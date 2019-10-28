from django.test import TestCase

from .erp_utils import ErpUtils


class TestErpUtils(TestCase):

    def setUp(self):
        self.erp = ErpUtils()
        self.maxDiff = None

    def test__get_sftp_providers_f5d(self):
        providers_list = self.erp.get_sftp_providers('f5d')

        is_f5d_pattern = all(
            ['f5d_syntax' in provider for provider in providers_list]
        )
        self.assertGreater(len(providers_list), 0)
        self.assertTrue(is_f5d_pattern)

    def test__get_sftp_providers_p5d(self):
        providers_list = self.erp.get_sftp_providers('p5d')

        is_p5d_pattern = all(
            ['p5d_syntax' in provider for provider in providers_list]
        )
        self.assertGreater(len(providers_list), 0)
        self.assertTrue(is_p5d_pattern)
