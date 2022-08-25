from django.contrib import admin

from .models import (
    Recipe, Ingredient, Tag, RecipeIngredient,
    Favorite, Follow, ShoppingCart,
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    def favorite_count(self, obj):
        return obj.favorite.count()

    favorite_count.short_description = 'Добавлено в избранное'

    list_display = ('name', 'author')
    readonly_fields = ('favorite_count',)
    list_filter = ('author', 'name', 'tags',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
