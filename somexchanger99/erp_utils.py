from operator import itemgetter

from django.conf import settings
from erppeek import Client


class ErpUtils(object):

    def __init__(self):
        self._client = Client(**settings.ERP_CONF)

    def get_attachments(self, model, date, process, step=None):
        '''
        Obtain file attachments of the process `process` in the step `step`
        associated with the `model` on date `date`.

        `process`: can be any ATR process (F1, A3, M1, ...)
        `step`: step of the `process` if is a switching process (A3, C1, M1, ...)
        `model`: ERP model
        `date`: Creation date
        '''
        objects = self._get_objects_with_attachment(
            model, date, process=process, step=step
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

        return attachments if not step else self.__step_filter(attachments, step)

    def _get_objects_with_attachment(self, model, date, **kwargs):
        Model = self._client.model(model)
        object_query = self.__get_object_query(model, date, **kwargs)
        objects = Model.browse(object_query)

        return objects

    def __get_object_query(self, model, date, **kwargs):

        BASE_QUERY = {
            'giscedata.facturacio.importacio.linia': [
                ('state', '=', 'valid'),
                ('data_carrega', '>=', date)
            ],
            'giscedata.switching': [
                ('proces_id.name', '=', kwargs.get('process')),
                ('step_id.name', '=', kwargs.get('step')),
                ('date', '>=', date)
            ]
        }

        return BASE_QUERY[model]

    def __step_filter(self, attachements, step):
        get_description = itemgetter('description')
        step_filter = 'Pas: {}'.format(step)

        return [
            attach for attach in attachements
            if step_filter in get_description(attach)
        ]
