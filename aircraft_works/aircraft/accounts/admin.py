from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from aircraft.accounts.models import  User, Team



@register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = [
        "id",
        "email",
        "team",
        "first_name",
        "last_name",
    ]
    list_filter = ["is_active", "is_admin", "is_deleted", "team"]
    search_fields = ["email", "first_name", "last_name"]
    ordering= ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Team Info",
            {"fields": ("team",)},  # Burada 'team' alanını ekliyoruz
        ),
        (
            "Status Info",
            {"fields": ("is_active","is_deleted")},  # Burada 'team' alanını ekliyoruz
        ),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Team Info",
            {"fields": ("team",)},  # Burada 'team' alanını ekliyoruz
        ),
    )

@register(Team)
class TeamAdmin(ModelAdmin):
    list_display = ["id", "team_type"]
    list_filter = ["team_type"]
    search_fields = ["team_type"]
    ordering = ["-id"]
    readonly_fields = ["created_at", "updated_at"]
