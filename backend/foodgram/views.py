from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated


from foodgram.models import (
    Recipe, Tag, Ingredient, ShoppingCart, Favorite, IngredientRecipe
)
from foodgram.serializers import (
    TagSerializer, CreateRecipeSerializer,
    ShowRecipeSerializer, IngredientSerializer
)
from backend.pagination import LimitPageNumberPagination
from foodgram.filters import IngredientFilter, RecipeFilter
from backend.permissions import IsAdminOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permissions = (IsAuthenticatedOrReadOnly,)
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied(
                'You do not have permission to update this recipe.'
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': ('You do not have permission to delete '
                            'this recipe.')},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        try:
            shopping_cart_item = ShoppingCart.objects.get(
                user=user, recipe=recipe
            )
        except ShoppingCart.DoesNotExist:
            return Response(
                {'error': 'Рецепт не найден или уже был удален из корзины.'},
                status=status.HTTP_400_BAD_REQUEST
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
            '\n'.join(shopping_list), content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class FavoriteApiView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_id):
        user = request.user
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        try:
            shopping_cart_item = Favorite.objects.get(user=user, recipe=recipe)
        except Favorite.DoesNotExist:
            return Response(
                {'error': 'Рецепт не найден или уже был удален из избранных.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
