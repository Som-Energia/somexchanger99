import ftplib
import io
import logging
import os
import re
from datetime import datetime

import ftputil
from dateutil import parser, tz
from django.utils.timezone import make_aware
from pytz.exceptions import AmbiguousTimeError

logger = logging.getLogger(__name__)


class FtpClientNative(ftplib.FTP):

    def listdir(self, path="."):
        return self.nlst(path)

    def getmtime(self, path):
        lst_dir_gen = self.mlsd(path)
        _, file_properties = lst_dir_gen.__next__()
        return parser.parse(
            file_properties['modify'], tzinfos={'UTC': tz.gettz('UTC')}
        )


class FtpClientFtpUtil(ftputil.FTPhost):

    def retrbinary(self, cmd, callback, blocksize=8192, rest=None):
        return self._session.retrbinary(cmd, callback, blocksize, rest)

    def getmtime(self, path):
        return datetime.utcfromtimestamp(self.path.getmtime(path))


class FtpClient(object):

    def __init__(self, host, username, password, native=True):
        return FtpClientNative(host, username, password) if native else FtpClientFtpUtil(host, username, password)


class FtpUtils(object):

    def __init__(self, host, username, password, base_dir, native=True):
        self._client = ftputil.FTPHost(host, username, password, native)
        self.base_dir = base_dir

    def download_file_content(self, path):
        with io.BytesIO() as f:
            self._client.retrbinary('RETR {}'.format(path), f.write)
            f.seek(0)
            content = f.read().decode()

        return content

    def get_files_to_download(self, path, pattern, date_from):
        msg = "Getting files from %s that match pattern %s and are newer than %s"
        logger.debug(msg, path, pattern, str(date_from))
        file_list = []

        try:
            for file_name in self._client.listdir(path):
                if self._client.path.isdir(file_name):
                    new_path = os.path.join(path, file_name)

                    file_list = file_list + self.get_files_to_download(new_path, pattern, date_from)
                try:
                    full_path_file = os.path.join(path, file_name)
                    file_date = make_aware(
                        self._client.getmtime(full_path_file),
                        date_from.tzinfo
                    )
                except AmbiguousTimeError as e:
                    msg = "An error ocurred in date comparation, reason: %s"
                    logger.error(msg, str(e))
                else:
                    match_file = re.match(r'{}'.format(pattern), file_name) and \
                                 file_date >= date_from
                    if match_file:
                        file_list.append((full_path_file, file_name))
        except ftputil.error.FTPError as e:
            logger.error(e)
            logger.error("Path %s not found", path)
        except Exception as e:
            msg = "An uncontroled error happened getting files to download, "\
                  "reason: %s"
            logger.exception(msg, str(e))
        finally:
            return file_list

    def close_connection(self):
        self._client.close()
