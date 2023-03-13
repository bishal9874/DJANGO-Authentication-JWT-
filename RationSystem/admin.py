from django.contrib import admin
from RationSystem.models import RationUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

class UserModelAdmin(BaseUserAdmin):
    def image_tag(self, obj):
        return format_html('<img src="{}" style="width: 120px; height:110px;">'.format(obj.face_image.url))

    list_display = ('id', 'email', 'rationId', 'name', 'tc', 'is_admin', 'image_tag')
    list_filter = ('is_admin',)
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'rationId', 'face_image', 'password')}),
        ('Personal info', {'fields': ('name', 'tc',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'rationId', 'name', 'tc', 'face_image', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('email', 'rationId')
    ordering = ('email', 'id')
    filter_horizontal = ()


admin.site.register(RationUser, UserModelAdmin)
