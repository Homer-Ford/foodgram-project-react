from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowViewSet, CustomUserViewSet


router = DefaultRouter()

router.register(
    r'users/(?P<users_id>\d+)',
    FollowViewSet,
    basename='subscribe'
)
router.register(
    'users/subscriptions',
    FollowViewSet,
    basename='subscriptions'
)
router.register(
    'users',
    CustomUserViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
