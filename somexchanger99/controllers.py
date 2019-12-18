from datetime import datetime

from django.utils.timezone import now

from .models import Atr2Exchange, Curve2Exchange, File2Exchange
from .sftp_utils import SftpUtils
from .utils import (get_attachments, get_curves, get_meteologica_files,
                    push_curves, push_meteologica_files, send_attachments)


def exchange_xmls():
    sftp = SftpUtils(**settings.SFTP_CONF)
    today = str(datetime.now().date())
    attachments_result = [
        get_attachments(
            model=file2exchange.model,
            date=today,
            process=file2exchange.process,
            step=file2exchange.step
        )
        for file2exchange in Atr2Exchange.objects.filter(active=True)
    ]

    [send_attachments(sftp, attachment) for attachment in attachments_result]
    ftp.close_conection()


def exchange_curves():
    exchange_result = dict()

    curves_to_exchage = Curve2Exchange.objects.filter(active=True)
    for curve in curves_to_exchage:
        curves_files = get_curves(curve.erp_name)
        exchange_status = {
            distri: {'downloaded': len(curves_to_exchage)}
            for distri, curves_to_exchage in curves_files.items()
        }

        upload_result = push_curves(curve, curves_files)
        for distri, num_uploaded_curves in upload_result.items():
            exchange_status[distri]['uploaded'] = num_uploaded_curves

        exchange_result[curve.name] = exchange_status

    return exchange_result


def exchange_meteologica_predictions():
    exchange_result = dict()

    files2exchange = File2Exchange.objects.filter(
        origin__code_name='METEOLGC',
        active=True
    )

    files = get_meteologica_files(files2exchange)
    for file_type, founded_file_list in files:
        exchange_result[file_type] = {'downloaded': len(founded_file_list)}

    upload_res = push_meteologica_files(files)
    for file_type, uploaded_files in upload_res.items():
        exchange_result[file_type]['uploaded'] = uploaded_files

    files2exchange.update(last_upload=now())
    return exchange_result
