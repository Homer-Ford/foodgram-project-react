from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import FavoriteViewSet
from .views import (TagsViewSet, RecipesViewSet, IngredientsViewSet,
                    ShoppingViewSet)


router = DefaultRouter()

router.register(
    'tags',
    TagsViewSet,
    basename='tags'
)
router.register(
    r'recipes/(?P<recipes_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'recipes/(?P<recipes_id>\d+)/shopping_cart',
    ShoppingViewSet,
    basename='shopping_cart'
)
router.register(
    'recipes',
    RecipesViewSet,
    basename='recipes'
)
router.register(
    'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
