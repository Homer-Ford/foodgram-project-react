from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from recipes.models import Recipes, Ingredients, Tags, Follow
from users.models import User
from djoser.serializers import UserSerializer





class CustomUserSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователях."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Follow.objects.filter(following=obj.id, user=request_user).exists()
        return queryset
