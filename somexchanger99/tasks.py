import base64
import os
from datetime import datetime

from django.conf import settings
from celery.utils.log import get_task_logger

from config import celery_app
from .erp_utils import ErpUtils
from .sftp_utils import SftpUtils
from .models import File2Exchange


logger = get_task_logger(__name__)

ERP = ErpUtils()


def get_attachments(model, date, process, step=None):

    logger.info("Getting attachments of process: %s", process)

    attachments = ERP.get_attachments(
        model=model,
        date=date,
        process=process,
        step=step
    )
    attachments_result = {
        'date': date,
        'process': process,
        'attachments': attachments
    }
    if step:
        attachments_result['step'] = step

    msg = "Founded %s attachments of process: %s"
    logger.info(msg, len(attachments_result['attachments']), process)
    return attachments_result


def upload_attach_to_sftp(sftp, attachment, path):

    logger.info("Uploading %s to %s", attachment['name'], path)

    attach_conent = base64.decodebytes(
        attachment['datas'].encode()
    ).decode('iso-8859-1')
    sftp.upload_file(attach_conent, attachment['name'], path)

    logger.info("%s succesfully uploaded to %s", attachment['name'], path)


def send_attachments(sftp, object_attachment):
    path = os.path.join(
        settings.SFTP_CONF['base_dir'],
        object_attachment['date'],
        object_attachment['process'],
        object_attachment.get('step', '')
    )
    upload_results = [
        upload_attach_to_sftp(sftp, attachment, path)
        for attachment in object_attachment['attachments']
    ]


@celery_app.task(ignore_result=False)
def exchange_files():
    '''
    Main task in charge to exchange erp attachments
    '''
    sftp = SftpUtils()
    today = str(datetime.now().date())
    attachments_result = [
        get_attachments(
            model=file2exchange.model,
            date=today,
            process=file2exchange.process,
            step=file2exchange.step
        )
        for file2exchange in File2Exchange.objects.filter(active=True)
    ]

    [send_attachments(sftp, attachment) for attachment in attachments_result]
    sftp.close_conection()
