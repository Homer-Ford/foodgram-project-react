# Generated by Django 4.1 on 2022-08-21 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipes_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favourites',
            options={'verbose_name_plural': 'Favourites'},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name_plural': 'Follow'},
        ),
        migrations.AlterModelOptions(
            name='recipesingredients',
            options={'verbose_name_plural': 'RecipesIngredients'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name_plural': 'ShoppingCart'},
        ),
        migrations.AlterField(
            model_name='recipes',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите картинку рецепта', null=True, upload_to='recipes/', verbose_name='Картинка'),
        ),
    ]
