def notify():
    msg_context = {
        "task_name": result.task_name,
        "task_error": kwargs['exception'],
        "task_url": ""
	}
    message = render_to_string("failure_email.txt", msg_context)
    mail_admins(subject, message)
