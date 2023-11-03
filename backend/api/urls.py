from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

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
'''router.register(
    r'auth/signup',
    UsersViewSet,
    basename='signup'
)
router.register(
    r'users',
    UsersViewSet,
    basename='users'
)'''

urlpatterns = [
    # path('v1/users/me/', CurrentUserView.as_view()),
    # path('v1/auth/token/', TokenView.as_view()),
    path('v1/', include(router.urls)),
]
