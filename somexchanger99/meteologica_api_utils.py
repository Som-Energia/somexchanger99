import logging
import os
import re
import stat
import pandas as pd
import pytz

from datetime import datetime as dt
from datetime import timedelta

from django.conf import settings

from zeep import Client
from zeep.transports import Transport
from requests import Session
from yamlns import namespace as ns

logger = logging.getLogger(__name__)

class MeteologicaApiError(Exception): pass

class MeteologicaApi_Mock(object):
    def __init__(self):
        self._data = {}
        self._session = {}
        self._login = {}
        self._response = {}
        self._validPlants = "MyPlant OtherPlant".split()

    def login(self, username, password):
        self._login = dict(
            username = username,
            password = password,
        )
        if self._login['username'] != 'alberto' or self._login['password'] != '1234':
            self._session = {
                    'errorCode': 'INVALID_USERNAME_OR_PASSWORD',
                    'header': {
                        'sessionToken': None,
                        'errorCode': 'NO_SESSION'
                        }
                    }
            return self._session
        else:
            self._session = {
                    'errorCode': 'OK',
                    'header': {
                    'sessionToken': '73f19a710bbced25fb2e46e5a0d65b126716a8d19bb9f9038d2172adc14665a5f0c65a30e9fb677e5654b2f59f51abdb',
                    'errorCode': 'OK'
                        }
                    }
            return self._session

    def uploadProduction(self, facility, data):
        self._checkFacility(facility)
        facility_data = self._data.setdefault(facility, [])
        facility_data += data

    def _checkFacility(self, facility):
        if facility not in self._validPlants:
            raise MeteologicaApiError("INVALID_FACILITY_ID")

    def lastDateUploaded(self, facility):
        facility_data = self._data.get(facility, [])
        if not facility_data: return None
        return max(date for date, measure in facility_data)

class MeteologicaApi:
    def __init__(self, **kwds):
        self._config = ns(kwds)
        self._lastDates = ns()

    def _checkFacility(self, facility): pass

    def uploadProduction(self, facility, data):
        self.client = Client(self._config.wsdl)
        self.session = self.client.service.login(dict(
            username = self._config.username,
            password = self._config.password,
        ))
        if os.environ.get("VERBOSE"): print(self.session)
        response = self.client.service.setObservation(dict(
            header = self.session.header,
            facilityId = facility,
            variableId = 'prod',
            measurementType ='CUMULATIVE',
            measurementTime = 60, # minutes
            unit = 'kW',
            observationData = dict(item=[
                dict(
                    startTime = startTime,
                    data = value,
                )
                for startTime, value in data
            ]),
        ))
        if os.environ.get("VERBOSE"): print(response)
        if response.errorCode != "OK":
            raise MeteologicaApiError(response.errorCode)

        self.session.header['sessionToken'] = response.header['sessionToken']
        self.client.service.logout(self.session)
        lastDateOfCurrentBatch = max(date for date, measure in data)
        self._lastDates[facility] = max(self._lastDates.get(facility,''), lastDateOfCurrentBatch)

    def lastDateUploaded(self, facility):
        return self._lastDates.get(facility,None)


class MeteologicaApiUtils(object):

    def __init__(self, wsdl, username, password):
        self.__wsdl = wsdl
        self.__username = username
        self.__password = password
        self._client = Client(wsdl)
        self.__data_login = {'username': self.__username, 'password': self.__password}
        self._api_session = self._client.service.login(self.__data_login)
        logger.info("Sesion information %s", self._api_session.header)

    def upload_to_api(self, file_name):
        '''
        Upload `data` to Meteologica API
        '''
        try:
            df = pd.read_csv(settings.METEOLOGICA_CONF['file'], delimiter=';')
            local = pytz.timezone ("Europe/Madrid")
            for row in df.itertuples():
                facilityId_val = row[1]
                startTime_val = row[2]
                data_val = row[5]
                naive = dt.strptime(startTime_val, "%Y-%m-%d %H:%M:%S")
                local_dt = local.localize(naive, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                startTime_val = utc_dt.strftime ("%Y-%m-%d %H:%M:%S")
                try: 
                    logger.info("Uploading production curves to Meteologica API")
                    observationData = {
                                        'item': [
                                            {
                                                'startTime': startTime_val,
                                                'data': data_val
                                            }
                                        ]
                                    }
                    data_observation = {
                                        'header':self._api_session.header,
                                        'facilityId': facilityId_val,
                                        'variableId': 'prod',
                                        'measurementType': 'CUMULATIVE',
                                        'measurementTime': 60,
                                        'unit': 'kW',
                                        'observationData': observationData
                                    }
                    logger.info("Sending data: %s", data_observation)
                    resp_data = self._client.service.setObservation(data_observation)
                    logger.info("Response from API: %s", resp_data)
                    if resp_data.header['sessionToken'] != self._api_session.header['sessionToken']:
                        self._api_session.header['sessionToken'] = resp_data.header['sessionToken']
                
                except Exception as e:
                        msg = "An uncontroled error happened during uploading "\
                            "process, reason: %s"
                        logger.exception(msg, str(e))
        except Exception as e:
            msg = "An uncontroled error happened during downloading "\
                    "process, reason: %s"
            logger.exception(msg, str(e))


    def close_conection(self):
        if self._client is not None:
            self._client.service.logout(self._api_session)

