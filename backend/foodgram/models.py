from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента', max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200)

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
    )
    tags = models.ManyToManyField(
        Tag, through='TagRecipe', related_name='recipes'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        blank=True,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Время публикации',
    )
    image = models.ImageField()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers'
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
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredient'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe'
    )
    amount = models.PositiveIntegerField(
        null=True, verbose_name='Количество ингредиента'
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
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite',
    )
    when_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-when_added',)
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
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )
    when_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-when_added',)
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user} added {self.recipe}'
