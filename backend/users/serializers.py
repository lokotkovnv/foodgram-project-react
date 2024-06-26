import re

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram.models import Follow
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

INCORRECT_USERNAME_ERROR = (
    'Username должен содержать только буквы, цифры и символы: @ . + - _'
)

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=(UniqueValidator(queryset=User.objects.all()),))
    username = serializers.CharField(
        max_length=150,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(INCORRECT_USERNAME_ERROR)
        return value

    class Meta:
        model = User
        fields = (
            'email', 'id', 'password', 'username', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, following=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes_count'
        )


class FollowListSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=True
    )

    class Meta:
        model = Follow
        fields = ('following',)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class BasicUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, following=obj).exists()
        return False
