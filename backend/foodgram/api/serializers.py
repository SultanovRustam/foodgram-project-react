from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Ingredient, IngredientWithAmount, Recipe,
                            RecipeTag, Tag)
from rest_framework import serializers

from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = 'name', 'color', 'slug'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = 'name', 'measurement_unit'
        model = Ingredient


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.BooleanField(read_only=True)
    in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorite',
            'in_shopping_cart', 'name', 'text', 'cooking_time', 'image'
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient__amount')
        )

    def write_ingredients_tags(self, recipe, ingredients, tags):
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get_object_or_404(
                id=ingredient.get('id')
            )
            IngredientWithAmount.objects.update_or_create(
                ingredient=current_ingredient,
                amount=ingredient.get('amount'),
                recipe=recipe
            )
        if isinstance(tags, int):
            current_tag = Tag.objects.get_object_or_404(id=tags)
            RecipeTag.objects.update_or_create(tag=current_tag, recipe=recipe)
        else:
            for tag in tags:
                current_tag = Tag.objects.get_object_or_404(id=tag)
                RecipeTag.objects.update_or_create(
                    tag=current_tag,
                    recipe=recipe
                )
        return recipe

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ingredients не может быть пустым'
            )
        try:
            for ingredient in ingredients:
                ingredient_id = ingredient.get('id')
                amount = ingredient.get('amount')
                if int(amount) < 1:
                    raise serializers.ValidationError(
                        'Минимальное количество ингредиентов 1'
                    )
                if not Ingredient.objects.filter(id=ingredient_id).exists():
                    raise serializers.ValidationError(
                        f'Ингредиента c id {ingredient_id} не существует'
                    )
        except TypeError:
            raise serializers.ValidationError(
                'Поле tags обязательно для заполнения'
            )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Поле tags не может быть пустым'
            )
        try:
            for tag in tags:
                if not Tag.objects.filter(id=tag).exists():
                    raise serializers.ValidationError(
                        f'Тега c id {tag} не существует'
                    )
        except TypeError:
            raise serializers.ValidationError(
                'Поле tags обязательно для заполнения'
            )
        return tags

    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        self.validate_ingredients(ingredients)
        recipe = Recipe.objects.create(**validated_data)
        return self.write_ingredients_tags(recipe, ingredients, tags)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        instance = self.write_ingredients_tags(instance, ingredients, tags)
        return super().update(instance, validated_data)


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.all().count()
