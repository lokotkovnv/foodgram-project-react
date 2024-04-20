from django.conf import settings
from django.contrib import admin
from django.db.models import Count
from foodgram.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                             ShoppingCart, Tag, TagRecipe)


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = settings.ADMIN_EXTRA_FIELDS
    min_num = settings.ADMIN_MIN_NUM_FIELDS


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = settings.ADMIN_EXTRA_FIELDS
    min_num = settings.ADMIN_MIN_NUM_FIELDS


class TagsFilter(admin.SimpleListFilter):
    title = 'Tags'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        tags = Tag.objects.annotate(
            recipe_count=Count('recipes')
        ).filter(recipe_count__gt=0)
        return [(tag.id, tag.name) for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__id=self.value())


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'get_author_email', 'name',
        'get_tags_display', 'get_favorite_count',
    )
    list_filter = ('tags',)
    search_fields = ('author__username', 'author__email', 'name',)
    inlines = (TagRecipeInline, IngredientRecipeInline)

    def get_tags_display(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def get_author_email(self, obj):
        return obj.author.email

    get_tags_display.short_description = 'Теги'
    get_favorite_count.short_description = 'Добавлений в избранное'
    get_author_email.short_description = 'Email'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    list_filter = ('name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'get_recipe_name', 'get_username', 'get_email', 'get_recipe_tags',
    )
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name', 'user__username', 'user__email',)

    def get_recipe_name(self, obj):
        return obj.recipe.name

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def get_recipe_tags(self, obj):
        return ', '.join(tag.name for tag in obj.recipe.tags.all())

    get_recipe_name.short_description = 'Рецепт'
    get_username.short_description = 'Пользователь'
    get_email.short_description = 'Email'
    get_recipe_tags.short_description = 'Теги'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'get_recipe_name', 'get_username', 'get_email', 'get_recipe_tags'
    )
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name', 'user__username', 'user__email')

    def get_recipe_tags(self, obj):
        return ', '.join(tag.name for tag in obj.recipe.tags.all())

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def get_recipe_name(self, obj):
        return obj.recipe.name

    get_recipe_name.short_description = 'Рецепт'
    get_username.short_description = 'Пользователь'
    get_email.short_description = 'Email'
    get_recipe_tags.short_description = 'Теги'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
