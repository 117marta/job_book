from django.template.loader import render_to_string
from django.utils.html import strip_tags


def convert_to_html_content(template_name, context):
    return render_to_string(
        template_name=template_name,
        context=context,
    )


def plain_message():
    return strip_tags(convert_to_html_content)
