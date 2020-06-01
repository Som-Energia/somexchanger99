from datetime import datetime
from operator import itemgetter

from celery.utils.log import get_task_logger
from django.conf import settings
from erppeek import Client

logger = get_task_logger(__name__)


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

    def get_sftp_providers(self, curve_type):
        Provider = self._client.model('tg.comer.provider')
        TgSFTP = self._client.model('tg.sftp')
        provider_ids = Provider.search([])

        providers = Provider.read(provider_ids)

        pattern = '{}_syntax'.format(curve_type)

        return [
            dict(
                list(TgSFTP.read(provider['sftp'][0]).items()) + [(pattern, provider[pattern])]
            )
            for provider in providers if provider['enabled'] and provider['{}_enabled'.format(curve_type)]
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
        date = date.date()

        step_info = 'Pas: {}'.format(step)
        is_created_at_date = lambda attach, filter_date: datetime.strptime(
            create_date(attach), '%Y-%m-%d %H:%M:%S'
        ).date() == filter_date

        return [
            attach for attach in attachements
            if step_info in description(attach) and is_created_at_date(attach, date)
        ]
