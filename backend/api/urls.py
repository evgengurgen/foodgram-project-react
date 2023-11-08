from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UsersViewSet

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
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
