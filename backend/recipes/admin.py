from django.contrib import admin

from .models import Recipe, Tag, Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
    )
    search_fields = ('name',)
    list_filter = ('author',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
