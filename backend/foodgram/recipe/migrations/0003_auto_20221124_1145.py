# Generated by Django 2.2.16 on 2022-11-24 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_auto_20221124_1129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientwithamount',
            options={'ordering': ['-id'], 'verbose_name': 'Количество ингредиента', 'verbose_name_plural': 'Количество ингредиентов'},
        ),
    ]