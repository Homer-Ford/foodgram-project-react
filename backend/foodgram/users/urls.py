from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowViewSet, SubscriptionUserViewSet, CustomUserViewSet


router = DefaultRouter()

router.register(
    r'users/(?P<users_id>\d+)/subscribe',
    FollowViewSet,
    basename='subscribe'
)
router.register(
    r'users/subscriptions',
    SubscriptionUserViewSet,
    basename='subscriptions'
)
router.register(
    r'users',
    CustomUserViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
