from django.db import models
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField

from .validators import validate_no_zero
from users.models import User


class Ingredient(models.Model):
    """Модель для создания таблицы ингредиентов."""

    name = models.CharField(
        max_length=200,
        null=False,
        verbose_name='Название',
    )
    measurement_unit = models.TextField(
        null=False,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name.capitalize()} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель для создания таблицы рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(
        'Картинка',
        help_text='Загрузите картинку рецепта',
        upload_to='images/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        'Текст рецепта',
        help_text='Введите текст рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipes', 'ingredients'),
        verbose_name='Ингредиент',
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        verbose_name='Тег',
        help_text='Выберете теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=(validate_no_zero,)
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    is_favorited = models.BooleanField(default=False, verbose_name='Избранный')
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name='В корзине',
    )

    class Meta:
        verbose_name = 'Рецепт'
        ordering = ['-pub_date']
        verbose_name_plural = 'Recipe'

    def __str__(self):
        return f'{self.name}, {self.author}'


class Tag(models.Model):
    """Модель для создания таблицы тегов."""

    name = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='Название',
    )
    color = ColorField(format='hex', unique=True, verbose_name='Цветовой код')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Tag'
        constraints = [
            models.UniqueConstraint(fields=['name', 'color', 'slug'],
                                    name='teg_unique')]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель для создания таблицы связи рецепт-ингредиенты."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        default=1,
        validators=(validate_no_zero,),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'RecipeIngredient'
        constraints = [
            models.UniqueConstraint(fields=['recipes', 'ingredients'],
                                    name='recipe_ingredient_unique')]


class Favorite(models.Model):
    """Модель для создания таблицы избранных."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )

    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Favorite'
        constraints = [models.UniqueConstraint(
            fields=['recipes', 'user'],
            name='favorite_unique')
        ]


class ShoppingCart(models.Model):
    """Модель для создания таблицы покупок."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shop'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shop'
    )

    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Продуктовая корзина'
        verbose_name_plural = 'ShoppingCart'
        constraints = [models.UniqueConstraint(
            fields=['recipes', 'user'],
            name='shopping_unique')
        ]


class Follow(models.Model):
    """Модель для создания таблицы подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Follow'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='follow_unique')]
