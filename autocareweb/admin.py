from django.contrib import admin

# Register your models here.
# admin.py

from .models import CustomUser, UserDetails, ServiceCategory, ServiceType
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )

from .models import Slot

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('slotname', 'mechanic', 'status')
    list_filter = ('status',)
    actions = ['make_free']

    @admin.action(description="Mark selected slots as Free")
    def make_free(self, request, queryset):
        queryset.update(status='free')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserDetails)
admin.site.register(ServiceCategory)
admin.site.register(ServiceType)

