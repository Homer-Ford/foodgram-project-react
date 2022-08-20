from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipes


class RecipesFilter(FilterSet):
    """Фильтрация произведений."""

    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='icontains'
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='icontains'
    )
    class Meta:
        model = Recipes
        fields = ['tags', 'author']

    def get_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favourit__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shop__user=self.request.user)
        return queryset