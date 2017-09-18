from flask import current_app
from requests import post

from meido.models import User


def send_email(project, subject, text):
    if not current_app.config['MAILGUN_ENABLED']:
        return

    to_addresses = [u.email for u in project.subscribed_users]
    data = {
        "from": 'Meido <{}>'.format(current_app.config['MAILGUN_SENDER']),
        "to": to_addresses,
        "subject": subject,
        "text": text,
    }
    if not data['to']:
        return
    return post(current_app.config['MAILGUN_URL'], data=data,
                auth=("api", current_app.config['MAILGUN_KEY']))


def upload_failed(project, build_number, reason=None):
    """Send an email notification to all users informing of a failed build upload."""
    formatting = {
        'name': project.name,
        'number': build_number,
        'reason': reason if reason else 'UNKNOWN',
    }
    title = '{name}: upload failed'.format(**formatting)
    message = ('Build #{number} failed to upload for project {name}.\n'
               '\n'
               'REASON: {reason}'
               .format(**formatting))
    send_email(project, title, message)


def upload_successful(project, build_number):
    """Send an email notification to all users informing of a successful build upload."""
    formatting = {
        'name': project.name,
        'number': build_number,
    }
    title = '{name}: upload successful'.format(**formatting)
    message = ('Build #{number} was successfully uploaded for project {name}.'
               .format(**formatting))
    send_email(project, title, message)
