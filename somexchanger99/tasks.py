from config import celery_app

from .controllers import exchange_curves, exchange_meteologica_predictions


@celery_app.task(ignore_result=False)
def exchange_xmls_task():
    '''
    Xml exchange task
    '''
    return exchange_xmls()


@celery_app.task(ignore_result=False)
def exchange_curves_task():
    return exchange_curves()


@celery_app.task(ignore_result=False)
def exchange_meteologica_predictions_task():
    return exchange_meteologica_predictions()
