import io

from django.db.models import Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import MyUser as User
from users.models import Subscription
from .filters import RecipeFilter
from .paginatiors import ResponsePaginator
from .permissions import (IsAdminOrReadOnly, IsAuthor, IsBlockedUser,
                          IsCurrentUserOrAdmin, UserPermissions)
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipeSerializer, SetPasswordSerializer,
                          RecipeActionSerializer,
                          SubscriptionsGetSerializer, SubscriptionsSerializer,
                          TagSerializer, UserGetSerializer, UserSerializer)

USER_ONLY_METHODS = ('create', 'update', 'partial_update', 'destroy')


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('slug',)
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

    '''def create(self, request, *args, **kwargs):
        serializer = RecipeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)'''

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsBlockedUser,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if (request.method == 'POST' and not Favorite.objects.filter(
                user=request.user, recipe=recipe).exists()):
            if Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
                return Response({'detail': 'В избранном уже есть'},
                                status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite(user=request.user, recipe=recipe)
            favorite.save()
            serializer = RecipeActionSerializer(favorite.recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(Favorite, user=request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response({'detail': 'Рецепт удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated, IsBlockedUser))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            shopping_cart = ShoppingCart(user=request.user, recipe=recipe)
            shopping_cart.save()
            serializer = RecipeActionSerializer(shopping_cart.recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        shopping_cart = get_object_or_404(ShoppingCart, user=request.user,
                                          recipe=recipe)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsBlockedUser,))
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
            return (IsAuthor(), IsBlockedUser())
        return super().get_permissions()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (UserPermissions,)
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username', 'email')

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
            if Subscription.objects.filter(user=request.user,
                                           author=author).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionsSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif author == request.user:
            return Response(
                {'detail': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST)

        # Не понял, как использовать .mapping.delete
        get_object_or_404(Subscription, user=request.user,
                          author=author).delete()
        return Response(
            {'detail': 'Вы отписались от автора: ' + author.email},
            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsCurrentUserOrAdmin, IsBlockedUser))
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
