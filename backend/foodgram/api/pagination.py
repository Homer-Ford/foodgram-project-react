from rest_framework import pagination


class RecipesResultsSetPagination(pagination.PageNumberPagination):
    """Пагинатор для списка рецептов."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
