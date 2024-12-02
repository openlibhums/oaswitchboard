from django.template.loader import render_to_string


def menu_hook(context):
    template = render_to_string(
        "oas/elements/menu_nav.html",
    )

    return template
