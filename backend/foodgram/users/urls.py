from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserSetPassword, UserViewSet)

router = DefaultRouter()

"""router.register(
    '',
    UserViewSet
)
router.register(
    r'me',
    UserViewSet,
    basename="users_me"
)
router.register(
    r'set_password',
    UserSetPassword,
    basename="users_psw"
)
router.register(
    r'subscriptions',
    UserSetPassword,
    basename="users_subscriptions"
)"""

urlpatterns = [
    path('', include('djoser.urls')),
]