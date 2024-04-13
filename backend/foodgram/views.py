from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.filters import IngredientFilter, RecipeFilter
from foodgram.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                             ShoppingCart, Tag)
from foodgram.serializers import (CreateRecipeSerializer, IngredientSerializer,
                                  ShowRecipeSerializer, TagSerializer)
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.pagination import LimitPageNumberPagination
from backend.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        method = self.request.method
        if method == 'POST' or method == 'PATCH':
            return CreateRecipeSerializer
        return ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_permissions(self):
        if self.action in ('update', 'destroy'):
            permission_classes = (IsAuthorOrReadOnly,)
        else:
            permission_classes = (IsAuthenticatedOrReadOnly,)
        return [permission() for permission in permission_classes]


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class ShoppingCartAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт уже в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ShoppingCart.objects.create(user=user, recipe=recipe)

        serializer = ShowRecipeSerializer(recipe, context={
            'request': request,
            'hide_fields': [
                'tags', 'author', 'ingredients',
                'is_favorited', 'is_in_shopping_cart', 'text'
            ]
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_cart_item = get_object_or_404(
            ShoppingCart, user=user, recipe=recipe
        )

        shopping_cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        ingredients = IngredientRecipe.objects.filter(
            recipe__in=shopping_cart_items.values('recipe')
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )

        shopping_list = []
        for ingredient in ingredients:
            line = (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) — "
                f"{ingredient['total_amount']}"
            )
            shopping_list.append(line)

        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type=settings.SHOPPING_CART_CONTENT_TYPE
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{settings.SHOPPING_CART_FILENAME}"'
        )
        return response


class FavoriteApiView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Favorite.objects.create(user=user, recipe=recipe)

        serializer = ShowRecipeSerializer(recipe, context={
            'request': request,
            'hide_fields': [
                'tags', 'author', 'ingredients',
                'is_favorited', 'is_in_shopping_cart', 'text'
            ]
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_cart_item = get_object_or_404(
            Favorite, user=user, recipe=recipe
        )

        shopping_cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
