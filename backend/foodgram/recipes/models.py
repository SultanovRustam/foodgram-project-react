from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Название тэга',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        default='#101cc4',
        verbose_name='Цветовая метка',
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )

    image = models.ImageField(
        upload_to='static/recipe',
        verbose_name='Картинка',
        help_text='Добавьте изображение'
    )
    text = models.TextField(
        verbose_name='Текстовое описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientWithAmount',
        verbose_name='Используемые ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientWithAmount(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient'
    )

    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient')]

    def __str__(self):
        return self.ingredient.name


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэги рецепта'
        verbose_name_plural = 'Тэги рецепта'
        constraints =[
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique tag'
            )
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class FavoriteRecipe(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_of_favoritting'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite_recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='uniq_favorites',
            ),
        )
        ordering = ('user',)


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_of_shopping_cart',
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='Покупка'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart',
            ),
        )
