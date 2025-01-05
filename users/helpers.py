from django.conf import settings
from django.template.loader import render_to_string

from users.models import User
from users.tasks import email_to_user


def convert_to_html_content(template_name, context):
    return render_to_string(
        template_name=template_name,
        context=context,
    )


def html_content(user_name, content, template_name):
    return convert_to_html_content(
        template_name=template_name,
        context={
            "user_name": user_name,
            "content": content,
        },
    )


def send_email(recipients, subject, content, template_name=settings.EMAIL_TEMPLATE, attachments=None):  # fmt: skip
    """
    Prepare to send an e-mail to the recipients list.

    :param list recipients: a list of strings, each an email address
    :param str subject: a subject of an e-mail
    :param str content: a content of an e-mail
    :param str template_name: a template name of an e-mail
    :param list attachments: a list of attachments to put on the message
    """
    for recipient in recipients:
        try:
            to_user_name = User.objects.get(email=recipient).get_full_name()
        except User.DoesNotExist:
            to_user_name = "User"
        html_message = html_content(
            user_name=to_user_name, content=content, template_name=template_name
        )

        if settings.SEND_EMAIL_CELERY:
            email_to_user.delay(recipient, subject, html_message, attachments)
        else:
            email_to_user(recipient, subject, html_message, attachments)
