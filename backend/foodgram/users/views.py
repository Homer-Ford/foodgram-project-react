from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import Follow
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (CustomUserSerializer, FollowSerializer,
                          UserSignInSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        return UserSignInSerializer

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path='me',
            url_name='me'
            )
    def me(self, request):
        user_me = self.request.user
        serializer = self.get_serializer(user_me)
        return Response(serializer.data)

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюсет для списка подписок."""

    def get_queryset(self):
        user = self.request.user
        following = user.follower.all()
        return following

    serializer_class = FollowSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)

    @action(detail=False, permission_classes=(IsAuthenticated,),
            url_path='subscribe', methods=['delete', 'post'])
    def subscribe(self, request, **kwargs):
        if request.method == 'DELETE':
            following = self.kwargs.get('users_id')
            user = self.request.user
            follow = get_object_or_404(Follow, user=user, following=following)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        following_id = self.kwargs.get('users_id')
        following = get_object_or_404(User, pk=following_id)
        user = request.user
        serializer = FollowSerializer(
            data={'user': user, 'following': following.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
