import os
import random
import string

import django_filters
from django.conf import settings
from django.core import mail
from django.db.models import Avg
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, serializers, status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination, \
    LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, \
    IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from recipes.models import Recipes, Ingredients, Tags, RecipesIngredients, Favourites, ShoppingCart, Follow
from users.models import User
from djoser.views import UserViewSet
from rest_framework import mixins
from .permissions import (AdminAuthorPermission, AdminOnly,
                          IsAdminUserOrReadOnly)
from .serializers import (UserGetTokenSerializer, TagsSerializer, CustomUserSerializer,
                          UserSignSerializer, RecipesReadSerializer, RecipesWriteSerializer, AllIngredientsSerializer,
                          FavoriteSerializer, FollowSerializer, SubsribtionsSerializer, ShopSerializer, SubSerializer, SubUserSerializer,
                          ShoppingCartSerializer)

from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipesFilter
from .mixins import CDMixinSet, ModelMixinSet


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        else:
            return UserSignSerializer

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination


    #@action(detail=False, url_path='subscriptions')
    #def subscriptions(self, request):
    #    user = request.user
    #    following = user.follower.all()
     #   serializer = SubSerializer(following, many=True)
      #  return Response(serializer.data)


class SubscriptionUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей."""

    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    serializer_class = SubSerializer

    def get_queryset(self):
        user = self.request.user
        following = user.follower.all()
        return following



class UserFollowViewSet(viewsets.ViewSet):
    "Управление подписками."
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




class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для Тегов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'
    pagination_class = None



class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipesWriteSerializer
        return RecipesReadSerializer

    queryset = Recipes.objects.all()



    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter



    @action(detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        recipe = user.shop.all()
        serializer = ShoppingCartSerializer(recipe, many=True)
        cart = dict()
        for i in serializer.data:
            if i[0]['id'] in cart:
                new = cart[i[0]['id']] + i[0]['amount']
                cart[i[0]['id']] = new
            else:
                cart[i[0]['id']] = i[0]['amount']
        with open(os.path.join(settings.BASE_DIR, 'data',
                               'shop.txt'), 'w', encoding='UTF-8') as f:
            for i in cart:
                ingredient = Ingredients.objects.get(pk=i)
                f.write(f'{ingredient} ({ingredient.measurement_unit}) - {cart[i]} \n')

        return FileResponse(open(os.path.join(settings.BASE_DIR, 'data',
                               'shop.txt'), 'rb'), content_type='application/txt')

class CustomSearchFilter(filters.SearchFilter):
    search_param = "name"

class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для Тегов."""

    queryset = Ingredients.objects.all()
    serializer_class = AllIngredientsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


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
            raise serializers.ValidationError("Вы уже оставили отзыв.")
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
            raise serializers.ValidationError("Вы уже оставили отзыв.")
        serializer.save(following=author, user=user)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        author_id = self.kwargs.get('users_id')
        author = get_object_or_404(User, pk=author_id)
        user = self.request.user
        follow = get_object_or_404(Follow, following=author, user=user)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingViewSet(viewsets.ModelViewSet):
    """Вьюсет для списка Избранных."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)


    def perform_create(self, serializer):
        recipes_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipes, pk=recipes_id)
        author = self.request.user
        if ShoppingCart.objects.filter(user=author, recipes=recipes).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв.")
        serializer.save(user=author, recipes=recipes)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        recipes_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipes, pk=recipes_id)
        author = request.user
        favorite = get_object_or_404(ShoppingCart, user=author, recipes=recipes)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


