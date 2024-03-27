from django.urls import include, path
from foodgram.views import (DownloadShoppingCartView, FavoriteApiView,
                            IngredientViewSet, RecipeViewSet,
                            ShoppingCartAPIView, TagViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartAPIView.as_view()),
    path('recipes/<int:recipe_id>/favorite/', FavoriteApiView.as_view()),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCartView.as_view()),
    path('', include(router.urls)),
]
