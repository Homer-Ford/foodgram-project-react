from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)

from .filters import CustomSearchFilter, RecipeFilter
from .pagination import RecipeResultSetPagination
from .permissions import AdminAuthorPermission, IsAdminUserOrReadOnly
from .serializers import (AllIngredientsSerializer, FavoriteSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShopSerializer, TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для Тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов и скачивании списка покупок."""

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = RecipeResultSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(methods=['patch', 'delete'], detail=False,
            permission_classes=(AdminAuthorPermission,),)
    def delete(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipe, pk=recipe_id)
        recipes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self):
        recipe_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipe, pk=recipe_id)
        serializer = RecipeWriteSerializer(recipes)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=(IsAuthenticated,),
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        responce = HttpResponse(content_type='text/plain')
        responce['Content-Disposition'] = 'attachment; filename=shop.txt'
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipes__shop__user=user
        ).values(
            'ingredients_id__name',
            'ingredients_id__measurement_unit'
        ).annotate(Sum('amount'))
        for ingredient in ingredients:
            name = ingredient['ingredients_id__name'].capitalize()
            measurement_unit = ingredient['ingredients_id__measurement_unit']
            amount = ingredient['amount__sum']
            responce.writelines(f'{name} ({measurement_unit}) - {amount} \n')
        return responce

    @action(detail=False, permission_classes=(IsAuthenticated,),
            url_path='favorite',
            url_name='favorite',
            methods=['delete', 'post']
            )
    def favorite(self, request, **kwargs):
        if request.method == 'DELETE':
            recipes_id = self.kwargs.get('recipes_id')
            recipes = get_object_or_404(Recipe, pk=recipes_id)
            author = request.user
            favorite = get_object_or_404(
                Favorite,
                user=author,
                recipes=recipes,
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        recipes_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipe, pk=recipes_id)
        user = request.user
        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipes': recipes.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=(IsAuthenticated,),
            url_path='shopping_cart',
            url_name='shopping_cart',
            methods=['delete', 'post'])
    def shopping_cart(self, request, **kwargs):
        if request.method == 'DELETE':
            recipe_id = self.kwargs.get('recipes_id')
            recipes = get_object_or_404(Recipe, pk=recipe_id)
            author = request.user
            cart = get_object_or_404(ShoppingCart, user=author,
                                     recipes=recipes)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        recipes_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipe, pk=recipes_id)
        user = request.user
        serializer = ShopSerializer(
            data={'user': user.id, 'recipes': recipes.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для игредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = AllIngredientsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)
