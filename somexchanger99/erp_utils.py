from operator import itemgetter

from celery.utils.log import get_task_logger
from dateutil import parser
from django.conf import settings
from django.utils.timezone import make_aware
from erppeek import Client

from somexchanger99.models import Curve2Exchange

logger = get_task_logger(__name__)

client = Client(**settings.ERP_CONF)


class ErpUtils(object):

    def __init__(self):
        self._client = Client(**settings.ERP_CONF)

    def get_attachments(self, model, date, process, **kwargs):
        '''
        Obtain file attachments of the process `process` in the step `step`
        associated with the `model` on date `date`.

        `process`: can be any ATR process (F1, A3, M1, ...)
        `step`: step of the `process` if is a switching process (A3, C1, M1, ...)
        `model`: ERP model
        `date`: Creation date
        '''
        date_to = kwargs.get('date_to')
        step = kwargs.get('step')
        objects = self._get_objects_with_attachment(
            model, date, process=process, step=step, date_to=date_to
        )

        attach_query = [
            ('res_id', 'in', objects.id),
            ('res_model', '=', model)
        ]

        attachments = self._client.read(
            'ir.attachment',
            attach_query,
            order='create_date DESC'
        )

        return attachments if not step else self.__filter_attachment(attachments, step=step, date=date)

    def get_sftp_providers(self):
        Provider = self._client.model('tg.comer.provider')
        TgSFTP = self._client.model('tg.sftp')

        provider_ids = Provider.search([])
        providers = Provider.read(provider_ids)

        return [
            TgSFTP.read(provider['sftp'][0])
            for provider in providers if provider['enabled']
        ]

    def _get_objects_with_attachment(self, model, date, **kwargs):
        Model = self._client.model(model)
        object_query = self.__get_object_query(model, date, **kwargs)
        objects = Model.browse(object_query)

        return objects

    def __get_object_query(self, model, date_from, **kwargs):

        date_to = kwargs.get('date_to')

        BASE_QUERY = {
            'giscedata.facturacio.importacio.linia': [
                ('state', '=', 'valid'),
                ('write_date', '>=', str(date_from.date())),
            ] + ([('write_date', '<', str(date_to.date()))] if date_to else []),
            'giscedata.switching': [
                ('proces_id.name', '=', kwargs.get('process')),
                ('date', '>=', str(date_from.date())),
            ] + ([('date', '<', str(date_to.date()))] if date_to else [])
        }
        query = BASE_QUERY[model]
        logger.info(query)
        return query

    def __filter_attachment(self, attachements, step, date):
        description = lambda attach: attach.get('description', '') or ''
        create_date = itemgetter('create_date')

        step_info = 'Pas: {}'.format(step)
        is_created_from_date = lambda attach, from_date: \
            make_aware(parser.parse(create_date(attach)), from_date.tzinfo) >= from_date

        return [
            attach for attach in attachements
            if step_info in description(attach) and is_created_from_date(attach, date)
        ]


class ERPCurveProvider(object):

    FIELDS = [
        'name',
        'host',
        'port'
        'user',
        'password',
        'private_key_binary',
        'private_key',
        'private_key_pass',
        'root_dir'
    ]

    def __init__(self, provider_id):
        self._erp_conn = client

        for name, value in self._erp_conn.TgSFTP.read(provider_id, self.FIELDS).items():
            setattr(self, name, value)

        self._source = Sftp(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            base_dir=self.root_dir
        )

    def get_curves(self, *curve_name, date=None):
        curves = Curve2Exchange.objects.filter(name__in=curve_name)
        result = {}

        with self._source:
            for curve in curves:
                result[curve.name] = self._source.get_files_to_download(
                    path=self.root_dir,
                    pattern=curve.pattern,
                    date=curve.last_upload or date
                )
        return result
