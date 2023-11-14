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
        'id',
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
    )
    search_fields = ('name',)
    list_filter = ('author', 'name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
