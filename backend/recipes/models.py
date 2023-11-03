from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта',
        blank=False
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название рецепта',
        blank=False
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
        help_text='Картинка рецепта',
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
        blank=False
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты рецепта',
        blank=False
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги',
        help_text='Теги рецепта',
        blank=False
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах',
        default=0,
        blank=False
    )
    is_favorited = models.BooleanField(
        verbose_name='В избранном',
        help_text='Добавлен ли рецепт в избранное',
        default=False,
        blank=False
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В корзине',
        help_text='Добавлен ли рецепт в корзину',
        default=False,
        blank=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название тега',
        unique=True,
        blank=False
    )
    color = models.CharField(
        max_length=16,
        verbose_name='Цвет',
        help_text='Цвет в HEX',
        default='#FFFFFF',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Слаг',
        help_text='Уникальный слаг',
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название ингредиента',
        blank=False
    )
    amount = models.CharField(
        max_length=200,
        verbose_name='Колличество',
        help_text='Колличество ингредиента',
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Единица измерения ингредиента',
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title
