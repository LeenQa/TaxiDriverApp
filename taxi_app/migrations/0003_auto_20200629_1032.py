# Generated by Django 3.0.7 on 2020-06-29 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxi_app', '0002_auto_20200629_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workhours',
            name='hours',
            field=models.DurationField(null=True),
        ),
    ]
