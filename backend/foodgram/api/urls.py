from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, RecipeViewSet, IngredientViewSet,
)


router = DefaultRouter()

router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'recipes/(?P<recipes_id>\d+)',
    RecipeViewSet,
    basename='favorite'
)
router.register(
    r'recipes/(?P<recipes_id>\d+)',
    RecipeViewSet,
    basename='shopping_cart'
)
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
