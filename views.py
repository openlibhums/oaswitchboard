"""
Views for the OAS plugin.
"""

__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from plugins.oas import forms
from security import decorators

from oas.logic import get_plugin_settings, save_plugin_settings


@staff_member_required
@decorators.has_journal
def manager(request):
    """
    The manager view for the OAS plugin.
    :param request: the request object
    """
    (
        oas_enabled,
        oas_email,
        oas_sandbox,
        oas_password,
        oas_url,
        oas_sandbox_url,
    ) = get_plugin_settings(request)

    if request.POST:
        form = forms.OASManagerForm(request.POST)

        if form.is_valid():
            oas_enabled = form.cleaned_data["enabled"]
            oas_email = form.cleaned_data["email"]
            oas_sandbox = form.cleaned_data["sandbox"]
            oas_password = form.cleaned_data["password"]
            oas_url = form.cleaned_data["url"]
            oas_sandbox_url = form.cleaned_data["sandbox_url"]

            save_plugin_settings(
                oas_email,
                oas_enabled,
                oas_password,
                oas_sandbox,
                oas_sandbox_url,
                oas_url,
                request,
            )

    else:
        form = forms.OASManagerForm(
            initial={
                "enabled": oas_enabled,
                "email": oas_email,
                "sandbox": oas_sandbox,
                "password": oas_password,
                "url": oas_url,
                "sandbox_url": oas_sandbox_url,
            }
        )

    template = "oas/manager.html"
    context = {
        "form": form,
    }

    return render(request, template, context)
