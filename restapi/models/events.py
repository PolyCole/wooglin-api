from django.db import models


class Event(models.Model):

    time_start = models.DateTimeField(
        verbose_name="Event start time. Date in YYYY-MM-DD, time in 24-hour format",
        blank=False
    )

    time_end = models.DateTimeField(
        verbose_name="Event end time. Date in YYYY-MM-DD, time in 24-hour format",
        blank=False
    )

    guest_count = models.IntegerField(
        verbose_name="Automatically generated field that counts the number of guests at the event",
        default=0
    )

    location = models.CharField(
        verbose_name="The location of the event",
        max_length=255,
        null=False,
        blank=False
    )

    comments = models.TextField(
        verbose_name="Any comments about the event. Notes are appreciated",
        null=False,
        blank=False
    )

    event_name = models.CharField(
        verbose_name="The unique name of the event",
        max_length=255,
        null=False,
        blank=False,
        unique=True
    )

    def __str__(self):
        return str(self.event_name)


