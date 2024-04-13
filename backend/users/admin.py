from django.contrib import admin
from foodgram.models import Follow, User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_active', 'is_staff', 'is_superuser'
    )
    list_filter = ('first_name', 'last_name', 'username', 'email',)
    search_fields = ('username', 'email', 'first_name', 'last_name')


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'following'
    )
    list_filter = (
        'user', 'following'
    )
    search_fields = (
        'user', 'following'
    )


admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
