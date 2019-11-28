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

    active = models.BooleanField(
        verbose_name=_('Active'),
        help_text=_('Shows if this kind of files will be exchanged')
    )

    def __str__(self):
        exchange_attrs = '{process}, {model}' if not self.step \
                         else '{process}, {step}, {model}'

        return '<File2Exchange({})>'.format(
            exchange_attrs.format(**self.__dict__)
        )

    def __repr__(self):
        return self.__str__()


class Curve2Exchange(models.Model):

    name = models.CharField(
        max_length=20,
        verbose_name=_('Name'),
        help_text=_('Name of the curve (p1d, f5d....)')
    )

    erp_name = models.CharField(
        max_length=20,
        verbose_name=_('ERP Name'),
        help_text=_('Name of the curve in ERP (p1, f5d....)'),
        null=True
    )

    active = models.BooleanField(
        verbose_name=_('Active'),
        help_text=_('Check to enable or disable exchange this kind of curves')
    )

    last_upload = models.DateTimeField(
        verbose_name=_('Last date uploaded'),
        help_text=_('Last time this kind of curves was uploaded')
    )

    def __str__(self):

        return '<Curve2Exchange({name}, active:{active})>'.format(
            **self.__dict__
        )

    def __repr__(self):
        return self.__str__()
