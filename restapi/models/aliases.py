from django.db import models
from restapi.models.guests import Guest


class Alias(models.Model):
    guest = models.OneToOneField(
        Guest,
        verbose_name="The guest account associated with this alias.",
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING
    )

    alias = models.CharField(
        verbose_name="The provided alias.",
        max_length=255,
        null=False,
        blank=False
    )

    def __str__(self):
        return str(self.guest.name) + "'s alias: " + str(self.alias)