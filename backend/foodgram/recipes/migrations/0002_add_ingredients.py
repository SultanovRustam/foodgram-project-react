import json
import os.path

from django.db import migrations
from foodgram.settings import BASE_DIR

json_name = 'ingredients.json'
location_json = os.path.abspath(os.path.join(BASE_DIR,
                                             os.path.pardir,
                                             os.path.pardir,
                                             'data', json_name))

with open(location_json, encoding='utf-8') as json_file:
    json_data = json.load(json_file)


def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipe', 'Ingredient')
    for ingredient in json_data:
        new_ingredient = Ingredient(**ingredient)
        new_ingredient.save()


class Migration(migrations.Migration):
    dependencies = [
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
        ),
    ]
