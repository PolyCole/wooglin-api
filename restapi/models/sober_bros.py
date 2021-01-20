from django.db import models


class SoberBro(models.Model):
    shift = models.ForeignKey(
        to='SoberBroShift',
        on_delete=models.CASCADE
    )

    member = models.ForeignKey(
        to='Member',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    def __str__(self):
        return str(self.member.name) + \
               " is signed up for a shift on " + \
               str(self.shift.date)
