import django_filters
from django_filters.widgets import BooleanWidget
from recipe.models import Recipe
from rest_framework.filters import SearchFilter


class CustomFilter(django_filters.FilterSet):
    author = django_filters.AllValuesMultipleFilter(field_name='author__id')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited',
        widget=BooleanWidget()
    )
    in_shopping_cart = django_filters.BooleanFilter(
        field_name='in_shopping_cart',
        widget=BooleanWidget()
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'in_shopping_cart']


class CustomSearchFilter(SearchFilter):
    search_param = 'name'
