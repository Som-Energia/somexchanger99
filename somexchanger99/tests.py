from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from . import erp_utils, sftp_utils
from .models import Curve2Exchange
from .utils import get_curves, push_curves


class TestUtils(TestCase):

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

    def test__get_sftp_providers_p1d(self):
        providers_list = self.erp.get_sftp_providers('p1')

        is_p1d_pattern = all(
            ['p1_syntax' in provider for provider in providers_list]
        )
        self.assertGreater(len(providers_list), 0)
        self.assertTrue(is_p1d_pattern)

    @patch.object(sftp_utils.SftpUtils, 'get_files_to_download')
    def test__get_curves_f5d(self, mock):
        mock.return_value = [
            ('/folder1/file1.zip', 'file1.zip'),
            ('/folder2/file2.zip', 'file2.zip')
        ]
        curve2exchange = Curve2Exchange(name='f5d', erp_name='f5d', active=True)
        curve2exchange.save()

        curves = get_curves(curve2exchange.erp_name)

        curve2exchange.refresh_from_db()
        self.assertEqual(curve2exchange.last_upload.date(), timezone.now().date())
        self.assertDictEqual(
            curves,
            {
                'Aseme': [
                    ('/folder1/file1.zip', 'file1.zip'),
                    ('/folder2/file2.zip', 'file2.zip')
                ],
                'E.on': [
                    ('/folder1/file1.zip', 'file1.zip'),
                    ('/folder2/file2.zip', 'file2.zip')
                ],
                'Eléctrica de Eriste': [
                    ('/folder1/file1.zip', 'file1.zip'),
                    ('/folder2/file2.zip', 'file2.zip')
                ],
                'Eléctrica del Ebro SA': [
                    ('/folder1/file1.zip', 'file1.zip'),
                    ('/folder2/file2.zip', 'file2.zip')
                ],
                'Endesa': [
                    ('/folder1/file1.zip', 'file1.zip'),
                    ('/folder2/file2.zip', 'file2.zip')
                ],
                'Iberdrola': [
                    ('/folder1/file1.zip', 'file1.zip'),
                    ('/folder2/file2.zip', 'file2.zip')
                ],
                'Unión Fenosa': [
                    ('/folder1/file1.zip', 'file1.zip'),
                    ('/folder2/file2.zip', 'file2.zip')
                ]
            }
        )

    @patch.object(sftp_utils.SftpUtils, 'get_files_to_download')
    def test__get_curves_p1d(self, mock):
        mock.return_value = [
            ('/folder1/p1dfile1.zip', 'p1dfile1.zip'),
            ('/folder2/p1dfile2.zip', 'p1dfile2.zip')
        ]

        curve2exchange = Curve2Exchange(name='p1d', erp_name='p1', active=True)
        curve2exchange.save()

        curves = get_curves('p1')

        curve2exchange.refresh_from_db()
        self.assertEqual(
            curve2exchange.last_upload.date(),
            timezone.now().date()
        )
        self.assertDictEqual(
            curves,
            {
                'Endesa': [
                    ('/folder1/p1dfile1.zip', 'p1dfile1.zip'),
                    ('/folder2/p1dfile2.zip', 'p1dfile2.zip')
                ],
                'Iberdrola': [
                    ('/folder1/p1dfile1.zip', 'p1dfile1.zip'),
                    ('/folder2/p1dfile2.zip', 'p1dfile2.zip')
                ],
            }
        )

    @patch.object(sftp_utils.SftpUtils, 'download_file_content')
    @patch.object(sftp_utils.SftpUtils, 'upload_file')
    def test__push_curves_p1d(self, sftp_mock, neuro_mock):
        curve2exchange = Curve2Exchange(name='p1d', erp_name='p1', active=True)
        sftp_mock.return_value = 'hola soy una curva cuarthoria'
        neuro_mock.return_value = None
        curves_files = {
            'Endesa': [
                ('/folder1/p1dfile1.zip', 'p1dfile1.zip'),
                ('/folder2/p1dfile2.zip', 'p1dfile2.zip')
            ],
            'Iberdrola': [
                ('/folder1/p1dfile1.zip', 'p1dfile1.zip'),
                ('/folder2/p1dfile2.zip', 'p1dfile2.zip')
            ],
        }

        exchange_result = push_curves(curve2exchange, curves_files)

        self.assertDictEqual(
            exchange_result, {'Endesa': 2, 'Iberdrola': 2}
        )
