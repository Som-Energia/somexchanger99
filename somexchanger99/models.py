from django.db import models
from django.utils.translation import ugettext as _


class File2Exchange(models.Model):

    process = models.CharField(
        max_length=128,
        verbose_name=_('Process'),
        help_text=_('ATR process (F1, A3, C1, ...)')
    )

    step = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_('Step'),
        help_text=_('Step of the ATR process. No used when process is F1')
    )

    model = models.CharField(
        max_length=256,
        verbose_name=_('ERP model'),
        help_text=_('Dotted model name in erp, eg. \"giscedata.switching\"')
    )

    def __str__(self):
        exchange_attrs = '{process}, {model}' if not self.step \
                         else '{process}, {step}, {model}'

        return '<File2Exchange({})>'.format(
            exchange_attrs.format(**self.__dict__)
        )

    def __repr__(self):
        return self.__str__()

# class ExchangeResult(models.Model):

#     IN_PROGESS = 'IN_PROGESS'
#     UPLOADED = 'UPLOADED'
#     FAILED = 'FAILED'

#     STATES = (
#         (IN_PROGESS, _('In progess')),
#         (UPLOADED, _('Uploaded')),
#         (FAILED, _('Failed')),
#     )

#     exchange_type = models.ForeignKey(
#         File2Exchange,
#         on_delete=models.SET_NULL,
#         null=True,
#         verbose_name=_('Kind of file uploaded'),
#         help_text=_('Type of file uploaded')
#     )

#     file_name = models.CharField(
#         max_length=128,
#         db_index=True,
#         verbose_name=_('File'),
#         help_text=_('Name of the file')
#     )

#     erp_attach_id = models.IntegerField(
#         db_index=True,
#         verbose_name=_('ERP Attachment id'),
#         help_text=_('ERP Attachment Id')
#     )

#     state = models.CharField(
#         max_length=15,
#         choices=STATES,
#         verbose_name=_('State'),
#         help_text=_('State of the file')
#     )

#     uploaded_date = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_('Uploaded date'),
#         help_text=_('Date when the file was uploaded')
#     )

#     reasons = models.TextField(
#         verbose_name=_('Reasons of the errors'),
#         help_text=_(
#             'Show information about the reasons when the state of a '
#             'file is Failed'
#         )
#     )
