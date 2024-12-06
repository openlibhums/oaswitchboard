"""
This file is used to define the URL patterns for the OAS plugin.
"""

from django.urls import re_path
from plugins.oas import views

urlpatterns = [
    re_path(r"^manager/$", views.manager, name="oas_manager"),
    re_path(r"^logs/$", views.list_articles, name="oas_logs"),
    re_path(r"^send/$", views.send_article, name="oas_send"),
]
