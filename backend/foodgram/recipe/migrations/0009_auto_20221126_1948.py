# Generated by Django 2.2.16 on 2022-11-26 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0008_auto_20221126_1933'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit',
            new_name='measurement_unit',
        ),
    ]