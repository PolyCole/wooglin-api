from django.contrib.auth.models import User
from django.db import models


class Member(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        verbose_name="The User account associated with this Member."
    )

    name = models.CharField(
        max_length=127,
        db_index=True,
        verbose_name="The colloquial name of this member."
    )

    first_name = models.CharField(
        max_length=127,
        verbose_name="The member's first name"
    )

    last_name = models.CharField(
        max_length=127,
        verbose_name="The member's last name"
    )

    legal_name = models.CharField(
        max_length=127,
        verbose_name="The member's legal name"
    )

    address = models.CharField(
        max_length=511,
        verbose_name="The member's home address"
    )

    email = models.CharField(
        max_length=127,
        verbose_name="The member's primary email address. @du.edu emails are okay, but not preferred"
    )

    phone = models.CharField(
        max_length=15,
        db_index=True,
        verbose_name="The member's cell phone number. It's critical that this is correct."
    )

    rollnumber = models.IntegerField(
        verbose_name="The member's number in the roll book"
    )

    member_score = models.FloatField(
        verbose_name="The automatic value calculated by the system to assess member involvement"
    )

    inactive_flag = models.BooleanField(
        verbose_name="Whether they're inactive"
    )

    abroad_flag = models.BooleanField(
        verbose_name="Whether they're abroad"
    )

    temp_password = models.BooleanField(
        default=True,
        verbose_name="Whether their password is a temp, prompting a reset at first login."
    )

    present = models.IntegerField(
        verbose_name="How many times they've been present at chapter."
    )

    position = models.CharField(
        max_length=255,
        verbose_name="Their position within the chapter. If they don't have one, just use 'Brother'."
    )
    # avatar = models.ImageField(upload_to='staticfiles/UserMedia/', default='/staticfiles/images/default.jpg')

    def __str__(self):
        return self.name
