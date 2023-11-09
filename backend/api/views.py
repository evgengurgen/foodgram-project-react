from django.contrib.auth import get_user_model
from django.db.models import Sum, Exists, OuterRef, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, Tag,
                            ShoppingCart, Favorite, RecipeIngredient)
from users.models import Subscription

from .paginatiors import ResponsePaginator
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipeSerializer, SubscriptionsGetSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserGetSerializer, UserSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = ResponsePaginator
    lookup_field = 'id'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                ingredients=Exists(RecipeIngredient.objects.filter(
                    recipe=OuterRef('id'))),
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user,
                        recipe=OuterRef('id'))),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user,
                        recipe=OuterRef('id')))
            ).select_related('author')
        return Recipe.objects.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False))

    def create(self, request, *args, **kwargs):
        serializer = RecipeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        if request.method == 'POST':
            favorite = Favorite(user=request.user, recipe=recipe)
            favorite.save()
            return Response(status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(Favorite, user=request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        if request.method == 'POST':
            shopping_cart = ShoppingCart(user=request.user, recipe=recipe)
            shopping_cart.save()
            return Response(status=status.HTTP_201_CREATED)
        shopping_cart = get_object_or_404(ShoppingCart, user=request.user,
                                          recipe=recipe)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'name',
            'measurement_unit'
        ).annotate(amount=Sum('recipe__shopping_cart__amount'))

        content = ""
        for ingredient in ingredients:
            name = ingredient['name']
            amount = ingredient['amount']
            measurement_unit = ingredient['measurement_unit']
            content += f"{name}: {amount} {measurement_unit}/n"

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')

        return response

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = ResponsePaginator
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return UserGetSerializer
        return UserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def me(self, request):
        return Response(UserGetSerializer(request.user).data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])

        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=request.user,
                              author=author).delete()
            return Response(
                {'detail': 'Вы отписались от автора: ' + author.email},
                status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=ResponsePaginator)
    def subscriptions(self, request):
        subscribers = User.objects.filter(
            following__user=request.user).all()
        page = self.paginate_queryset(subscribers)
        serializer = SubscriptionsGetSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.set_password(serializer.data["new_password"])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
