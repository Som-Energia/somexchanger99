import base64
import os
from datetime import datetime, timedelta

from django.conf import settings
from celery.utils.log import get_task_logger

from config import celery_app
from .erp_utils import ErpUtils
from .sftp_utils import SftpUtils
from .models import Curve2Exchange, File2Exchange


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
def exchange_xmls():
    '''
    Main task in charge to exchange erp attachments
    '''
    sftp = SftpUtils(**settings.SFTP_CONF)
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


@celery_app.task(ingnore_result=False)
def exchange_curves():

    curves_to_exchage = Curve2Exchange.filter(active=True)

    result = []

    for curve in curves_to_exchage:
        result.append(exchange_curve.delay(curve.name))

    return result


@celery_app.task(ignore_result=False)
def exchange_curve(curve_type):
    return get_curves(curve_type)


def get_curves(curve_type):
    '''
    Get curves of `curve_type` from all providers defined in ERP
    '''
    files_to_exchange = dict()
    from_date = datetime.now() - timedelta(days=1)
    erp_utils = ErpUtils()

    providers_sftp = erp_utils.get_sftp_providers(curve_type)
    for provider in providers_sftp:
        logger.info("Getting curves from %s", provider['host'])
        try:
            sftp = SftpUtils(
                host=provider['host'],
                port=provider['port'],
                username=provider['user'],
                password=provider['password'] or '',
                base_dir=provider['root_dir']
            )
            pattern = '{}_syntax'.format(curve_type)
            files_to_exchange[provider['name']] = sftp.get_files_to_download(
                path=provider['root_dir'],
                pattern=provider[pattern],
                date=from_date
            )
        except Exception as e:
            msg = "An uncontroled error happened getting curves from: "\
                  "%s, reason: %s"
            logger.exception(msg, provider['id'], str(e))
        finally:
            sftp.close_conection()

    return files_to_exchange


def push_curves(curves_files):

    try:
        neuro_sftp = SftpUtils(
            host=settings.SFTP_CONF['host'],
            port=settings.SFTP_CONF['port'],
            username=settings.SFTP_CONF['username'],
            password=settings.SFTP_CONF['password'],
            base_dir=curve_type
        )

        try:
            sftp = SftpUtils(
                host=provider['host'],
                port=provider['port'],
                username=provider['user'],
                password=provider['password'],
                base_dir=provider['root_dir']
            )
            for path, filename in curves_files:
                content_file = sftp.download_file_content(path)
                logger.info("Uploading file %s to exchange sftp", filename)
                neuro_sftp.upload_file(
                    content_file,
                    filename,
                    os.path.join(neuro_sftp._base_remote_dir, str(datetime.now().date()))
                )
        except Exception as e:
            msg = "An uncontroled error happened during uploading "\
                  "process, reason: %s"
            logger.exception(msg, str(e))
        finally:
            sftp.close_conection()
    except Exception as e:
        logger.exception("An uncontroled error happened, reason: %s", str(e))
    finally:
        neuro_sftp.close_conection()
