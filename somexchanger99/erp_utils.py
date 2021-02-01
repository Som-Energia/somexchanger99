from operator import itemgetter

from celery.utils.log import get_task_logger
from dateutil import parser
from django.conf import settings
from django.utils.timezone import make_aware
from erppeek import Client

logger = get_task_logger(__name__)


class ErpUtils(object):

    def __init__(self):
        self._client = Client(**settings.ERP_CONF)

    def get_e101_attachments(self, model, date, process, **kwargs):

        step = kwargs.get('step')

        sw_obj = self._client.model('giscedata.switching')
        sw_step_obj = self._client.model('giscedata.switching.step')
        swe101 = self._client.model('giscedata.switching.e1.01')
        switching_wizard = self._client.model('giscedata.switching.wizard')

        e1_ids = sw_obj.search([('proces_id', '=', 11)])

        e1_id = e1_ids[2]

        steps = sw_step_obj.search([('proces_id','=', 11)])

        pas_id = swe101.search([('sw_id', '=', e1_id)])[0]

        e101_step = sorted(steps)[0]
        
        step_id = str( (e101_step, pas_id) )

        id_wiz = switching_wizard.create(
            {'name': False, 'state': 'init', 'multicas': 0, 'file': False, 'step_id': step_id, 'mark_as_processed': 0, 'send_always': 1},
            {'lang': 'ca_ES', 'active_ids': [e1_id], 'tz': 'Europe/Madrid', 'active_id': e1_id}
        )

        switching_wizard.action_exportar_xml([id_wiz.id], {'active_ids': [e1_id], 'active_id': e1_id})
        e101_xml = switching_wizard.read([id_wiz.id],['file'], {'lang': 'ca_ES', 'bin_size': False, 'tz': 'Europe/Madrid', 'active_ids': [e1_id], 'active_id': e1_id})

        #e101_xml_content = base64.decodebytes(e101_xml.encode()).decode()

        # attachments_result = {
        #     'process': process,
        #     'attachments': attachments
        # }
        # if step:
        #     attachments_result['step'] = step

        return e101_xml

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
