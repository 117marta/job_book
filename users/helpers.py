from django.template.loader import render_to_string


def convert_to_html_content(template_name, context):
    return render_to_string(
        template_name=template_name,
        context=context,
    )
