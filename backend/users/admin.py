from django.contrib import admin
from foodgram.models import Follow, User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_active', 'is_staff', 'is_superuser'
    )
    list_filter = ('first_name', 'last_name', 'username', 'email',)


admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow)
