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
        'get_user_username', 'get_user_email',
        'get_following_username', 'get_following_email',
    )
    search_fields = (
        'user__username', 'user__email',
        'following__username', 'following__email',
    )

    def get_user_username(self, obj):
        return obj.user.username

    def get_user_email(self, obj):
        return obj.user.email

    def get_following_username(self, obj):
        return obj.following.username

    def get_following_email(self, obj):
        return obj.following.email

    get_user_username.short_description = 'Подписчик'
    get_user_email.short_description = 'Email подписчика'
    get_following_username.short_description = 'Подписан на'
    get_following_email.short_description = 'Email'


admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
