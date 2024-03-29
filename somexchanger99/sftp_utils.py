import logging
import os
import re
import stat
from datetime import datetime as dt
from operator import attrgetter

from django.conf import settings
from django.utils.timezone import make_aware
from paramiko.sftp_client import SFTPClient
from paramiko.transport import Transport
from pytz.exceptions import AmbiguousTimeError

paramiko_logger = logging.getLogger('paramiko.transport')
paramiko_logger.addHandler(logging.NullHandler())
paramiko_logger.propagate = False

logger = logging.getLogger(__name__)


class SftpUploadException(Exception):
    pass


class SftpUtils(object):

    def __init__(self, host, port, username, password, base_dir):
        self.__transport = Transport(
            (host, int(port))
        )

        self.__transport._preferred_kex = (
            'ecdh-sha2-nistp256',
            'ecdh-sha2-nistp384',
            'ecdh-sha2-nistp521',
            'diffie-hellman-group-exchange-sha256',
            'diffie-hellman-group14-sha256',
            'diffie-hellman-group-exchange-sha1',
            'diffie-hellman-group14-sha1',
            'diffie-hellman-group1-sha1',
        )

        self.__transport.start_client()
        self.__transport.get_remote_server_key()
        self.__transport.auth_password(username, password)

        self._client = SFTPClient.from_transport(self.__transport)

        self._base_remote_dir = base_dir

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
                msg,
                os.path.join(remote_path, file_name),
                settings.SFTP_CONF['host'],
                str(e)
            )
            raise SftpUploadException(e.message) from e
        return os.path.join(remote_path, file_name)

    def download_file_content(self, path):
        with self._client.open(path) as f:
            content = f.read()

        return content

    def get_files_to_download(self, path, pattern, date_from, date_to=None):
        msg = "Getting files from %s that match pattern %s and are newer than %s"
        logger.debug(msg, path, pattern, str(date_from))
        mtime = attrgetter('st_mtime')
        mtime_aware = lambda timestamp, tzinfo: make_aware(
            dt.fromtimestamp(timestamp), tzinfo
        )
        file_list = []

        try:
            dir_content = sorted(
                self._client.listdir_attr(path), key=mtime, reverse=True
            )
            for file_ in dir_content:
                if stat.S_ISDIR(file_.st_mode):
                    new_path = os.path.join(path, file_.filename)
                    file_list = file_list + self.get_files_to_download(
                        new_path, pattern, date_from, date_to
                    )
                try:
                    if mtime_aware(file_.st_mtime, date_from.tzinfo) < date_from:
                        continue

                    match_file_conditions = [
                        re.match(pattern, file_.filename),
                        mtime_aware(file_.st_mtime, date_from.tzinfo) >= date_from
                    ]
                    if date_to:
                        match_file_conditions.append(
                            mtime_aware(file_.st_mtime, date_from.tzinfo) < date_to
                        )
                except AmbiguousTimeError as e:
                    msg = "An error ocurred in date comparation for file %s, reason: %s"
                    logger.error(msg, file_.filename, str(e))
                else:
                    if all(match_file_conditions):
                        file_list.append(
                            (os.path.join(path, file_.filename), file_.filename)
                        )
        except FileNotFoundError:
            logger.error("Path %s not found", path)
        except Exception as e:
            msg = "An uncontroled error happened getting files to download, "\
                  "reason: %s"
            logger.exception(msg, str(e))
        finally:
            return file_list

    def close_connection(self):
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
            relative_path.split(os.path.sep)
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
