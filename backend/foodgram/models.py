from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента', max_length=200,
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=200,
        help_text='Единица измерения ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Название', help_text='Название тега'
    )
    color = models.CharField(
        max_length=7, verbose_name='Цвет', help_text='Цвет тега'
    )
    slug = models.SlugField(
        max_length=200, verbose_name='Slug', help_text='Slug тега'
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
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag, through='TagRecipe', related_name='recipes',
        verbose_name='Теги', help_text='Теги рецепта'
    )
    name = models.CharField(
        max_length=200, verbose_name='Название', help_text='Название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание', help_text='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах',
        validators=[
            MinValueValidator(settings.RECIPE_MIN_COOKING_TIME),
            MaxValueValidator(settings.RECIPE_MAX_COOKING_TIME)
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        blank=True,
        verbose_name='Ингредиенты',
        help_text='Ингредиенты рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Время публикации',
        help_text='Время публикации'
    )
    image = models.ImageField(
        verbose_name='Изображение', help_text='Изображение рецепта'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions',
        verbose_name='Подписчик',
        help_text='Пользователь, который подписывается'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='Пользователь',
        help_text='Пользователь на которого подписываются'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'), name='unique_subscription'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name='Теги',
        help_text='Тег рецепта'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        help_text='Рецепт'
    )

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredient',
        help_text='Ингредиент в рецепте'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe', help_text='Рецепт'
    )
    amount = models.PositiveIntegerField(
        null=True, verbose_name='Количество ингредиента',
        help_text='Количество ингредиента в рецепте',
        validators=[MinValueValidator(settings.INGREDIENT_MIN_VALUE)]
    )

    class Meta:
        verbose_name = 'Количетсво ингредиента в рецепте'
        verbose_name_plural = verbose_name


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Избранный рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite',
        help_text='Пользователь, который добавил рецепт в избранное'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user} added {self.recipe}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт в списке покупок'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        help_text='Пользователь, который добавил рецепт в список покупок'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user} added {self.recipe}'
