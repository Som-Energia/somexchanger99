import os
import base64
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from celery.utils.log import get_task_logger

from .erp_utils import ErpUtils
from .sftp_utils import SftpUtils
from .models import Curve2Exchange

ERP = ErpUtils()

logger = get_task_logger(__name__)


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


def get_curves(curve_name):
    '''
    Get curves of `curve_type` from all providers defined in ERP
    curve_name: technical name of the curve.
    '''
    sftp = None
    files_to_exchange = dict()
    curve = Curve2Exchange.objects.get(erp_name=curve_name)
    erp_utils = ErpUtils()

    providers_sftp = erp_utils.get_sftp_providers(curve.erp_name)
    for provider in providers_sftp:
        logger.info("Getting %s curves from %s", curve_name, provider['host'])
        try:
            sftp = SftpUtils(
                host=provider['host'],
                port=provider['port'],
                username=provider['user'],
                password=provider.get('password') or  '',
                base_dir=provider['root_dir']
            )
            pattern = '{}_syntax'.format(curve_name)
            files_to_exchange[provider['name']] = sftp.get_files_to_download(
                path=provider['root_dir'],
                pattern=provider[pattern],
                date=curve.last_upload or timezone.now() - timedelta(days=1)
            )
        except Exception as e:
            msg = "An uncontroled error happened getting curves from: "\
                  "%s, reason: %s"
            logger.exception(msg, provider['id'], str(e))
        finally:
            if sftp:
                sftp.close_conection()
                sftp = None
    curve.last_upload = timezone.now()
    curve.save()
    return files_to_exchange


def push_curves(curve2exchange, curves_files):
    '''
    curve2exchange: Curve object to exchange
    curves_files: Structure {provider: [(curve_file_path, file_name)]} with all
    files in providers to exchange
    '''
    sftp = None
    upload_result = dict()
    erp_utils = ErpUtils()
    try:
        neuro_sftp = SftpUtils(
            host=settings.SFTP_CONF['host'],
            port=settings.SFTP_CONF['port'],
            username=settings.SFTP_CONF['username'],
            password=settings.SFTP_CONF['password'],
            base_dir=curve2exchange.name
        )
        providers_sftp = erp_utils.get_sftp_providers(curve2exchange.erp_name)
        for provider in providers_sftp:
            num_exchange_files = 0
            try:
                sftp = SftpUtils(
                    host=provider['host'],
                    port=provider['port'],
                    username=provider['user'],
                    password=provider.get('password') or '',
                    base_dir=provider['root_dir']
                )
                for path, filename in curves_files[provider['name']]:
                    content_file = sftp.download_file_content(path)
                    logger.info("Uploading file %s to exchange sftp", filename)
                    neuro_sftp.upload_file(
                        content_file,
                        filename,
                        os.path.join(neuro_sftp._base_remote_dir, str(datetime.now().date()))
                    )
                    num_exchange_files += 1
            except Exception as e:
                msg = "An uncontroled error happened during uploading "\
                      "process, reason: %s"
                logger.exception(msg, str(e))
            finally:
                upload_result[provider['name']] = num_exchange_files
    except Exception as e:
        logger.exception("An uncontroled error happened, reason: %s", str(e))
    finally:
        neuro_sftp.close_conection()
        return upload_result
