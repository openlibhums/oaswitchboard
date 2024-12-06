"""
Views for the OAS plugin.
"""

__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render, reverse, redirect
from django.views.decorators.http import require_POST
from plugins.oas import forms, logic
from security import decorators
from submission import models as submission_models

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


@decorators.editor_user_required
def list_articles(request):
    """
    List the articles for the OAS plugin.
    :param request: the request object
    """
    articles = submission_models.Article.objects.filter(
        journal=request.journal
    ).order_by("-date_published")

    template = "oas/listing.html"
    context = {
        "articles": articles,
    }

    return render(request, template, context)


@require_POST
@decorators.editor_user_required
def send_article(request):
    """
    Send an article to the OA Switchboard.
    :param request: the request object
    """
    article_id = request.POST.get("article_id")
    article = get_object_or_404(
        submission_models.Article,
        id=article_id,
        journal=request.journal,
    )

    kwargs = {"article": article, "request": request}

    logic.publication_event_handler(**kwargs)

    return redirect(
        reverse("admin:oas_switchboardmessage_changelist")
        + "?article__id__exact="
        + article_id
    )
