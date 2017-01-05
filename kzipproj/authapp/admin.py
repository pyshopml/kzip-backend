from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import ExtUser


@admin.register(ExtUser)
class ExtUserAdmin(UserAdmin):
    list_display = [
        'id',
        'email',
        'name',
        'date_joined',
        'last_login',
    ]

    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'name',
            )}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'is_superuser',)}),

    )

    add_fieldsets = (
        (None, {
            'fields': (
                'email',
                'password1',
                'password2',
            )}
         ),
    )

    list_display_links = [
        'id',
        'email',
    ]

    search_fields = ('email',)
    ordering = ('id', 'name')


admin.site.unregister(Group)
