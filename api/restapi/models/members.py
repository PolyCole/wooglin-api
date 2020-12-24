from django.contrib.auth.models import User
from django.db import models


class Member(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=127, db_index=True)
    first_name = models.CharField(max_length=127)
    last_name = models.CharField(max_length=127)
    legal_name = models.CharField(max_length=127)

    address = models.CharField(max_length=511)
    email = models.CharField(max_length=127)
    phone = models.CharField(max_length=15, default="000.000.0000", db_index=True)

    rollnumber = models.IntegerField()
    member_score = models.FloatField()

    inactive_flag = models.BooleanField()
    abroad_flag = models.BooleanField()

    present = models.IntegerField()

    position = models.CharField(max_length=255)
    # avatar = models.ImageField(upload_to='static/UserMedia/', default='/static/images/default.jpg')

    def __str__(self):
        return self.name
