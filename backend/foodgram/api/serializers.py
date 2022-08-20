from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from recipes.models import Recipes, Ingredients, Tags, RecipesIngredients, Favourites, Follow, ShoppingCart
from users.models import User
from rest_framework.relations import SlugRelatedField
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField



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


class RecipeUserSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователях."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return False



class SubUserSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователях."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        queryset = Recipes.objects.filter(author=obj.id)
        serializer = RecipesMiniSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        queryset = Recipes.objects.filter(author=obj.id).count()
        return queryset


class UserSignSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                'Имя пользователя не может быть <me>.'
            )
        return value


class UserGetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получение токенов пользователей."""



    class Meta:
        model = User
        fields = ('email', 'password')


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о пользователях."""


    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')

class IngredientsSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()


    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipes = self.context['recipes']
        for ingredient in ingredients:
            amount = RecipesIngredients.objects.get(ingredients=ingredient, recipes=recipes).amount
            ingredient.amount = amount
        return ingredients

    def get_id(self, obj):
        return obj.ingredients.id

    def get_name(self, obj):
        return obj.ingredients.name

    def get_measurement_unit(self, obj):
        return obj.ingredients.measurement_unit

class RecipesIngredientsSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())


    class Meta:
        fields = ('id', 'amount')
        model = RecipesIngredients


class AllIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о пользователях."""
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')






"""
class IngredientsWriteSerializer(serializers.ModelSerializer):


    amount = serializers.SerializerMethodField()
    class Meta:
        model = Ingredients
        fields = ('id',  'amount')

    def get_amount(self, obj):
        return RecipesIngredients.objects.get(ingredients=obj).amount"""

class RecipesMiniSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра произведений."""



    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipes


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра произведений."""
    tags = TagsSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipes

    def get_ingredients(self, obj):
        ingredients = RecipesIngredients.objects.filter(recipes=obj)
        serializer = IngredientsSerializer(ingredients, many=True)
        return serializer.data


    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        queryset = Favourites.objects.filter(recipes=obj,
                                         user=user).exists()
        return queryset


    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user.id
        queryset = ShoppingCart.objects.filter(recipes=obj.id,
                                             user=request_user).exists()
        return queryset


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра произведений."""

    tags = TagsSerializer(read_only=True, many=True)
    author = RecipeUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipes

    def get_ingredients(self, obj):
        ingredients = RecipesIngredients.objects.filter(recipes=obj)
        serializer = IngredientsSerializer(ingredients, many=True)
        return serializer.data


    def get_is_favorited(self, obj):
        return False


    def get_is_in_shopping_cart(self, obj):
        return False


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения произведений."""

    author = RecipeUserSerializer(read_only=True)
    ingredients = RecipesIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True)
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipes

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipes = Recipes.objects.create(**validated_data)
        recipes.tags.set(tags)
        for ingredient in ingredients:
            RecipesIngredients.objects.create(
                recipes=recipes,
                ingredients=ingredient['id'],
                amount=ingredient['amount'])

        return recipes

    def update(self, instance, validated_data):
        for i in RecipesIngredients.objects.filter(recipes=instance):
            i.delete()
        instance.tags.set(validated_data.get('tags'))
        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()

        ingredients = validated_data.get('ingredients')
        for ingredient in ingredients:

            RecipesIngredients.objects.create(
                recipes=instance,
                ingredients=ingredient['id'],
                amount=ingredient['amount'])

        return instance

    def to_representation(self, instance):
        serializer = RecipesSerializer(instance)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о пользователях."""

    recipes = serializers.PrimaryKeyRelatedField(queryset=Recipes.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Favourites
        fields = ('recipes', 'user')




class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""

    user = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        required=False
    )
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False)

    def validate(self, data):
        user = self.context.get('request').user

        following = data.get('following')
        if user == following:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя.")
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError("Вы уже подписаны.")
        return data

    class Meta:
        model = Follow
        fields = ('user', 'following')

class SubsribtionsSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователях."""

    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('following', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        queryset = Recipes.objects.filter(author=obj.following.id)
        serializer = RecipesMiniSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        queryset = Recipes.objects.filter(author=obj.following.id).count()
        return queryset


class ShopSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра произведений."""
    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipes.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False)

    class Meta:
        fields = ('recipes', 'user')
        model = ShoppingCart

    def to_representation(self, instance):
        serializer = RecipesMiniSerializer(instance.recipes)
        return serializer.data

class SubSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""




    class Meta:
        model = Follow
        fields = ('following',)

    def to_representation(self, instance):
        user = User.objects.filter(username=instance.following)
        serializer = SubUserSerializer(user, many=True)
        return serializer.data[0]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра произведений."""

    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipes.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False)

    class Meta:
        fields = ('recipes', 'user')
        model = ShoppingCart

    def to_representation(self, instance):
        ingredients = RecipesIngredients.objects.filter(recipes=instance.recipes)
        serializer = IngredientsSerializer(ingredients, many=True)
        return serializer.data