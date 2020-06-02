from django.db import models
from django.utils.translation import ugettext as _


class ProviderConnection(models.Model):

    name = models.CharField(
        max_length=64,
        verbose_name=_('Name'),
        help_text=_('Provider name (endesa, fenosa...)')
    )

    host = models.CharField(
        max_length=64,
        verbose_name=_('Host'),
        help_text=_('Hostname or ip')
    )

    port = models.PositiveIntegerField(
        verbose_name=_('Port'),
        help_text=_('Port to connect')
    )

    username = models.CharField(
        max_length=64,
        verbose_name=_('Username'),
        help_text=_('User name of the connection')
    )

    password = models.CharField(
        max_length=128,
        verbose_name=_('Password'),
        help_text=_('Password of the connection')
    )

    base_dir = models.CharField(
        max_length=128,
        verbose_name=_('Base directory'),
        help_text=_('Base directory when start a connection')
    )

    secure = models.BooleanField(
        default=True,
        verbose_name=_('Secure'),
        help_text=_('Set if this connection will be secure or not, default true')
    )

    active = models.BooleanField(
        verbose_name=_('Active'),
        help_text=_('Check to enable or disable this provider')
    )

    class Meta:
        verbose_name = _('Provider connection')
        verbose_name_plural = _('Provider connections')

    def __str__(self):
        return f'<ProviderConnection({self.name}, active:{self.active}, '\
               f'{self.host}:{self.port})>'

    def __repr__(self):
        return self.__str__()


class Curve2Exchange(models.Model):

    name = models.CharField(
        max_length=20,
        verbose_name=_('Name'),
        help_text=_('Name of the curve (p1d, f5d....)')
    )

    pattern = models.CharField(
        max_length=255,
        verbose_name=_('Pattern'),
        help_text=_('Pattern (python regex) of the curve file'),
        null=True
    )

    active = models.BooleanField(
        verbose_name=_('Active'),
        help_text=_('Check to enable or disable exchange this kind of curves')
    )

    last_upload = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last date uploaded'),
        help_text=_('Last time this kind of curves was uploaded'),
    )

    provider_connection = models.ForeignKey(
        to=ProviderConnection,
        on_delete=models.SET_NULL,
        related_name='curve2exchange',
        null=True,
        verbose_name=_('Provider'),
        help_text=_('Provider connection'),
    )

    class Meta:
        verbose_name = _('Curve to exchange')
        verbose_name_plural = _('Curves to exchane')

    def __str__(self):
        return f'<Curve2Exchange({self.name}, active:{self.active}, '\
               f'provider:{self.provider_connection.name})>'

    def __repr__(self):
        return self.__str__()
