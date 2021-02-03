import base64
from unittest.mock import patch

import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from pytz import timezone

from somexchanger99 import erp_utils, sftp_utils
from somexchanger99.utils import get_attachments
from somexchanger99.models import Curve2Exchange, File2Exchange

def test_pytest_ok():
    assert 'foo' != 'bar'

def test_testenviron_ok(settings):
    # Given a settings object
    # settings

    # then we are in test environment
    assert settings.TEST == 'OK'

# TODO defragilize the tests with a mock or a fake
# TODO mock or fake so that we're certain only one attachment is there

def test__ErpUtils_get_objects_with_attachment():
    erp = erp_utils.ErpUtils()

    model = 'giscedata.switching'
    date = datetime(2020, 10, 1, 7, 46, 22, tzinfo=timezone('CET'))
    process = 'E1'
    step = '01'

    e1s_objects = erp._get_objects_with_attachment(
        model, date, process=process, step=step, date_to=None
    )

    assert e1s_objects.id != []


def test__ErpUtils_get_e101_attachments__oneCase():

    erp = erp_utils.ErpUtils()

    model = 'giscedata.switching'
    date = datetime(2020, 10, 1, 7, 46, 22, tzinfo=timezone('CET'))
    process = 'E1'
    step = '01'

    attachments = erp.generate_e101_attachments(model=model, date=date, process=process, step=step)

    # TODO defragilize
    # assert len(attachments) == 1
    assert attachments != []

    e101_xml_content = base64.decodebytes(attachments[0]['datas'].encode()).decode()

    assert 'MensajeSolicitudDesistimiento' in e101_xml_content


def test__ErpUtils_get_e101_attachments__manyCases():

    erp = erp_utils.ErpUtils()

    model = 'giscedata.switching'
    date = datetime(2020, 10, 1, 7, 46, 22, tzinfo=timezone('CET'))
    process = 'E1'
    step = '01'

    attachments = erp.generate_e101_attachments(model=model, date=date, process=process, step=step)

    assert attachments != []
    assert len(attachments) > 1

    for attachment in attachments:
        e101_xml_content = base64.decodebytes(attachment['datas'].encode()).decode()

        assert 'MensajeSolicitudDesistimiento' in e101_xml_content

# TODO erppeek seems to not filter correctly the dates, we tested calling browse directly filtering by date
def _test__ErpUtils_get_e101_attachments__manyCases_filterByDateRange():

    erp = erp_utils.ErpUtils()

    model = 'giscedata.switching'
    date = datetime(2020, 10, 1, 1, 46, 22, tzinfo=timezone('CET'))
    process = 'E1'
    step = '01'
    date_to = datetime(2020, 10, 2, 12, 00, 22, tzinfo=timezone('CET'))

    attachments = erp.generate_e101_attachments(model=model, date=date, process=process, step=step)

    assert attachments != []
    assert len(attachments) == 1

    for attachment in attachments:
        e101_xml_content = base64.decodebytes(attachment['datas'].encode()).decode()

        assert 'MensajeSolicitudDesistimiento' in e101_xml_content

# TODO data has already an empty step example, keep it when mocking/faking
def _test__ErpUtils_get_e101_attachments__oneCase__EmptyStep():

    erp = erp_utils.ErpUtils()

    model = 'giscedata.switching'
    date = datetime(2020, 10, 1, 7, 46, 22, tzinfo=timezone('CET'))
    process = 'E1'
    step = '01'

    attachments = erp.generate_e101_attachments(model=model, date=date, process=process, step=step)

    assert attachments != []

def test__ErpUtils_get_attachments__E101():

    model = 'giscedata.switching'
    date = datetime(2020, 10, 1, 7, 46, 22, tzinfo=timezone('CET'))
    process = 'E1'
    step = '01'

    attachment_result = get_attachments(model=model, date=date, process=process, step=step)
 
    assert 'attachments' in attachment_result

    attachments = attachment_result['attachments']

    assert attachments != []

    for attachment in attachments:
        # TODO how do we distinguish e1 from others?
        e101_xml_content = base64.decodebytes(attachment['datas'].encode()).decode()

        assert 'MensajeSolicitudDesistimiento' in e101_xml_content

def test__ErpUtils_get_attachments__notE101():

    model = 'giscedata.switching'
    date = datetime(2020, 10, 1, 7, 46, 22, tzinfo=timezone('CET'))
    process = 'E1'
    step = '02'
    date_to = datetime(2020, 10, 4, 7, 46, 22, tzinfo=timezone('CET'))

    attachment_result = get_attachments(model=model, date=date, process=process, step=step, date_to=date_to)
    assert 'attachments' in attachment_result

    attachments = attachment_result['attachments']

    assert attachments != []
    for attachment in attachments:
        xml_content = base64.decodebytes(attachment['datas'].encode()).decode()
        
        assert 'MensajeSolicitudDesistimiento' not in xml_content

def _test__ErpUtils_action_exportar_xml():

    erp = erp_utils.ErpUtils()
    sw_obj = erp._client.model('giscedata.switching')
    e1_ids = sw_obj.search([('proces_id', '=', 11)])
    step_obj = erp._client.model('giscedata.switching.step')

    e1_id = e1_ids[2]
    steps = step_obj.search([('proces_id','=', 11)])

    swe101 = erp._client.model('giscedata.switching.e1.01')
    pas_id = swe101.search([('sw_id', '=', e1_id)])[0]

    
    e101_step = sorted(steps)[0]
    switching_wizard = erp._client.model('giscedata.switching.wizard')
    
    step_id = str( (e101_step, pas_id) )
    print(step_id)


    id_wiz = switching_wizard.create(
        {'name': False, 'state': 'init', 'multicas': 0, 'file': False, 'step_id': step_id, 'mark_as_processed': 0, 'send_always': 1},
        {'lang': 'ca_ES', 'active_ids': [e1_id], 'tz': 'Europe/Madrid', 'active_id': e1_id}
    )

    switching_wizard.action_exportar_xml([id_wiz.id], {'active_ids': [e1_id], 'active_id': e1_id})
    e101_xml = switching_wizard.read([id_wiz.id],['file'], {'lang': 'ca_ES', 'bin_size': False, 'tz': 'Europe/Madrid', 'active_ids': [e1_id], 'active_id': e1_id})

    e101_xml_content = base64.decodebytes(e101_xml.encode()).decode()

    assert erp != None


@pytest.mark.skip(reason="To refactor")
class TestUtils(TestCase):

    erp = None # erp_utils.ErpUtils()

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
