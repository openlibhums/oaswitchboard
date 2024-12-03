"""
Implements the admin pages for the OA Switchboard plugin
"""

__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from plugins.oas import models


class SwitchboardMessageAdmin(ModelAdmin):
    """
    The admin interface for the switchboard messages
    """

    list_display = (
        "success",
        "broadcast",
        "message_type",
        "article",
        "_journal",
        "message",
        "response",
    )
    list_filter = (
        "success",
        "broadcast",
        "message_type",
        "article",
        "message",
        "response",
    )

    def _journal(self, obj):
        return obj.article.journal


admin_list = [
    (models.SwitchboardMessage, SwitchboardMessageAdmin),
]

[admin.site.register(*t) for t in admin_list]
