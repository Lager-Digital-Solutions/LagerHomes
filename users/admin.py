from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', "first_name", 'username', 'role', 'userID']  # Include 'role' in the display
    list_display_links = ('username', "first_name", 'email')
    list_filter = ('role',)  # Add a filter for the 'role' field in the admin panel
    search_fields = ('email', 'username', 'userID')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password',)}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Roles and Permissions', {'fields': ('role', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role",),  # Include 'role' in the add form
            },
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
