

def notify(results : dict):



    msg_context = {
        "task_name": result.task_name,
        "task_error": kwargs['exception'],
        "task_url": ""
	}
    message = render_to_string("failure_email.txt", msg_context)
    prints(message)
    #mail_admins(subject, message)
