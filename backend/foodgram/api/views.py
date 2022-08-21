import os

from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Recipes, Ingredients, Tags, RecipesIngredients,
                            ShoppingCart)
from .permissions import AdminAuthorPermission, IsAdminUserOrReadOnly
from .serializers import (TagsSerializer, RecipesReadSerializer,
                          RecipesWriteSerializer, AllIngredientsSerializer,
                          ShopSerializer, ShoppingCartSerializer)
from .filters import RecipesFilter, CustomSearchFilter
from .pagination import RecipesResultsSetPagination


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для Тегов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов и скачивании списка покупок."""

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipesWriteSerializer
        return RecipesReadSerializer

    queryset = Recipes.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = RecipesResultsSetPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter

    @action(methods=['patch', 'delete'], detail=False,
            permission_classes=(AdminAuthorPermission,))
    def delete(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipes_id')
        recipe = get_object_or_404(Recipes, pk=recipe_id)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self):
        recipe_id = self.kwargs.get('recipes_id')
        recipe = get_object_or_404(Recipes, pk=recipe_id)
        serializer = RecipesWriteSerializer(recipe)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=(IsAuthenticated,),
            url_path='download_shopping_cart')
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
                f.write(f'{ingredient} - {cart[i]} \n')
        return FileResponse(open(os.path.join(settings.BASE_DIR,
                                              'data', 'shop.txt'), 'rb'),
                            content_type='application/txt')


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для игредиентов."""

    queryset = Ingredients.objects.all()
    serializer_class = AllIngredientsSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class ShoppingViewSet(viewsets.ModelViewSet):
    """Вьюсет для добавлении или удалении из списка покупок."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        recipes_id = self.kwargs.get('recipes_id')
        recipes = get_object_or_404(Recipes, pk=recipes_id)
        author = self.request.user
        if ShoppingCart.objects.filter(user=author, recipes=recipes).exists():
            raise serializers.ValidationError('Вы уже добавили в корзину.')
        serializer.save(user=author, recipes=recipes)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipes_id')
        recipe = get_object_or_404(Recipes, pk=recipe_id)
        author = request.user
        favorite = get_object_or_404(ShoppingCart, user=author, recipes=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
