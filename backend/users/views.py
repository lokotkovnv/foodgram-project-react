from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from users.serializers import UserListSerializer
from users.serializers import FollowSerializer
from users.serializers import CustomUserSerializer, BasicUserSerializer
from foodgram.models import Follow, Recipe
from backend.pagination import LimitPageNumberPagination
from foodgram.serializers import (UserRecipeSerializer,
                                  SubscriptionUserSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            user = request.user
            serializer = BasicUserSerializer(
                user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BasicUserSerializer(
            instance, context={'request': request}
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = UserListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
            detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        serializer = FollowSerializer(data={'user': user, 'following': author})
        if serializer.is_valid():
            serializer.save()

            recipes_limit = int(request.query_params.get('recipes_limit', 0))
            recipes_queryset = Recipe.objects.filter(
                author=author
            )[:recipes_limit] if recipes_limit > 0 else Recipe.objects.filter(
                author=author
            )
            recipes_data = UserRecipeSerializer(
                recipes_queryset, many=True
            ).data

            user_data = CustomUserSerializer(
                author, context={'request': request}
            ).data
            user_data['recipes'] = recipes_data
            user_data['recipes_count'] = len(recipes_data)
            user_data['is_subscribed'] = True

            return Response(user_data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        try:
            follow = Follow.objects.get(user=user, following=author)
        except Follow.DoesNotExist:
            return Response(
                {'error': 'Подписка не найдена или уже была удалена.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user).select_related('following')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        recipes_limit = request.query_params.get('recipes_limit')
        context = {
            'request': request,
            'use_custom_user_serializer': True,
            'hide_fields': [
                'author', 'is_favorited',
                'is_in_shopping_cart', 'tags',
                'ingredients', 'text'
            ],
            'recipes_limit': recipes_limit
        }
        serializer = SubscriptionUserSerializer(
            [follow.following for follow in page],
            many=True,
            context=context
        )
        return paginator.get_paginated_response(serializer.data)


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return self.request.user.subscriptions.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
