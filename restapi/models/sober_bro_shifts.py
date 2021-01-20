from django.db import models


class SoberBroShift(models.Model):

    date = models.DateField(verbose_name="Date of shift start", blank=False)
    title = models.CharField(
        max_length=100,
        verbose_name='Exigence of shift.',
        blank=True,
        default='Sober Bro Shift'
    )

    time_start = models.DateTimeField(verbose_name="Shift start", blank=False)
    time_end = models.DateTimeField(verbose_name="Shift end", blank=False)

    capacity = models.IntegerField(
        verbose_name="The number of brothers who are able to sign up for this slot.",
        blank=False,
        null=False,
        default=5
    )

    def __str__(self):
        return "(" + self.title + \
                ") starting on " + \
                str(self.date)
