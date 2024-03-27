from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/', include('djoser.urls')),
]
