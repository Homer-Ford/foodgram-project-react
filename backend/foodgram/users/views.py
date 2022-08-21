from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from recipes.models import Favourites, Follow, Recipes
from users.models import User
from .serializers import (CustomUserSerializer, UserSignSerializer,
                          FavoriteSerializer, FollowSerializer, SubSerializer)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        else:
            return UserSignSerializer

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


class UserFollowViewSet(viewsets.ViewSet):
    """Управление подписками."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, pk=author_id)
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет для списка Избранных."""

    queryset = Favourites.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        recipes_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipes, pk=recipes_id)
        author = self.request.user
        if Favourites.objects.filter(user=author, recipes=recipes).exists():
            raise serializers.ValidationError("Вы уже добавили в избранное.")
        serializer.save(user=author, recipes=recipes)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        recipes_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipes, pk=recipes_id)
        author = self.request.user
        favorite = get_object_or_404(Favourites, user=author, recipes=recipes)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюсет для списка подписок."""

    serializer_class = FollowSerializer
    queryset = Follow.objects.all()

    def perform_create(self, serializer):
        author_id = self.kwargs.get('users_id')
        author = get_object_or_404(User, pk=author_id)
        user = self.request.user
        if Follow.objects.filter(following=author, user=user).exists():
            raise serializers.ValidationError('Вы уже подписались.')
        serializer.save(following=author, user=user)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        author_id = self.kwargs.get('users_id')
        author = get_object_or_404(User, pk=author_id)
        user = self.request.user
        follow = get_object_or_404(Follow, following=author, user=user)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей."""

    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    serializer_class = SubSerializer

    def get_queryset(self):
        user = self.request.user
        following = user.follower.all()
        return following
