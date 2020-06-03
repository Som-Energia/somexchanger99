from django.db import models
from django.utils.translation import ugettext as _


class Atr2Exchange(models.Model):

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

    last_upload = models.DateTimeField(
        verbose_name=_('Last date uploaded'),
        help_text=_('Last time this atr process was uploaded'),
        null=True,
        blank=True
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

    pattern = models.CharField(
        max_length=128,
        verbose_name=_('Pattern'),
        help_text=_('Patern of the curve file'),
        null=False
    )

    active = models.BooleanField(
        verbose_name=_('Active'),
        help_text=_('Check to enable or disable exchange this kind of curves')
    )

    last_upload = models.DateTimeField(
        verbose_name=_('Last date uploaded'),
        help_text=_('Last time this kind of curves was uploaded'),
        null=True,
        blank=True
    )

    def __str__(self):

        return '<Curve2Exchange({name}, active:{active})>'.format(
            **self.__dict__
        )

    def __repr__(self):
        return self.__str__()


class OriginFile(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name=_('Name'),
        help_text=_('Description name of the origin, eg. Meteologica')
    )

    code_name = models.CharField(
        max_length=20,
        verbose_name=_('Code'),
        help_text=_('Code name of the origin, eg. METEOLGC')
    )

    def __str__(self):
        return '<OriginFile({name}, code_name:{code_name})>'.format(
            **self.__dict__
        )

    def __repr__(self):
        return self.__str__()


class File2Exchange(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name=_('Name'),
        help_text=_('Description name of the file to exchange, eg \"Predicción Matallana\"')
    )

    origin = models.ForeignKey(
        to='OriginFile',
        on_delete=models.CASCADE,
        verbose_name=_('Origin'),
        help_text=_('Origin of this file')
    )

    pattern = models.CharField(
        max_length=20,
        verbose_name=_('Pattern'),
        help_text=_('Pattern of the name to search the file. Has to be a python regex'),
        null=True
    )

    active = models.BooleanField(
        verbose_name=_('Active'),
        help_text=_('Check to enable or disable exchange this kind of files')
    )

    last_upload = models.DateTimeField(
        verbose_name=_('Last date uploaded'),
        help_text=_('Last time this kind of files was uploaded'),
        null=True,
        blank=True
    )

    def __str__(self):

        return '<File2Exchange({name}, active:{active})>'.format(
            **self.__dict__
        )

    def __repr__(self):
        return self.__str__()
