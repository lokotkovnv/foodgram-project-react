from django.contrib import admin
from foodgram.models import Ingredient, Recipe, Tag

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
