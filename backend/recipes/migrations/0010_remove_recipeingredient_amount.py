# Generated by Django 4.2.7 on 2023-11-09 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_recipe_ingredients'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipeingredient',
            name='amount',
        ),
    ]
