from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from users.models import User


class Ingredients(models.Model):
    name = models.CharField(max_length=200, null=False)
    measurement_unit = models.TextField(null=False)

    class Meta:
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name.capitalize()

class Recipes(models.Model):
    """Модель для создания таблицы Recipes."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        'Картинка',
        help_text='Загрузите картинку рецепта',
        upload_to='recipes/image/',
        blank=True,
        null=True,
    )
    text = models.TextField('Текст рецепта', help_text='Введите текст рецепта')
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipesIngredients',
        through_fields=('recipes', 'ingredients')
    )
    tags = models.ManyToManyField(
        'Tags',
        blank=True,
        verbose_name='Тег',
        help_text='Выберете теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField()
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return f"{self.name}, {self.author}"




class Tags(models.Model):
    """Модель для создания таблицы Teg."""

    name = models.CharField(max_length=200, unique=True)
    color = ColorField(format="hex", unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Tags'
        constraints = [
            models.UniqueConstraint(fields=['name', 'color', 'slug'],
                                    name='teg_unique')]

    def __str__(self):
        return self.name

class RecipesIngredients(models.Model):

    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )

    amount = models.IntegerField(default=1)

class Favourites(models.Model):
    """Модель для создания таблицы Отзывы."""

    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favourit'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourit'
    )

    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipes', 'user'],
            name='favourite_unique')
        ]




class ShoppingCart(models.Model):
    """Модель для создания таблицы Отзывы."""

    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop'
    )

    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipes', 'user'],
            name='shopping_unique')
        ]

class Follow(models.Model):
    """Модель для создания таблицы Follow."""

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
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='follow_unique')]