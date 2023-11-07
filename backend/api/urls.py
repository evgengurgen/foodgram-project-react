from django.urls import include, path
from rest_framework import routers
# from djoser.urls.authtoken

from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet, UsersViewSet, TokenCreateView)

router = routers.DefaultRouter()
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    r'users',
    UsersViewSet,
    basename='users'
)

urlpatterns = [
    # path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/login/', TokenCreateView.as_view()),
    path('', include(router.urls)),
]
