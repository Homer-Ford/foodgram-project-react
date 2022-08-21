from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import User
from users.serializers import CustomUserSerializer
from recipes.models import (Recipes, Ingredients, Tags, RecipesIngredients,
                            ShoppingCart, Favourites)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о тегах."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об ингредиентах."""

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
            amount = RecipesIngredients.objects.get(ingredients=ingredient,
                                                    recipes=recipes).amount
            ingredient.amount = amount
        return ingredients

    def get_id(self, obj):
        return obj.ingredients.id

    def get_name(self, obj):
        return obj.ingredients.name

    def get_measurement_unit(self, obj):
        return obj.ingredients.measurement_unit


class RecipesIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для записи количества ингридиента."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = RecipesIngredients


class AllIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка ингредиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipesMiniSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о рецепте."""

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipes


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор для полного просмотра рецептов."""

    tags = TagsSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
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
        queryset = Favourites.objects.filter(recipes=obj, user=user).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        queryset = ShoppingCart.objects.filter(recipes=obj, user=user).exists()
        return queryset


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи и изменения рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipesIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True)
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
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
        serializer = RecipesReadSerializer(instance)
        return serializer.data


class ShopSerializer(serializers.ModelSerializer):
    """Сериализатор для дбавления в список покупок."""

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


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для скачивания спика покупок."""

    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipes.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False)

    class Meta:
        fields = ('recipes', 'user')
        model = ShoppingCart

    def to_representation(self, instance):
        recipes = instance.recipes
        ingredients = RecipesIngredients.objects.filter(recipes=recipes)
        serializer = IngredientsSerializer(ingredients, many=True)
        return serializer.data
