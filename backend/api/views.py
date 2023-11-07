from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS
import rest_framework
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated


from djoser import utils
from djoser.conf import settings

from .paginatiors import ResponsePaginator
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeGetSerializer,
                          UserGetSerializer, UserSerializer,
                          SubscriptionsSerializer)
from recipes.models import Tag, Ingredient, Recipe
from users.models import Subscription

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
    filterset_fields = ('is_favorited', 'author',
                        'is_in_shopping_cart', 'tags')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = ResponsePaginator
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return UserGetSerializer
        return UserSerializer

    def me(self, request):
        return UserGetSerializer(request.user).data

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=ResponsePaginator)
    def subscriptions(self, request):
        return UserGetSerializer(
            request.user.subscribers.all(), many=True).data

    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.set_password(serializer.data["new_password"])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

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
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """Use this endpoint to obtain user authentication token."""

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = (rest_framework.permissions.AllowAny,)

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )
