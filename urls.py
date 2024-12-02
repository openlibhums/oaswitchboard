"""
This file is used to define the URL patterns for the OAS plugin.
"""

from django.urls import re_path
from plugins.oas import views

urlpatterns = [
    re_path(r"^manager/$", views.manager, name="oas_manager"),
]
