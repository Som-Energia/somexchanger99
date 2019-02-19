import logging
import os

from django.conf import settings
from paramiko.sftp_client import SFTPClient
from paramiko.transport import Transport

logger = logging.getLogger(__name__)


class FtpUtils(object):

    def __init__(self):
        self.__transport = Transport(
            (settings.SFTP_CONF['host'], int(settings.SFTP_CONF['port']))
        )
        self.__transport.connect(
            None, settings.SFTP_CONF['username'], settings.SFTP_CONF['password']
        )

        self._client = SFTPClient.from_transport(self.__transport)
        self._base_remote_dir = settings.SFTP_CONF['base_dir']

    def upload_file(self, content_file, file_name, remote_path):
        '''
        Upload `file` to the FTP
        '''
        try:
            with self._client.open(os.path.join(remote_path, file_name), 'w') as f:
                f.write(content_file)
        except FileNotFoundError:
            self._create_remote_path(remote_path)
            with self._client.open(os.path.join(remote_path, file_name), 'w') as f:
                f.write(content_file)
        except Exception as e:
            msg = "There was an uncontroled error uploading %s to %s: %s"
            logger.exception(
                msg, os.path.join(remote_path, file_name), settings.SFTP_CONF['host'], str(e)
            )
            raise e
        return os.path.join(remote_path, file_name)

    def close_conection(self):
        if self._client is not None:
            self._client.close()

        if self.__transport is not None:
            self.__transport.close()

    def _create_remote_path(self, remote_path):
        relative_path = os.path.relpath(
            remote_path, start=self._base_remote_dir
        )

        self.__create_path(
            self._base_remote_dir,
            list(os.path.split(relative_path))
        )

    def __create_path(self, base_dir, dir_list):
        if dir_list:
            first, *rest = dir_list
            path = os.path.join(base_dir, first)
            try:
                self._client.stat(path)
            except FileNotFoundError:
                self._client.mkdir(path)
            finally:
                self.__create_path(path, rest)
