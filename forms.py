__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"

from django import forms


class OASManagerForm(forms.Form):
    enabled = forms.BooleanField(
        required=False, help_text="Whether to send p1-pio messages."
    )
    sandbox = forms.BooleanField(
        required=False, help_text="Whether to run in sandbox mode."
    )
    email = forms.CharField(help_text="The email login credential.")
    password = forms.CharField(
        help_text="The password login credential.",
    )
    url = forms.CharField(
        help_text="The URL for the live deposit.", label="URL"
    )
    sandbox_url = forms.CharField(
        help_text="The URL for the sandbox site.", label="Sandbox URL"
    )
