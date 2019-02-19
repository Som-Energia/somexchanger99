import base64
import logging

from config import celery_app

from .erp_utils import ErpUtils
from .ftp_utils import FtpUtils


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
