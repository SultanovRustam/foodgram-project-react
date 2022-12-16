from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientWithAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientsInRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInRecipeInline,)
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
    )
    search_fields = (
        'name',
        'author__username',
        'author__email'
    )
    list_filter = ('name', 'author', 'tags')

    def is_favorited(self, instance):
        return instance.favorite_recipes.count()


class IngredientWithAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient', 'amount')


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientWithAmount, IngredientWithAmountAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
