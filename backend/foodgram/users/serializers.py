from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from djoser.serializers import UserSerializer, UserCreateSerializer

import api.serializers as api
from .models import User
from recipes.models import (
    Recipe, Ingredient, Tag, RecipeIngredient,
    Favorite, Follow, ShoppingCart,
)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        queryset = Follow.objects.filter(following=obj, user=user).exists()
        return queryset


class UserSignInSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                'Имя пользователя не может быть <me>.'
            )
        return value


class SubUserSerializer(UserSerializer):
    """Сериализатор для получения информации о подписанных пользователях."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.id)
        serializer = api.RecipeMiniSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        queryset = Recipe.objects.filter(author=obj.id).count()
        return queryset


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""

    user = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        required=False
    )
    following = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )

    def validate(self, data):
        user = data.get('user')
        following = data.get('following')
        if user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError('Вы уже подписаны.')
        return data

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def to_representation(self, instance):
        serializer = SubUserSerializer(instance.following)
        return serializer.data
