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


logger = logging.getLogger(__name__)


class MeteologicaApiUtils(object):

    def __init__(self, wsdl, username, password):
        self.__wsdl = wsdl
        self.__username = username
        self.__password = password
        self._client = Client(wsdl)
        self.__data_login = {'username' : self.__username, 'password' : self.__password}
        self._api_session = self._client.service.login(self.__data_login)

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
                naive = dt.datetime.strptime(startTime_val, "%Y-%m-%d %H:%M:%S")
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
                                        'unit': 'kw', 
                                        'observationData': observationData
                                    }
                    self._client.service.setObservation(data_observation)
                
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

