from django.contrib import admin
from django.db.models import Count
from foodgram.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


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
        'author', 'get_tags_display', 'name', 'get_favorite_count',
    )
    list_filter = ('author', 'tags', 'name',)
    search_fields = ('author', 'name',)

    def get_tags_display(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    get_tags_display.short_description = 'Тэги'
    get_favorite_count.short_description = 'Добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name', 'measurement_unit',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    list_filter = ('name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('recipe', 'user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    list_filter = ('recipe', 'user',)
    search_fields = ('recipe', 'user',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
