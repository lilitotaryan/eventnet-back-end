# Generated by Django 2.2.5 on 2020-05-29 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_crud', '0007_auto_20200420_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]