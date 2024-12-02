"""
Models for the OAS plugin.
"""

from django.db import models


class SwitchboardMessage(models.Model):
    """
    A message that has been sent to the switchboard.
    """

    broadcast = models.BooleanField(default=True)
    message_type = models.CharField(max_length=255, default="p1-pio")
    authorized = models.BooleanField(default=False)

    article = models.OneToOneField(
        "submission.Article",
        on_delete=models.CASCADE,
    )

    message = models.TextField()
    response = models.TextField()

    message_date_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
