# Generated by Django 5.0.8 on 2025-02-02 08:38

import aircraft.accounts.managers
import aircraft.core.fields
import aircraft.core.helpers
import aircraft.core.mixins
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    aircraft.core.fields.AircraftPrimaryKeyField(
                        default=aircraft.core.helpers.generate_unique_id,
                        editable=False,
                        max_length=64,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created Date"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Date"),
                ),
                (
                    "team_type",
                    models.CharField(
                        choices=[
                            ("WING", "Kanat Takımı"),
                            ("FUSELAGE", "Gövde Takımı"),
                            ("TAIL", "Kuyruk Takımı"),
                            ("AVIONICS", "Aviyonik Takımı"),
                            ("ASSEMBLY", "Montaj Takımı"),
                        ],
                        default="WING",
                        max_length=20,
                        verbose_name="Team Type",
                    ),
                ),
            ],
            options={
                "verbose_name": "Team",
                "verbose_name_plural": "Teams",
            },
            bases=(aircraft.core.mixins.AdminUtilsMixin, models.Model),
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "id",
                    aircraft.core.fields.AircraftPrimaryKeyField(
                        default=aircraft.core.helpers.generate_unique_id,
                        editable=False,
                        max_length=64,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created Date"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Date"),
                ),
                (
                    "email",
                    models.EmailField(
                        db_index=True, max_length=254, unique=True, verbose_name="Email"
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="password"
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="First Name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Last Name"
                    ),
                ),
                (
                    "last_seen",
                    models.DateTimeField(null=True, verbose_name="Last Seen"),
                ),
                (
                    "is_admin",
                    models.BooleanField(default=False, verbose_name="Is Admin?"),
                ),
                (
                    "is_staff",
                    models.BooleanField(default=True, verbose_name="Is Staff?"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is Active?"),
                ),
                (
                    "is_deleted",
                    models.BooleanField(default=False, verbose_name="Is Deleted?"),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True, related_name="custom_user_groups", to="auth.group"
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="custom_user_permissions",
                        to="auth.permission",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.team",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
            },
            bases=(aircraft.core.mixins.AdminUtilsMixin, models.Model),
            managers=[
                ("objects", aircraft.accounts.managers.UserManager()),
            ],
        ),
    ]
