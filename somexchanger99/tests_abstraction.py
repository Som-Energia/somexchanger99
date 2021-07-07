from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

# from . import erp_utils, sftp_utils
from .controllers import exchange_meteologica_predictions
from .models import Curve2Exchange, File2Exchange
from .utils import get_curves, push_curves


class TestAbstraction(TestCase):

    # erp = erp_utils.ErpUtils()

    def setUp(self):
        self.maxDiff = None

    def test__get_CSV(self):
        pass

    def test__get_MHCIL(self):
        pass

    def test__to_meteologica(self):
        pass

    def test__from_MHCIL_to_meteologica(self):
        pass

    #move from one postgres to another
    def test__fromPostgresTable_ToPostgresTable(self):
        pass
