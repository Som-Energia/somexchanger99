from django.core.mail import mail_admins
from django.template.loader import render_to_string


SUBJECT = '''
    [SomExchanger] - {level}: {reason}
'''


def notify(results : dict):
    error_digest = {
        process: result for process, result in results.items() if "error" in result
    }

    # {task_name : task_error }

    msg_context = {
        "error_digest" : error_digest
	}
    message = render_to_string("somexchanger99/failure_email.txt", msg_context)
    subject = SUBJECT.format(level='', reason='')
    email_result = mail_admins(subject, message)
    return email_result
