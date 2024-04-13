import base64

import webcolors
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from foodgram.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                             Recipe, ShoppingCart, Tag, TagRecipe)
from rest_framework import serializers
from users.serializers import BasicUserSerializer, CustomUserSerializer

User = get_user_model()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            return webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = serializers.SerializerMethodField('get_author')
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        hide_fields = self.context.get('hide_fields', [])

        for field in hide_fields:
            representation.pop(field, None)

        return representation

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_author(self, obj):
        if self.context.get('use_custom_user_serializer'):
            return CustomUserSerializer(obj.author, context=self.context).data
        else:
            return BasicUserSerializer(obj.author, context=self.context).data

    def get_ingredients(self, obj):
        ingredients_data = IngredientRecipe.objects.filter(recipe=obj)
        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = {
                'id': ingredient_data.ingredient.id,
                'name': ingredient_data.ingredient.name,
                'measurement_unit': (
                    ingredient_data.ingredient.measurement_unit
                ),
                'amount': ingredient_data.amount
            }
            ingredients.append(ingredient)
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(
            recipe=obj, user=user
        ).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(
        many=True, queryset=Tag.objects.all(), slug_field='id'
    )
    ingredients = AddIngredientToRecipeSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredient_ids = [ingredient['id'] for ingredient in value]
        ingredient_amounts = [ingredient['amount'] for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        if ingredient_amounts and min(
            ingredient_amounts
        ) < settings.INGREDIENT_MIN_VALUE:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть не меньше 1'
            )
        return value

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Тэги не должны повторяться')
        return value

    def validate_cooking_time(self, value):
        if value < settings.RECIPE_MIN_COOKING_TIME:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше 1'
            )
        if value > settings.RECIPE_MAX_COOKING_TIME:
            raise serializers.ValidationError(
                'Время готовки должно быть не больше 360'
            )
        return value

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')

        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы 1 ингредиент'
            )
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы 1 тэг'
            )

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context.get('request').user

        with transaction.atomic():
            recipe = Recipe.objects.create(author=author, **validated_data)
            for ingredient in ingredients_data:
                ingredient_model = ingredient['id']
                amount = ingredient['amount']
                IngredientRecipe.objects.create(
                    ingredient=ingredient_model, recipe=recipe, amount=amount
                )
            recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        with transaction.atomic():
            TagRecipe.objects.filter(recipe=instance).delete()
            IngredientRecipe.objects.filter(recipe=instance).delete()
            for ingredient in ingredients_data:
                ingredient_model = ingredient['id']
                amount = ingredient['amount']
                IngredientRecipe.objects.create(
                    ingredient=ingredient_model, recipe=instance, amount=amount
                )

            instance.name = validated_data.pop('name')
            instance.text = validated_data.pop('text')
            if validated_data.get('image') is not None:
                instance.image = validated_data.pop('image')
            instance.cooking_time = validated_data.pop('cooking_time')
            instance.tags.set(tags_data)
            instance.save()

        return instance


class UserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, following=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes_limit = (
            int(recipes_limit) if recipes_limit and recipes_limit.isdigit()
            else None
        )

        if recipes_limit:
            recipes_queryset = obj.recipes.all()[:recipes_limit]
        else:
            recipes_queryset = obj.recipes.all()

        return UserRecipeSerializer(
            recipes_queryset, many=True, context=self.context
        ).data

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes_count', 'recipes'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')
