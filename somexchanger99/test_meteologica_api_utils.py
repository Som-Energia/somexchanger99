from .meteologica_api_utils import (
    MeteologicaApi_Mock,
    MeteologicaApi,
    MeteologicaApiError,
)
from unittest.mock import patch
import unittest

class MeteologicaApiMock_Test(unittest.TestCase):

    def createApi(self):
        return MeteologicaApi_Mock()

    def mainFacility(self):
        return "MyPlant"

    def otherFacility(slf):
        return "OtherPlant"

    def test_uploadProduction_singleData(self):
        facility = self.mainFacility()
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2040-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(facility),
            "2040-01-01 00:00:00"
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
            ("2040-01-01 00:00:00", 10),
            ("2040-01-02 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(facility),
            "2040-01-02 00:00:00"
        )

    def test_uploadProduction_calledTwice(self):
        facility = self.mainFacility()
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2040-01-02 00:00:00", 10),
        ])
        api.uploadProduction(facility, [
            ("2040-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(facility),
            "2040-01-02 00:00:00"
        )

    def test_uploadProduction_doesNotChangeOtherFacility(self):
        facility = self.mainFacility()
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2040-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded("OtherPlant"),
            None
        )

    def test_uploadProduction_otherFacility(self):
        facility = self.mainFacility()
        otherFacility = self.otherFacility()
        api = self.createApi()
        api.uploadProduction(facility, [
            ("2040-01-02 00:00:00", 10),
        ])
        api.uploadProduction(otherFacility, [
            ("2040-01-01 00:00:00", 10),
        ])
        self.assertEqual(
            api.lastDateUploaded(otherFacility),
            "2040-01-01 00:00:00"
        )

    def test_uploadProduction_wrongFacility(self):
        api = self.createApi()
        with self.assertRaises(MeteologicaApiError) as ctx:
            api.uploadProduction("WrongPlant", [
                ("2040-01-01 00:00:00", 10),
            ])
        self.assertEqual(type(u'')(ctx.exception), "INVALID_FACILITY_ID")

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
    def _test_uploadProduction_errorUpload(self):
        api = self.createApi()
        login = api.login('alberto','1234')
        facility = self.mainFacility()
        api.uploadProduction(facility, [
            ("2040-01-01 00:00:00", 10),
        ])
  


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

    def otherFacility(slf):
        return "SomEnergia_Alcolea"


unittest.TestCase.__str__ = unittest.TestCase.id


# vim: ts=4 sw=4 et