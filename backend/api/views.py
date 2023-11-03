from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
# from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS

from .paginatiors import ResponsePaginator
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeGetSerializer)
from recipes.models import Tag, Ingredient, Recipe

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = ResponsePaginator
    lookup_field = 'slug'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('is_favorited', 'author',
                        'is_in_shopping_cart', 'tags')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer
