__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"

from django.shortcuts import get_object_or_404, redirect, render
from plugins.oas import forms, plugin_settings
from utils import models, setting_handler


def manager(request):

    oas_enabled = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_send"
    )

    oas_email = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_email"
    )

    oas_sandbox = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_sandbox"
    )

    oas_password = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_password"
    )

    oas_url = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_url"
    )

    oas_sandbox_url = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_sandbox_url"
    )

    if request.POST:
        form = forms.OASManagerForm(request.POST)

        if form.is_valid():
            oas_enabled = form.cleaned_data["enabled"]
            oas_email = form.cleaned_data["email"]
            oas_sandbox = form.cleaned_data["sandbox"]
            oas_password = form.cleaned_data["password"]
            oas_url = form.cleaned_data["url"]
            oas_sandbox_url = form.cleaned_data["sandbox_url"]

            setting_handler.save_setting(
                setting_group_name="plugin:oaswitchboard_plugin",
                setting_name="oas_send",
                journal=request.journal,
                value=oas_enabled,
            )

            setting_handler.save_setting(
                setting_group_name="plugin:oaswitchboard_plugin",
                setting_name="oas_email",
                journal=request.journal,
                value=oas_email,
            )

            setting_handler.save_setting(
                setting_group_name="plugin:oaswitchboard_plugin",
                setting_name="oas_sandbox",
                journal=request.journal,
                value=oas_sandbox,
            )

            setting_handler.save_setting(
                setting_group_name="plugin:oaswitchboard_plugin",
                setting_name="oas_password",
                journal=request.journal,
                value=oas_password,
            )

            setting_handler.save_setting(
                setting_group_name="plugin:oaswitchboard_plugin",
                setting_name="oas_url",
                journal=request.journal,
                value=oas_url,
            )

            setting_handler.save_setting(
                setting_group_name="plugin:oaswitchboard_plugin",
                setting_name="oas_sandbox_url",
                journal=request.journal,
                value=oas_sandbox_url,
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
