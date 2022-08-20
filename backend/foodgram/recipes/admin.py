from django.contrib import admin

from .models import Recipes, Ingredients, Tags, RecipesIngredients, Favourites, Follow, ShoppingCart

@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_filter = ("author", "name", "tags",)

@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_filter = ("name",)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    pass

@admin.register(RecipesIngredients)
class RecipesIngredientsAdmin(admin.ModelAdmin):
    pass


@admin.register(Favourites)
class FavoritesAdmin(admin.ModelAdmin):
    pass

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
