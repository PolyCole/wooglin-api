# Generated by Django 3.1.4 on 2021-01-20 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0009_auto_20210120_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='soberbroshift',
            name='title',
            field=models.CharField(blank=True, default='Sober Bro Shift', max_length=100, verbose_name='Exigence of shift.'),
        ),
    ]