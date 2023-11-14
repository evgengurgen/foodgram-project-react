# Generated by Django 4.2.7 on 2023-11-09 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_remove_recipe_ingredients_remove_recipe_is_favorited_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Ингредиенты рецепта', through='recipes.RecipeIngredient', to='recipes.ingredient', verbose_name='Ингредиенты'),
        ),
    ]