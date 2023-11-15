from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
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
        if (self.context.get('request').user.is_authenticated):
            return obj.follower.filter(
                user=self.context['request'].user
                ).exists()
        return False


class UserShowCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'password', 'username', 'first_name',
                  'last_name')

    def to_representation(self, instance):
        return UserShowCreateSerializer(instance).data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError(
                'Учетные данные не были предоставлены.'
            )

        current_password = attrs.get('current_password')
        if not user.check_password(current_password):
            raise serializers.ValidationError('Неверный текущий пароль')

        new_password = attrs.get('new_password')
        user.set_password(new_password)
        user.save()

        return attrs


class SubscriptionsGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
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

    def get_is_subscribed(self, obj):
        return obj.follower.filter(
            user=self.context['request'].user
            ).exists()


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

    def get_is_subscribed(self, obj):
        return (
            Subscription.objects.filter(user=self.context['request'].user,
                                        author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        serializer = SubscribersRecipeSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = serializers.SerializerMethodField()
    author = UserGetSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        if (self.context.get('request').user.is_authenticated):
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

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        serializer = RecipeIngredientSerializer(
            recipe_ingredients, many=True,
            context={'recipe_id': obj.id})
        return serializer.data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')


class RecipeSerializer(serializers.Serializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            allow_empty=False
        ),
        allow_empty=False
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    image = Base64ImageField()
    name = serializers.CharField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_ids = []
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            ingredients_ids.append(ingredient_id)
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data.get('amount')
            )
        recipe.ingredients.set(ingredients_ids)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_ids = []
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            ingredients_ids.append(ingredient_id)
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data.get('amount')
            )
        instance.ingredients.set(ingredients_ids)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance).data


class SubscribersRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
