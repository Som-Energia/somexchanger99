from datetime import datetime
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

    def generate_e101_attachments(self, model, date, process, step, **kwargs):

        date_to = kwargs.get('date_to')

        Polissa = self._client.model('giscedata.polissa')
        Partner = self._client.model('res.partner')
        ProcesSwitching = self._client.model('giscedata.switching.proces')
        StepSwitching = self._client.model('giscedata.switching.step')
        E101 = self._client.model('giscedata.switching.e1.01')
        SwitchingWizard = self._client.model('giscedata.switching.wizard')

        e1s_objects = self._get_objects_with_attachment(
            model, date, process=process, step=step, date_to=date_to
        )
        e101_attachments = []

        e1_process_id = ProcesSwitching.search([('name','=','E1')])[0]

        for e1 in e1s_objects:
            pas_ids = E101.search([('sw_id', '=', e1.id)])
            if e1.polissa_ref_id and pas_ids:
                steps = StepSwitching.search([('proces_id','=', e1_process_id)])

                pas_id = pas_ids[0]
                e101_step = sorted(steps)[0]
                step_id = str( (e101_step, pas_id) )

                titular_id = Polissa.read(e1.polissa_ref_id.id, ['titular'])['titular'][0]
                lang = Partner.read(titular_id, ['lang'])['lang']

                id_wiz = SwitchingWizard.create(
                    {'step_id': step_id, 'mark_as_processed': 0},
                    {'lang': lang, 'active_ids': [ e1.id], 'active_id':  e1.id}
                )
                name = "{}_{}_{}_{}_{}.xml".format(
                    e1.company_id.ref,
                    e1_process_id,
                    pas_id,
                    e1.cups_input,
                    datetime.now().isoformat()
                )

                SwitchingWizard.action_exportar_xml([id_wiz.id], {'active_ids': [ e1.id], 'active_id':  e1.id})

                attachments = SwitchingWizard.read(
                    [id_wiz.id],
                    ['file'],
                    {'lang': lang, 'bin_size': False, 'tz': 'Europe/Madrid', 'active_ids': [e1.id], 'active_id': e1.id}
                )
            
                e101_attachments.extend([{'name': name, 'datas': attachment['file']} for attachment in attachments])

        return e101_attachments

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
                ('state', '!=', 'cancel'),
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
