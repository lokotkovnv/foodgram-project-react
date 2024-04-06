from django.contrib import admin
from foodgram.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagsFilter(admin.SimpleListFilter):
    title = 'Tags'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        tags = set()
        for recipe in Recipe.objects.all():
            for tag in recipe.tags.all():
                tags.add((tag.id, tag.name))
        return sorted(tags, key=lambda x: x[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__id=self.value())


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'get_tags_display', 'name', 'get_favorite_count',
    )
    list_filter = ('author', 'tags', 'name',)

    def get_tags_display(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    def get_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    get_tags_display.short_description = 'Тэги'
    get_favorite_count.short_description = 'Добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name', 'measurement_unit',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
