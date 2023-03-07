# Generated by Django 3.2.4 on 2021-09-13 13:07

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_UserUUID'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField('Gender', blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=12),
        ),
    ]
