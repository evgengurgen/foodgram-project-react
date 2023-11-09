from django.contrib.auth import get_user_model
from django.db import transaction
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import (Ingredient, Recipe, Tag,
                            RecipeIngredient, Favorite, ShoppingCart)
from users.models import Subscription

User = get_user_model()


class UserGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscription.objects.filter(
                user=self.context['request'].user,
                author=obj).exists()
        return False


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id',  'password', 'username', 'first_name',
                  'last_name')

    def to_representation(self, instance):
        return UserGetSerializer(instance).data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class SubscriptionsGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        serializer = SubscribersRecipeSerializer(recipes, many=True,
                                                 read_only=True)
        return serializer.data


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_email(self, obj):
        return obj.email

    def get_username(self, obj):
        return obj.username

    def get_is_subscribed(self, obj):
        return (
            Subscription.objects.filter(user=self.context['request'].user,
                                        author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = IngredientSerializer(
        read_only=True,
        source='ingredient')
    name = IngredientSerializer(
        read_only=True,
        source='ingredient')
    measurement_unit = IngredientSerializer(
        read_only=True,
        source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True
        )
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipeingredient'
        )
    author = UserGetSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Favorite.objects.filter(
                user=self.context['request'].user,
                recipe=obj
                ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj
                ).exists()
        return False

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
    ingredients = RecipeIngredientCreateSerializer(many=True)
    amount = RecipeIngredientCreateSerializer(
        many=True,
        source='recipeingredient'
        )
    image = Base64ImageField()

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in self.initial_data.get('ingredients'):
            RecipeIngredient.objects.create(recipe=recipe,
                                            **ingredient)
        recipe.tags.set(tags)
        return recipe

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'amount')


class SubscribersRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
