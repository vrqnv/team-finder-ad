from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'name', 'surname', 'phone', 'is_active', 'is_staff'
    )
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'name', 'surname')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Personal info',
            {
                'fields': (
                    'name', 'surname', 'avatar', 'phone', 'github_url', 'about'
                )
            }
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active', 'is_staff', 'is_superuser', 'groups',
                    'user_permissions'
                )
            }
        ),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'phone', 'password1', 'password2'
            ),
        }),
    )

    ordering = ('email',)
