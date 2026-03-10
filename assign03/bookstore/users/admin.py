from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Role, UserRole

# Unregister Group as it might not be needed if using custom Roles
admin.site.unregister(Group)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
