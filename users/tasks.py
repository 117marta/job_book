from celery import shared_task
from django.utils.html import strip_tags

from users.helpers import convert_to_html_content
from users.models import User


@shared_task
def send_email_with_celery(user_pk, subject, content, template_name="users/email.html"):
    """
    Send an email as an asynchronous task that runs independently of Django app.

    :param int user_pk: a user pk
    :param str subject: a subject of an e-mail
    :param str content: a content of an e-mail
    :param str template_name: a template name of an e-mail
    """
    user = User.objects.get(pk=user_pk)
    html_message = convert_to_html_content(
        template_name=template_name,
        context={
            "user_name": user.get_full_name(),
            "content": content,
        },
    )
    user.email_user(
        subject=subject,
        message=strip_tags(html_message),
        html_message=html_message,
    )
