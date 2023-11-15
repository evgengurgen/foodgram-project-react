from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__slug',
                              lookup_expr='iexact')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'name', 'tags',
                  'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(is_favorited=True)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(is_in_shopping_cart=True)
        return queryset
