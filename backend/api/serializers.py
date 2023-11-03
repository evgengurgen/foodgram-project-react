from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import Recipe, Tag, Ingredient

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True
        )
    ingredients = IngredientSerializer(
        many=True
        )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    tags = SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='slug'
        )
    ingredients = SlugRelatedField(
        many=True,
        queryset=Ingredient.objects.all(),
        slug_field='slug'
        )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
