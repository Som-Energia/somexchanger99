import ftplib
import io
import logging
import os
import re

from dateutil import parser
from django.utils.timezone import make_aware
from pytz.exceptions import AmbiguousTimeError

logger = logging.getLogger(__name__)


class FtpUtils(object):

    def __init__(self, host, username, password, base_dir):
        self._client = ftplib.FTP(host, username, password)
        self.base_dir = base_dir

    def download_file_content(self, path):
        with io.BytesIO() as f:
            self._client.retrbinary('RETR {}'.format(path), f.write)
            f.seek(0)
            content = f.read().decode()

        return content

    def get_files_to_download(self, path, pattern, date):
        file_list = []

        try:
            for file_name, file_properties in self._client.mlsd(path):
                if file_properties['type'] == 'dir':
                    new_path = os.path.join(path, file_name)
                    file_list = file_list + self.get_files_to_download(new_path, pattern, date)
                try:
                    file_date = make_aware(parser.parse(file_properties['modify']), date.tzinfo)
                except AmbiguousTimeError as e:
                    msg = "An error ocurred in date comparation, reason: %s"
                    logger.error(msg, str(e))
                else:
                    match_file = re.match(r'{}'.format(pattern), file_name) and \
                                 file_date >= date
                    if match_file:
                        file_list.append(
                            (os.path.join(path, file_name), file_name)
                        )
        except ftplib.error_perm:
            logger.error("Path %s not found", path)
        except Exception as e:
            msg = "An uncontroled error happened getting files to download, "\
                  "reason: %s"
            logger.exception(msg, str(e))
        finally:
            return file_list

    def close(self):
        self._client.close()
