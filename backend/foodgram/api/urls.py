from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (TagsViewSet, RecipesViewSet,
                    IngredientsViewSet, FavoriteViewSet, FollowViewSet, UserFollowViewSet,
                    ShoppingViewSet, CustomUserViewSet, SubscriptionUserViewSet
                    )

router = DefaultRouter()

router.register(
    'tags',
    TagsViewSet,
    basename="tags"
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
    basename="recipes"
)
router.register(
    'ingredients',
    IngredientsViewSet,
    basename="ingredients"
)

router.register(
    r'users/(?P<users_id>\d+)/subscribe',
    FollowViewSet,
    basename='subscribe'
)
#router.register(
#    r'users',
#    CustomUserViewSet,
#    basename='users'
#)
router.register(
    r'users/subscriptions',
    SubscriptionUserViewSet,
    basename='subscriptions'
)
urlpatterns = [

    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
