from .meteologica_api_utils import (
    MeteologicaApi_Mock,
    MeteologicaApi,
)
from unittest.mock import patch
import unittest

class MeteologicaApiMock_Test(unittest.TestCase):

    def createApi(self):
        return MeteologicaApi_Mock()

    def mainFacility(self):
        return "MyPlant"

    def test_uploadProduction_singleData(self):
        facility = self.mainFacility()
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2020-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(facility),
            "2020-01-01 00:00:00"
        )

    def test_uploadProduction_noData(self):
        facility = self.mainFacility()
        api = self.createApi()
        self.assertEqual(
            api.lastDateUploaded(facility),
            None
        )

    def test_uploadProduction_manyData(self):
        facility = self.mainFacility()
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
        facility = self.mainFacility()
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

    def test_uploadProduction_doesNotChangeOtherFacility(self):
        facility = self.mainFacility()
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2200-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded("OtherPlant"),
            None
        )

    def test_uploadProduction_otherFacility(self):
        facility = self.mainFacility()
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2200-01-02 00:00:00", 10),
        ])
        api.uploadProduction("OtherPlant", [
            ("2200-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded("OtherPlant"),
            "2200-01-01 00:00:00"
        )

    def test_login_wrongSessionLogin(self):
        api = self.createApi()
        login = api.login('alberto','124')
        self.assertEqual(
            login['errorCode'],
            'INVALID_USERNAME_OR_PASSWORD'
        )

    def test_login_rightSessionLogin(self):
        api = self.createApi()
        login = api.login('alberto','1234')
        self.assertEqual(
            login['errorCode'],
            'OK'
        )


from django.conf import settings

class MeteologicaApi_Test(MeteologicaApiMock_Test):

    def createApi(self):
        return MeteologicaApi(
            wsdl=settings.METEOLOGICA_CONF['wsdl'],
            username=settings.METEOLOGICA_CONF['username'],
            password=settings.METEOLOGICA_CONF['password'],
        )

    def mainFacility(self):
        return "SomEnergia_Fontivsolar"


unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et