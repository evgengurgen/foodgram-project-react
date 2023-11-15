import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from progress.bar import IncrementalBar

from foodgram_backend import settings
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


def ingredient_create(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1]
    )


def tags_create(row):
    Tag.objects.get_or_create(
        name=row[0],
        color=row[1],
        slug=row[2]
    )


class Command(BaseCommand):
    help = "Load ingredients to DB"

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'ingredients.csv')
        with open(path, 'r', encoding='utf-8') as file:
            row_count = sum(1 for row in file)
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            bar = IncrementalBar('ingredients.csv'.ljust(17), max=row_count)
            next(reader)
            for row in reader:
                bar.next()
                ingredient_create(row)
            bar.finish()
        self.stdout.write("[!] Ингредиенты успешно загружены.")

        path = os.path.join(settings.BASE_DIR, 'tags.csv')
        with open(path, 'r', encoding='utf-8') as file:
            row_count = sum(1 for row in file)
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            bar = IncrementalBar('tags.csv'.ljust(17), max=row_count)
            next(reader)
            for row in reader:
                bar.next()
                tags_create(row)
            bar.finish()
        self.stdout.write("[!] Теги успешно загружены.")

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@example.com',
                password='adminpassword', first_name='admin',
                last_name='admin'
            )
        self.stdout.write("[!] Учетная запись админа успешно создана.")
        if not Recipe.objects.filter(name='Рецепт админа').exists():
            admin_recipe = Recipe.objects.create(
                author=User.objects.get(id=1),
                name='Рецепт админа',
                image='image.jpg',
                text='Описание рецепта админа',
                cooking_time=10
            )
            admin_recipe.tags.set(
                Tag.objects.all().values_list('id', flat=True))
            RecipeIngredient.objects.create(
                recipe=admin_recipe,
                ingredient=Ingredient.objects.get(id=111),
                amount=100
            )
            RecipeIngredient.objects.create(
                recipe=admin_recipe,
                ingredient=Ingredient.objects.get(id=222),
                amount=200
            )
        self.stdout.write("[!] Рецепт админа успешно создан.")

        if not User.objects.filter(username='user').exists():
            User.objects.create_user(
                username='user', email='user@example.com',
                password='userpassword', first_name='user',
                last_name='user'
            )
        self.stdout.write("[!] Учетная запись пользователя успешно создана.")
        if not Recipe.objects.filter(name='Рецепт пользователя').exists():
            user_recipe = Recipe.objects.create(
                author=User.objects.get(id=2),
                name='Рецепт пользователя',
                image='image1.jpg',
                text='Описание рецепта пользователя',
                cooking_time=10
            )
            user_recipe.tags.set([1])
            RecipeIngredient.objects.create(
                recipe=user_recipe,
                ingredient=Ingredient.objects.get(id=100),
                amount=111
            )
            RecipeIngredient.objects.create(
                recipe=user_recipe,
                ingredient=Ingredient.objects.get(id=200),
                amount=222
            )
            RecipeIngredient.objects.create(
                recipe=user_recipe,
                ingredient=Ingredient.objects.get(id=300),
                amount=333
            )
        self.stdout.write("[!] Рецепт пользователя успешно создан.")
