from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Recipe, Ingredient, Tag, RecipeIngredient, ShoppingCart,
    Favorite,
)
from users.serializers import CustomUserSerializer
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о тегах."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об ингредиентах."""

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipes = self.context['recipes']
        for ingredient in ingredients:
            amount = RecipeIngredient.objects.get_object_or_404(
                ingredients=ingredient,
                recipes=recipes).amount
            ingredient.amount = amount
        return ingredients

    def get_id(self, obj):
        return obj.ingredients.id

    def get_name(self, obj):
        return obj.ingredients.name

    def get_measurement_unit(self, obj):
        return obj.ingredients.measurement_unit


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для записи количества ингридиента."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class AllIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о рецепте."""

    image = serializers.ImageField(use_url=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для полного просмотра рецептов."""

    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=False)

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipes=obj)
        serializer = IngredientSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        queryset = Favorite.objects.filter(recipes=obj, user=user).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        queryset = ShoppingCart.objects.filter(recipes=obj, user=user).exists()
        return queryset


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи и изменения рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    image = Base64ImageField(use_url=False)

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipes = Recipe.objects.create(**validated_data)
        recipes.tags.set(tags)
        recipeingredient_new = [RecipeIngredient(
            recipes=recipes,
            ingredients=ingredient['id'],
            amount=ingredient['amount'])
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(objs=recipeingredient_new)
        return recipes

    def update(self, instance, validated_data):
        RecipeIngredient.objects.get(recipes=instance).delete()
        instance.tags.set(validated_data.get('tags'))
        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        ingredients = validated_data.get('ingredients')
        recipeingredient_new = [RecipeIngredient(
            recipes=instance,
            ingredients=ingredient['id'],
            amount=ingredient['amount'])
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(objs=recipeingredient_new)
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data


class ShopSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в список покупок."""

    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )

    def validate(self, data):
        user = data.get('user')
        recipes = data.get('recipes')
        if ShoppingCart.objects.filter(user=user, recipes=recipes).exists():
            raise serializers.ValidationError('Вы уже добавили в корзину.')
        return data

    class Meta:
        fields = ('recipes', 'user')
        model = ShoppingCart

    def to_representation(self, instance):
        serializer = RecipeMiniSerializer(instance.recipes)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об избранных."""

    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False)

    def validate(self, data):
        user = data.get('user')
        recipes = data.get('recipes')
        if Favorite.objects.filter(user=user, recipes=recipes).exists():
            raise serializers.ValidationError("Вы уже добавили в избранное.")
        return data

    class Meta:
        model = Favorite
        fields = ('recipes', 'user')

    def to_representation(self, instance):
        serializer = RecipeMiniSerializer(instance.recipes)
        return serializer.data
