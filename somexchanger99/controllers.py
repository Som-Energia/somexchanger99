from datetime import datetime

from .sftp_utils import SftpUtils

from .models import Curve2Exchange, Atr2Exchange
from .utils import get_curves, push_curves, get_attachments, send_attachments


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
    pass
