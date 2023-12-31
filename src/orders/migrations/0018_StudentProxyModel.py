# Generated by Django 3.2.8 on 2021-10-28 17:09

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_StudentProxyModel'),
        ('orders', '0017_OrderPermissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.student', verbose_name='User'),
        ),
    ]
