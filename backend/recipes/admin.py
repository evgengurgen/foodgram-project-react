from django.contrib import admin

from .models import (Ingredient, Recipe, Tag, RecipeIngredient,
                     Favorite, ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 1


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, FavoriteInline, ShoppingCartInline)
    list_display = (
        'name',
        'author'
    )
    list_filter = ('author', 'name')
    readonly_fields = ['total_favorites']

    def total_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    total_favorites.short_description = 'В избранном у'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_filter = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
