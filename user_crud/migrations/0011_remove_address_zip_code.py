# Generated by Django 2.2.5 on 2020-04-24 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_crud', '0010_auto_20200416_2002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='zip_code',
        ),
    ]