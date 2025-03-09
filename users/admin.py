from django.contrib import admin
from django.contrib.auth import get_user_model


# from .models import User
User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ["user_permissions", "groups"]
    readonly_fields = [
        "password",
        "last_login",
        "is_superuser",
        "email",
    ]
