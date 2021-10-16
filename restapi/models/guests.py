from restapi.models.members import Member
from django.db import models


class Guest(models.Model):
    phone = models.CharField(
        max_length=15,
        db_index=True,
        verbose_name="The phone number associated with this guest.",
        blank=False,
        null=False
    )

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name="The name associated with this phone number."
    )

    member = models.OneToOneField(
        Member,
        null=True,
        verbose_name="The member account associated with this phone number, if there is one.",
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return str(self.name)
