from config.settings.local import METEO_CONF, SFTP_CONF
import logging

import paramiko
from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm

from somexchanger99.erp_utils import ErpUtils
from somexchanger99.ftp_utils import FtpUtils
from somexchanger99.sftp_utils import SftpUtils

paramiko_logger = logging.getLogger('paramiko.transport')
paramiko_logger.addHandler(logging.NullHandler())
paramiko_logger.propagate = False


class MayBeFTPException(Exception):
    pass


class Command(BaseCommand):
    help = 'Check connections to distributions sftps'

    def try_sftp(self, provider):
        sftp = None
        try:
            sftp = SftpUtils(
                host=provider['host'],
                port=provider['port'],
                username=provider['user'],
                password=provider.get('password') or '',
                base_dir=provider['root_dir']
            )
        except paramiko.ssh_exception.SSHException:
            raise MayBeFTPException()
        finally:
            if sftp:
                sftp.close_connection()

    def try_ftp(self, provider):
        ftp = None
        try:
            ftp = FtpUtils(
                host=provider['host'],
                username=provider['user'],
                password=provider.get('password') or '',
                base_dir=provider['root_dir']
            )
        finally:
            if ftp:
                ftp.close_connection()

    def handle(self, *args, **options):
        erp = ErpUtils()
        sftp_providers = erp.get_sftp_providers()

        sftp_providers.extend([
            {
                'name': 'SomSftp',
                'host': settings.SFTP_CONF['host'],
                'port': settings.SFTP_CONF['port'],
                'user': settings.SFTP_CONF['username'],
                'password':settings.SFTP_CONF['password'],
                'root_dir': settings.SFTP_CONF['base_dir']
            },
            {
                'name': 'MeteoFTP',
                'host': settings.METEO_CONF['host'],
                'port': settings.METEO_CONF.get('port', 21),
                'user': settings.METEO_CONF['username'],
                'password':settings.METEO_CONF['password'],
                'root_dir': settings.METEO_CONF['base_dir']
            }
        ])
        self.stdout.write(self.style.NOTICE('Checking connections...'))
        provider_tqdm = tqdm(sftp_providers, unit='', ncols=0)
        for provider in provider_tqdm:
            provider_tqdm.display(provider['name'], pos=0)
            try:
                self.try_sftp(provider)
            except MayBeFTPException:
                try:
                    self.try_ftp(provider)
                except Exception as e:
                    provider_tqdm.write(f"{provider['name']} {self.style.ERROR(str(e))}")
                else:
                    provider_tqdm.write(f"{provider['name']} {self.style.SUCCESS('OK')}")
            except Exception as e:
                provider_tqdm.write(f"{provider['name']} {self.style.ERROR(str(e))}")
            else:
                provider_tqdm.write(f"{provider['name']} {self.style.SUCCESS('OK')}")
