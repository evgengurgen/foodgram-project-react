from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from foodgram_backend.constants import (MAX_TAGS_LENGTH, MAX_RECIPES_LENGTH,
                                        MAX_INGREDIENTS_LENGTH,
                                        MAX_COLOR_LENGTH, MAX_MEASURE_LENGTH)

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    name = models.CharField(
        max_length=MAX_RECIPES_LENGTH,
        verbose_name='Название',
        help_text='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
        help_text='Картинка рецепта'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги',
        help_text='Теги рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах',
        default=1,
        validators=[
            MinValueValidator(
                1, message='Время приготовления должно быть больше нуля'
            )
        ]
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAGS_LENGTH,
        verbose_name='Название',
        help_text='Название тега',
        unique=True
    )
    color = models.CharField(
        max_length=MAX_COLOR_LENGTH,
        verbose_name='Цвет',
        help_text='Цвет в HEX',
        default='#FFFFFF',
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Некорректный формат HEX-кода цвета',
                code='invalid_hex_color'
            )
        ]
    )
    slug = models.SlugField(
        max_length=MAX_TAGS_LENGTH,
        verbose_name='Слаг',
        help_text='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENTS_LENGTH,
        verbose_name='Название',
        help_text='Название ингредиента',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASURE_LENGTH,
        verbose_name='Единица измерения',
        help_text='Единица измерения ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
        help_text='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Колличество',
        help_text='Колличество ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (f'{self.ingredient}: {self.amount} {self.recipe}')


# Не сделал через общий класс, потому что при создании миграций
# были ошибки related_name
class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Добавил в избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Добавил в корзину'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
