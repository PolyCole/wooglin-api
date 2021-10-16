from restapi.models.events import Event
from restapi.models.guests import Guest
from django.db import models


class EventAttendance(models.Model):
    # Basically, if the event or the guest associated here gets deleted,
    # we're doing nothing.
    event = models.OneToOneField(Event, on_delete=models.DO_NOTHING)
    guest = models.OneToOneField(Guest, on_delete=models.DO_NOTHING)

    arrival_time = models.DateTimeField(
        verbose_name="When this guest checked into the event.",
        blank=False,
        null=False
    )

    help_flag = models.BooleanField(
        verbose_name="Whether this person requested help at this event.",
        null=False,
        default=False
    )

    help_flag_raised_at = models.DateTimeField(
        verbose_name="When the help flag was raised for this person.",
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.guest.name) + \
               " at " + \
               str(self.event.event_name)


