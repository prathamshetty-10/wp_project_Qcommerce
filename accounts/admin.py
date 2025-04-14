# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, UserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'phone_number', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'address')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'address', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)