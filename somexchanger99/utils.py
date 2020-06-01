import base64
import os
from datetime import datetime, timedelta

from celery.utils.log import get_task_logger
from dateutil import parser
from django.conf import settings
from django.utils import timezone

from .erp_utils import ErpUtils
from .ftp_utils import FtpUtils
from .models import Curve2Exchange
from .sftp_utils import SftpUtils, SftpUploadException

ERP = ErpUtils()

logger = get_task_logger(__name__)


def get_attachments(model, date, process, **kwargs):
    step = kwargs.get('step')
    msg = "{process}{step}{date}".format(
        process="Getting attachments of proces %s ",
        step="step %s " if step else "%s",
        date="at date %s"
    )
    logger.info(msg, process, step or '', str(date))

    attachments = ERP.get_attachments(
        model=model,
        date=date,
        process=process,
        step=step,
        date_to=kwargs.get('date_to')
    )
    attachments_result = {
        'date': str(date.date()),
        'process': process,
        'attachments': attachments
    }
    if step:
        attachments_result['step'] = step

    msg = "Founded %s attachments of process %s at date %s"
    logger.info(msg, len(attachments_result['attachments']), process, str(date))
    return attachments_result


def upload_attach_to_sftp(sftp, attachment, path):

    logger.info("Uploading %s to %s", attachment['name'], path)
    try:
        attach_conent = base64.decodebytes(
            attachment['datas'].encode()
        ).decode('iso-8859-1')
        file_uploaded = sftp.upload_file(attach_conent, attachment['name'], path)
    except SftpUploadException as e:
        logger.error(e.message)
    else:
        logger.info("%s succesfully uploaded to %s", attachment['name'], path)
        return file_uploaded


def send_attachments(sftp, object_attachment):
    path = lambda date: os.path.join(
        settings.SFTP_CONF['base_dir'],
        str(date),
        object_attachment['process'],
        object_attachment.get('step', '')
    )

    upload_results = [
        upload_attach_to_sftp(
            sftp, attachment, path(parser.parse(attachment['create_date']).date())
        )
        for attachment in object_attachment['attachments']
    ]

    return '{}{}'.format(object_attachment.get('process'), object_attachment.get('step', '')), len(upload_results)



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


def get_meteologica_files(files2exchange):
    logger.info("Getting meteologica predictions")
    meteo_ftp = FtpUtils(**settings.METEO_CONF)
    meteologica_files = []

    meteologica_files = [
        (file_.name, meteo_ftp.get_files_to_download(meteo_ftp.base_dir, file_.pattern, file_.last_upload))
        for file_ in files2exchange
    ]
    logger.info("Founded %d preditcion files", len(meteologica_files))

    meteo_ftp.close()
    return meteologica_files


def push_meteologica_files(files2upload):
    meteo_ftp = FtpUtils(**settings.METEO_CONF)
    enexpa_sftp = SftpUtils(**settings.ENEXPA_CONF)
    upload_result = dict()

    for files in files2upload:
        num_exchange_files = 0
        file_type, files_to_upload = files
        msg = "Uploading %d files of plant %s from meteologica to our sftp"
        logger.info(msg, len(files_to_upload), file_type)

        for path, file_name in files_to_upload:
            content_file = meteo_ftp.download_file_content(path)
            enexpa_sftp.upload_file(
                content_file,
                file_name,
                os.path.join(enexpa_sftp._base_remote_dir, '')
            )
            num_exchange_files += 1
        upload_result[file_type] = num_exchange_files

    meteo_ftp.close()
    return upload_result
