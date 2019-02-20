import base64
import logging
from datetime import datetime

from config import celery_app

from .erp_utils import ErpUtils
from .ftp_utils import FtpUtils
from .models import File2Exchange


logger = logging.getLogger(__name__)

ERP = ErpUtils()
FTP = FtpUtils()

@celery_app.task()
def get_attachements(model, date, process, step=None):
    attachments_result = {
        'date': date,
        'process': process,
        'attachements': ERP.get_attachments(
            model=model,
            date=date,
            process=process,
            step=step
        )
    }
    if step:
        attachments_result['step'] = step

    return attachments_result


@celery_app.task()
def upload_attach_to_ftp(attachment, path):
    attach_conent = base64.decodebytes(
        attachment['datas'].encode()
    ).decode('iso-8859-1')
    FTP.upload_file(attach_conent, attachment['name'], path)
