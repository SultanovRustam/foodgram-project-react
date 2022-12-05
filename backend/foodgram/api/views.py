from djoser.views import UserViewSet
from rest_framework import viewsets

from recipe.models import (FavoriteRecipe, Ingredient, Recipe,
                           ShoppingCart, Tag)
from users.models import Follow, User
from .serializers import (FollowSerializer, IngredientSerializer, TagSerializer,
                          RecipeSerializer, RecipeShortSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ('^name',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class CustomUserViewSet(UserViewSet):
   pass