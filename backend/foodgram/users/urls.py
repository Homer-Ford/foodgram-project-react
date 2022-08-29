from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, FollowViewSet

router = DefaultRouter()


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
router.register(
    r'users/(?P<users_id>\d+)',
    FollowViewSet,
    basename='subscribe'
)
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
