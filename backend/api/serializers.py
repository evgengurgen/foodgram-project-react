from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import Recipe, Tag, Ingredient
from users.models import Subscription

User = get_user_model()


class UserGetSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'username', 'first_name',
                  'last_name')

    def to_representation(self, instance):
        return UserGetSerializer(instance).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
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
        slug_field='name'
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients)
        return recipe

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data
