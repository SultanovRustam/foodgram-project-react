from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента для первичного заполнения"""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class IngredientWithAmount(models.Model):
    """Модель ингредиента для указания количества в рецепте"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient'
    )

    amount = models.PositiveSmallIntegerField

    class Meta:
        verbose_name = 'Количество ингредиента'
        ordering = ['-id']

    def __str__(self):
        return (f'{self.ingredient.name} : {self.amount}'
                f'{self.ingredient.unit}')


class Tag(models.Model):
    """Модель тэга"""

    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
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
    """Модель рецепта"""

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='recipes',
        verbose_name='Автор',
        null=True,
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )

    image = models.ImageField(
        upload_to='recipe/images',
        verbose_name='Картинка',
        help_text='Добавьте изображение'
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
    )
    ingredients = models.ManyToManyField(
        IngredientWithAmount,
        related_name='recipes',
        verbose_name='Используемые ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name
