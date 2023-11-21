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
        "error_digest" : errpr_digest
	}
    message = render_to_string("failure_email.txt", msg_context)
    subject = SUBJECT.format(level='', reason='')
    mail_admins(subject, message)
