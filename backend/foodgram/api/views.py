from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, IngredientWithAmount,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User
from .filters import CustomFilter, CustomSearchFilter
from .pagination import CustomPageNumberPagination
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ('^name',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)
    filter_backends = (CustomSearchFilter,)


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    @action(permission_classes=(permissions.IsAuthenticated,), detail=False)
    def subscriptions(self, request, pk=None):
        user = self.request.user
        queryset = user.follower.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        object_existence = user.follower.filter(author=author).exists()
        if request.method == 'POST':
            if object_existence or user.id == int(id):
                return Response({
                    'error': 'Вы уже подписаны или пытаетесь подписаться '
                             'на самого себя'
                },
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not object_existence:
            return Response({
                'error': 'Подписаться не удалось'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.follower.filter(author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            queryset = Recipe.objects.annotate(
                is_favorited=Exists(
                    user.author_of_favoritting.filter(
                        recipe__pk=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    user.author_of_shopping_cart.filter(
                        recipe__pk=OuterRef('pk')
                    )
                ),
            )
        else:
            queryset = Recipe.objects.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_fav_shopping_cart(
        self, request, model, post_error, delete_error, pk
    ):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        object_existence = model.objects.filter(
            user=user,
            recipe__id=pk
        ).exists()

        if request.method == 'POST':
            if object_existence:
                return Response({
                    'error': post_error
                },
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not object_existence:
            return Response({
                'error': delete_error},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        model = FavoriteRecipe
        post_error = 'Рецепт уже есть в избранном'
        delete_error = 'Рецепта нет в избранном'
        return self.add_fav_shopping_cart(
            request, model, post_error, delete_error, pk
        )

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        model = ShoppingCart
        post_error = 'Рецепт уже есть в списке покупок'
        delete_error = 'Рецепта нет в списке покупок'
        return self.add_fav_shopping_cart(
            request, model, post_error, delete_error, pk
        )

    @action(permission_classes=(permissions.IsAuthenticated,), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = 'Cписок покупок:'
        shopping_cart = IngredientWithAmount.objects.filter(
            recipe__in=Recipe.objects.filter(shopping_cart_recipes__user=user))
        shopping_cart = shopping_cart.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            amount_sum=Sum('amount'))
        for num, i in enumerate(shopping_cart):
            ingredients += (
                f"\n{i['ingredient__name']} - "
                f"{i['amount_sum']} {i['ingredient__measurement_unit']}"
            )
            if num < shopping_cart.count() - 1:
                ingredients += ', '
        file = 'shopping_list'
        response = HttpResponse(
            ingredients, 'Content-Type: application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return response
