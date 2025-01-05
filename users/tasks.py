from smtplib import SMTPException

from celery import shared_task
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.utils.html import strip_tags


@shared_task
def email_to_user(recipient, subject, html_message, attachments):
    """
    Send an email as an asynchronous task that runs independently of Django app.

    :param str recipient: a recipient of an e-mail
    :param str subject: a subject of an e-mail
    :param str html_message: an alternative representation of the message body in the email
    :param list attachments: a list of attachments to put on the message
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_message),
        from_email=None,
        to=[recipient],
        bcc=None,
        reply_to=None,
        headers=None,
    )
    if attachments:
        for attachment in attachments:
            email.attach_file(attachment)
    if html_message:
        email.attach_alternative(content=html_message, mimetype="text/html")

    try:
        email.send()
    except BadHeaderError:
        print("Subject is not properly formatted.")
    except SMTPException as error:
        print(
            f"There was an error while trying to send a `{subject}` email to the {recipient} user. {error}"
        )
