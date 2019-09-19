from .meteologica_api_utils import MeteologicaApi
from unittest.mock import patch
import unittest

class MeteologicaApi_Test(unittest.TestCase):

    def setUp(self):
        self.config = dict()

    def createApi(self):
        return MeteologicaApi(**self.config)

    def test_uploadProduction_singleData(self):
        facility = "MyPlant"
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2200-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(facility),
            "2200-01-01 00:00:00"
        )

    def test_uploadProduction_noData(self):
        facility = "MyPlant"
        api = self.createApi()
        self.assertEqual(
            api.lastDateUploaded(facility),
            None
        )

    def test_uploadProduction_manyData(self):
        facility = "MyPlant"
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2200-01-01 00:00:00", 10),
            ("2200-01-02 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(facility),
            "2200-01-02 00:00:00"
        )

    def test_uploadProduction_calledTwice(self):
        facility = "MyPlant"
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2200-01-02 00:00:00", 10),
        ])
        api.uploadProduction(facility, [
            ("2200-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(facility),
            "2200-01-02 00:00:00"
        )

    def test_uploadProduction_otherFacility(self):
        facility = "MyPlant"
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2200-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded("OtherPlant"),
            None
        )








unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et