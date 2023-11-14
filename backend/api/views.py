from django.contrib.auth import get_user_model
import io
from django.db.models import Sum, Exists, OuterRef, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated, IsAdminUser)
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, Tag,
                            ShoppingCart, Favorite, RecipeIngredient)
from users.models import Subscription

from .paginatiors import ResponsePaginator
from .permissions import (IsAuthor, IsCurrentUser,
                          IsCurrentUserOrAdmin, IsBlockedUser)
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipeSerializer, SubscriptionsGetSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserGetSerializer, UserSerializer,
                          SetPasswordSerializer)

User = get_user_model()

USER_ONLY_METHODS = ('create', 'update', 'partial_update', 'destroy')


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (AllowAny(),)
        return (IsAdminUser(),)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (AllowAny(),)
        return (IsAdminUser(),)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'name', 'tags')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.annotate(
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
            permission_classes=(IsCurrentUser, IsBlockedUser))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            favorite = Favorite(user=request.user, recipe=recipe)
            favorite.save()
            return Response(status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(Favorite, user=request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsCurrentUser, IsBlockedUser))
    def favorites(self, request, **kwargs):
        favorites = Favorite.objects.filter(user=request.user)
        recipe_ids = [favorite.recipe.id for favorite in favorites]
        if recipe_ids:
            recipes = Recipe.objects.filter(id__in=recipe_ids)
        else:
            recipes = Recipe.objects.none()
        return Response(RecipeGetSerializer(recipes, many=True,
                                            context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated, IsBlockedUser))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            shopping_cart = ShoppingCart(user=request.user, recipe=recipe)
            shopping_cart.save()
            return Response(status=status.HTTP_201_CREATED)
        shopping_cart = get_object_or_404(ShoppingCart, user=request.user,
                                          recipe=recipe)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsCurrentUser, IsBlockedUser))
    def download_shopping_cart(self, request):
        carts = ShoppingCart.objects.filter(user=request.user)
        content = ""
        total_ingredients = {}
        for cart in carts if carts else []:
            ingredients = cart.recipe.ingredients.values(
                'id', 'name', 'measurement_unit'
            )
            for ingredient in ingredients:
                name = ingredient['name']
                amount = RecipeIngredient.objects.filter(
                    recipe=cart.recipe, ingredient=ingredient['id']
                ).aggregate(Sum('amount'))['amount__sum']
                measurement_unit = ingredient['measurement_unit']
                if name not in total_ingredients:
                    total_ingredients[name] = (amount, measurement_unit)
                else:
                    total_amount, measurement_unit = total_ingredients[name]
                    total_amount += amount
                    total_ingredients[name] = (total_amount, measurement_unit)

        for name, (amount, measurement_unit) in total_ingredients.items():
            content += f'{name}: {amount} {measurement_unit}\n'

        file_path = f'media/recipes/{request.user.email}_shopping_cart.txt'
        with io.open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='text/plain')
            response['Content-Disposition'] = ('attachment; '
                                               'filename="shopping_cart.txt"')

        return response

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in USER_ONLY_METHODS:
            return (IsAuthor(),)
        return super().get_permissions()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username', 'email')

    def get_permissions(self):
        if (self.request.method in SAFE_METHODS
           and self.request.method == 'POST'):
            return (AllowAny(),)
        return (IsCurrentUserOrAdmin(), IsBlockedUser())

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
            permission_classes=(IsAuthenticated, IsBlockedUser))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST' and author != request.user:
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

        return Response(
            {'detail': 'Нельзя подписаться на самого себя'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'],
            permission_classes=(IsCurrentUserOrAdmin, IsBlockedUser),
            pagination_class=ResponsePaginator)
    def subscriptions(self, request):
        subscribers = User.objects.filter(
            following__user=request.user).all()
        page = self.paginate_queryset(subscribers)
        serializer = SubscriptionsGetSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated, IsBlockedUser))
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
